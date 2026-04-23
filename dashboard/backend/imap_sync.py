from __future__ import annotations
"""
ITGYANI Dashboard — IMAP sync engine
RULE: DRAFT ONLY - Never call SMTP send
"""
import imaplib
import ssl
import email
import time
import re
import logging
import threading
import queue
from typing import Dict, List, Optional
from email.header import decode_header
from email.utils import parsedate_to_datetime, parseaddr

from config import ACCOUNTS, TAG_RULES
import database as db

logger = logging.getLogger("imap_sync")

# ── Thread-safe queue for new-mail events ─────────────────────────────────
new_mail_queue: queue.Queue = queue.Queue()

# ── SSL contexts ──────────────────────────────────────────────────────────────

def make_ssl_context(verify: bool) -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    if not verify:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


# ── Header decoding ───────────────────────────────────────────────────────────

def decode_mime_words(s: str) -> str:
    if not s:
        return ""
    parts = decode_header(s)
    result = []
    for text, charset in parts:
        if isinstance(text, bytes):
            try:
                result.append(text.decode(charset or "utf-8", errors="replace"))
            except Exception:
                result.append(text.decode("utf-8", errors="replace"))
        else:
            result.append(text)
    return "".join(result)


# ── Auto-tagger ───────────────────────────────────────────────────────────────

def auto_tag(subject: str, from_addr: str, body_text: str) -> List[str]:
    tags = []
    haystack = f"{subject} {from_addr}".lower()
    body_lower = (body_text or "").lower()

    for tag, keywords in TAG_RULES.items():
        if tag == "payment":
            if any(kw in subject.lower() for kw in keywords):
                tags.append(tag)
        else:
            if any(kw in haystack for kw in keywords):
                tags.append(tag)

    # Spam detection
    spam_signals = [
        "unsubscribe" in body_lower,
        "newsletter" in body_lower,
        bool(re.match(r"no[-_.]?reply@", from_addr.lower())),
        "noreply@" in from_addr.lower(),
    ]
    if any(spam_signals):
        tags.append("spam")

    return list(set(tags))


# ── Email body extraction ─────────────────────────────────────────────────────

def extract_body(msg) -> tuple:
    """Returns (html_body, text_body)"""
    html_body = ""
    text_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition", ""))
            if "attachment" in disp:
                continue
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            charset = part.get_content_charset() or "utf-8"
            try:
                decoded = payload.decode(charset, errors="replace")
            except Exception:
                decoded = payload.decode("utf-8", errors="replace")

            if ctype == "text/html" and not html_body:
                html_body = decoded
            elif ctype == "text/plain" and not text_body:
                text_body = decoded
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                decoded = payload.decode(charset, errors="replace")
            except Exception:
                decoded = payload.decode("utf-8", errors="replace")
            ctype = msg.get_content_type()
            if ctype == "text/html":
                html_body = decoded
            else:
                text_body = decoded

    return html_body, text_body


# ── Fetch and store a single UID ──────────────────────────────────────────────

def _fetch_and_store(imap: imaplib.IMAP4_SSL, uid: str, email_addr: str) -> bool:
    """Fetch one message by UID and upsert into DB. Returns True on success."""
    now = int(time.time())
    try:
        status, msg_data = imap.uid("FETCH", uid, "(RFC822 FLAGS)")
        if status != "OK" or not msg_data or msg_data[0] is None:
            return False

        raw = msg_data[0][1]
        flags = msg_data[0][0].decode() if msg_data[0][0] else ""
        is_read = 1 if "\\Seen" in flags else 0

        msg = email.message_from_bytes(raw)
        subject = decode_mime_words(msg.get("Subject", "(no subject)"))
        from_raw = msg.get("From", "")
        from_addr = decode_mime_words(from_raw)
        to_addr = decode_mime_words(msg.get("To", ""))
        date_str = msg.get("Date", "")

        try:
            date_ts = int(parsedate_to_datetime(date_str).timestamp())
        except Exception:
            date_ts = now

        html_body, text_body = extract_body(msg)
        snippet = (text_body or "").strip()[:200].replace("\n", " ")
        tags = auto_tag(subject, from_addr, text_body)

        db.upsert_email(
            account=email_addr,
            folder="INBOX",
            uid=uid,
            from_addr=from_addr,
            to_addr=to_addr,
            subject=subject,
            date_str=date_str,
            date_ts=date_ts,
            snippet=snippet,
            body_html=html_body,
            body_text=text_body,
            is_read=is_read,
            tags=tags,
            synced_at=now,
        )
        return True
    except Exception as e:
        logger.warning(f"Error fetching uid {uid} for {email_addr}: {e}")
        return False


# ── Quick sync (last N emails) ────────────────────────────────────────────────

