from __future__ import annotations
"""
ITGYANI Dashboard — IMAP sync engine
"""
import imaplib
import ssl
import email
import smtplib
import time
import re
import logging
import threading
import queue
import os
from typing import Dict, List, Optional
from email.header import decode_header
from email.utils import parsedate_to_datetime, parseaddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import ACCOUNTS, TAG_RULES, SMTP_CONFIG
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

# ── IMAP Delete (move to Trash) ─────────────────────────────────────────────────────

def delete_email(account_cfg: dict, uid: str) -> bool:
    """
    Move email to Trash on the IMAP server.
    - Gmail: copies to [Gmail]/Trash then marks \\Deleted + expunges from INBOX.
    - VPS / other: tries Trash then Deleted Items.
    Returns True on success.
    """
    email_addr = account_cfg["email"]
    host = account_cfg["imap_host"]
    port = account_cfg["imap_port"]
    password = account_cfg["password"]
    ssl_verify = account_cfg["ssl_verify"]

    if not password:
        logger.warning(f"delete_email: no password for {email_addr}")
        return False

    ctx = make_ssl_context(ssl_verify)
    try:
        imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
        imap.login(email_addr, password)

        # Select INBOX (write mode)
        status, _ = imap.select("INBOX")
        if status != "OK":
            logger.error(f"delete_email: cannot SELECT INBOX for {email_addr}")
            imap.logout()
            return False

        is_gmail = "gmail" in host.lower()
        if is_gmail:
            trash_folder = "[Gmail]/Trash"
        else:
            # Try common trash folder names
            trash_folder = None
            for candidate in ["Trash", "INBOX.Trash", "Deleted Items", "Deleted Messages"]:
                typ, lst = imap.list('""', f'"{candidate}"')
                if typ == "OK" and lst and lst[0]:
                    trash_folder = candidate
                    break
            if not trash_folder:
                trash_folder = "Trash"  # fallback, server will create

        # Copy to trash
        result = imap.uid("COPY", uid, trash_folder)
        if result[0] != "OK":
            logger.error(f"delete_email: COPY to {trash_folder} failed for uid {uid} ({email_addr}): {result}")
            imap.logout()
            return False

        # Mark as deleted in INBOX and expunge
        imap.uid("STORE", uid, "+FLAGS", "(\\Deleted)")
        imap.expunge()

        imap.logout()
        logger.info(f"delete_email: uid {uid} moved to {trash_folder} for {email_addr}")
        return True

    except Exception as e:
        logger.error(f"delete_email error for {email_addr} uid {uid}: {e}")
        try:
            imap.logout()
        except Exception:
            pass
        return False


def restore_email(account_cfg: dict, uid: str) -> bool:
    """
    Move email from Trash back to INBOX.
    Returns True on success.
    """
    email_addr = account_cfg["email"]
    host = account_cfg["imap_host"]
    port = account_cfg["imap_port"]
    password = account_cfg["password"]
    ssl_verify = account_cfg["ssl_verify"]

    if not password:
        return False

    is_gmail = "gmail" in host.lower()
    trash_folder = "[Gmail]/Trash" if is_gmail else "Trash"

    ctx = make_ssl_context(ssl_verify)
    try:
        imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
        imap.login(email_addr, password)

        status, _ = imap.select(trash_folder)
        if status != "OK":
            logger.error(f"restore_email: cannot select {trash_folder} for {email_addr}")
            imap.logout()
            return False

        # Copy back to INBOX
        result = imap.uid("COPY", uid, "INBOX")
        if result[0] != "OK":
            logger.error(f"restore_email: COPY to INBOX failed for uid {uid}: {result}")
            imap.logout()
            return False

        # Delete from trash
        imap.uid("STORE", uid, "+FLAGS", "(\\Deleted)")
        imap.expunge()

        imap.logout()
        logger.info(f"restore_email: uid {uid} restored to INBOX for {email_addr}")
        return True

    except Exception as e:
        logger.error(f"restore_email error for {email_addr} uid {uid}: {e}")
        try:
            imap.logout()
        except Exception:
            pass
        return False


# ── SMTP Reply ───────────────────────────────────────────────────────────────────

def send_reply(account_cfg: dict, original_uid: str, reply_text: str) -> bool:
    """
    Fetch the original email by UID, build a proper reply with In-Reply-To /
    References headers, and send it via SMTP.
    Logs the sent email to the database.
    Returns True on success.
    """
    email_addr = account_cfg["email"]
    host = account_cfg["imap_host"]
    port = account_cfg["imap_port"]
    password = account_cfg["password"]
    ssl_verify = account_cfg["ssl_verify"]

    if not password:
        logger.warning(f"send_reply: no password for {email_addr}")
        return False

    # — Step 1: Fetch original email via IMAP —
    ctx = make_ssl_context(ssl_verify)
    orig_msg = None
    try:
        imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
        imap.login(email_addr, password)
        imap.select("INBOX", readonly=True)
        status, msg_data = imap.uid("FETCH", original_uid, "(RFC822)")
        if status == "OK" and msg_data and msg_data[0]:
            raw = msg_data[0][1]
            orig_msg = email.message_from_bytes(raw)
        imap.logout()
    except Exception as e:
        logger.error(f"send_reply: IMAP fetch failed for {email_addr} uid {original_uid}: {e}")
        return False

    if orig_msg is None:
        logger.error(f"send_reply: could not fetch original uid {original_uid} for {email_addr}")
        return False

    # — Step 2: Build reply headers —
    orig_from = orig_msg.get("From", "")
    orig_subject = decode_mime_words(orig_msg.get("Subject", ""))
    orig_message_id = orig_msg.get("Message-ID", "")
    orig_references = orig_msg.get("References", "")

    reply_to = orig_from  # reply goes to the original sender
    reply_subject = orig_subject if orig_subject.lower().startswith("re:") else f"Re: {orig_subject}"

    # Build References chain
    refs = orig_references.strip()
    if orig_message_id:
        refs = (refs + " " + orig_message_id).strip() if refs else orig_message_id

    # — Step 3: Build MIME message —
    msg = MIMEMultipart("alternative")
    msg["From"] = email_addr
    msg["To"] = reply_to
    msg["Subject"] = reply_subject
    if orig_message_id:
        msg["In-Reply-To"] = orig_message_id
    if refs:
        msg["References"] = refs

    msg.attach(MIMEText(reply_text, "plain", "utf-8"))

    # — Step 4: Get SMTP config —
    smtp_cfg = SMTP_CONFIG.get(host, SMTP_CONFIG.get("194.233.64.74"))
    smtp_host = smtp_cfg["smtp_host"]
    smtp_port = smtp_cfg["smtp_port"]

    # — Step 5: Send via SMTP —
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(email_addr, password)
            server.sendmail(email_addr, [reply_to], msg.as_string())
        logger.info(f"send_reply: sent reply from {email_addr} to {reply_to} re uid {original_uid}")
    except Exception as e:
        logger.error(f"send_reply: SMTP send failed for {email_addr}: {e}")
        return False

    # — Step 6: Log to DB —
    try:
        db.log_sent_email(
            account=email_addr,
            in_reply_to_uid=original_uid,
            to_addr=reply_to,
            subject=reply_subject,
            body_text=reply_text,
            sent_at=int(time.time()),
        )
    except Exception as e:
        logger.warning(f"send_reply: could not log to DB: {e}")

    return True


# ── Quick sync (last N emails) ───────────────────────────────────────────────────────

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