def sync_account_quick(account_cfg: dict, limit: int = 50) -> dict:
    """
    Fast sync: fetch only the last `limit` emails by UID.
    Used on startup and page load for rapid DB population.
    """
    email_addr = account_cfg["email"]
    host = account_cfg["imap_host"]
    port = account_cfg["imap_port"]
    password = account_cfg["password"]
    ssl_verify = account_cfg["ssl_verify"]

    result = {"account": email_addr, "synced": 0, "errors": []}

    if not password:
        result["errors"].append("No password configured")
        return result

    ctx = make_ssl_context(ssl_verify)

    try:
        imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
    except Exception as e:
        result["errors"].append(f"Connection failed: {e}")
        return result

    try:
        imap.login(email_addr, password)
    except Exception as e:
        result["errors"].append(f"Login failed: {e}")
        try:
            imap.logout()
        except Exception:
            pass
        return result

    try:
        status, data = imap.select("INBOX", readonly=True)
        if status != "OK":
            result["errors"].append("Cannot select INBOX")
            return result

        status, uids = imap.uid("SEARCH", None, "ALL")
        if status != "OK":
            result["errors"].append("SEARCH failed")
            return result

        uid_list = uids[0].split()
        # Take only the last `limit` UIDs (newest)
        uid_list = uid_list[-limit:]

        for uid_bytes in reversed(uid_list):
            uid = uid_bytes.decode()
            if _fetch_and_store(imap, uid, email_addr):
                result["synced"] += 1

    except Exception as e:
        result["errors"].append(f"Quick sync error: {e}")
    finally:
        try:
            imap.logout()
        except Exception:
            pass

    logger.info(f"Quick sync {email_addr}: {result['synced']} emails, errors: {result['errors']}")
    return result


# ── Per-account full sync ─────────────────────────────────────────────────────

def sync_account(account_cfg: dict, max_emails: int = 100) -> dict:
    email_addr = account_cfg["email"]
    host = account_cfg["imap_host"]
    port = account_cfg["imap_port"]
    password = account_cfg["password"]
    ssl_verify = account_cfg["ssl_verify"]

    result = {"account": email_addr, "synced": 0, "errors": []}

    if not password:
        result["errors"].append("No password configured")
        return result

    ctx = make_ssl_context(ssl_verify)

    try:
        imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
    except Exception as e:
        result["errors"].append(f"Connection failed: {e}")
        return result

    try:
        imap.login(email_addr, password)
    except Exception as e:
        result["errors"].append(f"Login failed: {e}")
        imap.logout()
        return result

    try:
        status, data = imap.select("INBOX", readonly=True)
        if status != "OK":
            result["errors"].append("Cannot select INBOX")
            imap.logout()
            return result

        # Fetch last N emails by UID
        status, uids = imap.uid("SEARCH", None, "ALL")
        if status != "OK":
            result["errors"].append("SEARCH failed")
            imap.logout()
            return result

        uid_list = uids[0].split()
        # Take newest max_emails
        uid_list = uid_list[-max_emails:]

        for uid_bytes in reversed(uid_list):
            uid = uid_bytes.decode()
            if _fetch_and_store(imap, uid, email_addr):
                result["synced"] += 1

    except Exception as e:
        result["errors"].append(f"Sync error: {e}")
    finally:
        try:
            imap.logout()
        except Exception:
            pass

    return result


# ── IMAP IDLE watcher ─────────────────────────────────────────────────────────

class IdleWatcher:
    """
    Persistent IMAP IDLE watcher for a single account.
    Runs as a daemon thread. On new mail (EXISTS response),
    fetches the new message(s) and pushes events to new_mail_queue.
    Reconnects automatically on connection drop.
    """

    RECONNECT_DELAY = 30  # seconds

    def __init__(self, account_cfg: dict) -> None:
        self.account_cfg = account_cfg
        self.email_addr = account_cfg["email"]
        self.host = account_cfg["imap_host"]
        self.port = account_cfg["imap_port"]
        self.password = account_cfg["password"]
        self.ssl_verify = account_cfg["ssl_verify"]
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def _connect(self) -> Optional[imaplib.IMAP4_SSL]:
        if not self.password:
            logger.warning(f"IDLE watcher: no password for {self.email_addr}")
            return None
        ctx = make_ssl_context(self.ssl_verify)
        try:
            imap = imaplib.IMAP4_SSL(self.host, self.port, ssl_context=ctx)
            imap.login(self.email_addr, self.password)
            typ, data = imap.select("INBOX")
            if typ != "OK":
                logger.error(f"IDLE: cannot SELECT INBOX for {self.email_addr}")
                imap.logout()
                return None
            # Record current EXISTS count
            exists_count = int(data[0]) if data and data[0] else 0
            imap._idle_exists = exists_count
            logger.info(f"IDLE watcher connected for {self.email_addr} (EXISTS={exists_count})")
            return imap
        except Exception as e:
            logger.error(f"IDLE connect failed for {self.email_addr}: {e}")
            return None

    def _send_idle(self, imap: imaplib.IMAP4_SSL) -> None:
        """Send IDLE command (raw, since imaplib doesn't support it natively)."""
        imap.send(b"IDLE0001 IDLE\r\n")

    def _send_done(self, imap: imaplib.IMAP4_SSL) -> None:
        """Send DONE to terminate IDLE."""
        try:
            imap.send(b"DONE\r\n")
        except Exception:
            pass

    def _watch_once(self, imap: imaplib.IMAP4_SSL) -> bool:
        """
        Run one IDLE session. Returns True to continue, False to stop.
        """
        try:
            self._send_idle(imap)
            # Set socket timeout — we'll re-send IDLE every 20 minutes
            # (IMAP servers typically cut IDLE at 29 min)
            imap.socket().settimeout(20 * 60)

            while not self._stop_event.is_set():
                try:
                    # Read a line from the server
                    line = imap.readline()
                except Exception:
                    # Timeout or disconnect
                    self._send_done(imap)
                    return False

                if not line:
                    self._send_done(imap)
                    return False

                line_str = line.decode("utf-8", errors="replace").strip()
                logger.debug(f"IDLE [{self.email_addr}]: {line_str}")

                # EXISTS means new mail arrived
                if "EXISTS" in line_str:
                    try:
                        new_count = int(line_str.split()[1])
                    except (IndexError, ValueError):
                        new_count = 0

                    old_count = getattr(imap, "_idle_exists", 0)
                    if new_count > old_count:
                        imap._idle_exists = new_count
                        # Terminate IDLE, fetch new messages, restart IDLE
                        self._send_done(imap)
                        self._fetch_new_messages(imap, old_count, new_count)
                        return True  # reconnect IDLE loop

                # OK continuation (server keepalive)
                elif "OK" in line_str and "Still" in line_str:
                    pass  # normal keepalive

                # Re-send IDLE after timeout
                elif line_str == "":
                    self._send_done(imap)
                    return True  # re-enter IDLE

        except Exception as e:
            logger.error(f"IDLE watch error for {self.email_addr}: {e}")
            return False

        return True

    def _fetch_new_messages(
        self, imap: imaplib.IMAP4_SSL, old_count: int, new_count: int
    ) -> None:
        """Fetch messages from old_count+1 to new_count by sequence number."""
        count = 0
        for seq in range(old_count + 1, new_count + 1):
            try:
                # Convert sequence number to UID
                status, uid_data = imap.fetch(str(seq), "(UID)")
                if status != "OK" or not uid_data or uid_data[0] is None:
                    continue
                uid_match = re.search(rb"UID (\d+)", uid_data[0])
                if not uid_match:
                    continue
                uid = uid_match.group(1).decode()
                if _fetch_and_store(imap, uid, self.email_addr):
                    count += 1
            except Exception as e:
                logger.warning(f"IDLE fetch seq {seq} for {self.email_addr}: {e}")

        if count > 0:
            logger.info(f"IDLE: {count} new email(s) for {self.email_addr}")
            new_mail_queue.put({
                "type": "new_mail",
                "account": self.email_addr,
                "count": count,
            })

    def run(self) -> None:
        """Main loop — connect, IDLE, reconnect on failure."""
        while not self._stop_event.is_set():
            imap = self._connect()
            if imap is None:
                logger.info(f"IDLE: waiting {self.RECONNECT_DELAY}s before retry for {self.email_addr}")
                self._stop_event.wait(self.RECONNECT_DELAY)
                continue

            try:
                # Keep re-entering IDLE until disconnect or stop
                while not self._stop_event.is_set():
                    should_continue = self._watch_once(imap)
                    if not should_continue:
                        break
            finally:
                try:
                    imap.logout()
                except Exception:
                    pass

            if not self._stop_event.is_set():
                logger.info(f"IDLE: reconnecting in {self.RECONNECT_DELAY}s for {self.email_addr}")
                self._stop_event.wait(self.RECONNECT_DELAY)


def start_idle_watcher(account_cfg: dict) -> threading.Thread:
    """Start an IDLE watcher daemon thread for one account."""
    watcher = IdleWatcher(account_cfg)
    t = threading.Thread(
        target=watcher.run,
        name=f"idle-{account_cfg['email']}",
        daemon=True,
    )
    t.start()
    logger.info(f"Started IDLE watcher thread for {account_cfg['email']}")
    return t


# ── Full sync ─────────────────────────────────────────────────────────────────

def sync_all_accounts() -> List[dict]:
    results = []
    for account_cfg in ACCOUNTS:
        logger.info(f"Syncing {account_cfg['email']}...")
        result = sync_account(account_cfg)
        results.append(result)
        logger.info(f"  → {result['synced']} emails, errors: {result['errors']}")
    return results


def quick_sync_all_accounts() -> List[dict]:
    """Quick sync (last 50) for all accounts."""
    results = []
    for account_cfg in ACCOUNTS:
        result = sync_account_quick(account_cfg, limit=50)
        results.append(result)
    return results
