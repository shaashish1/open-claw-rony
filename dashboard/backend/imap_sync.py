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
from email.header import decode_header
from email.utils import parsedate_to_datetime, parseaddr

from config import ACCOUNTS, TAG_RULES
import database as db

logger = logging.getLogger("imap_sync")

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

def auto_tag(subject: str, from_addr: str, body_text: str) -> list[str]:
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

def extract_body(msg) -> tuple[str, str]:
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


# ── Per-account sync ──────────────────────────────────────────────────────────

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

        now = int(time.time())

        for uid_bytes in reversed(uid_list):
            uid = uid_bytes.decode()
            try:
                status, msg_data = imap.uid("FETCH", uid, "(RFC822 FLAGS)")
                if status != "OK" or not msg_data or msg_data[0] is None:
                    continue

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
                result["synced"] += 1

            except Exception as e:
                logger.warning(f"Error processing uid {uid} for {email_addr}: {e}")
                continue

    except Exception as e:
        result["errors"].append(f"Sync error: {e}")
    finally:
        try:
            imap.logout()
        except Exception:
            pass

    return result


# ── Full sync ─────────────────────────────────────────────────────────────────

def sync_all_accounts() -> list[dict]:
    results = []
    for account_cfg in ACCOUNTS:
        logger.info(f"Syncing {account_cfg['email']}...")
        result = sync_account(account_cfg)
        results.append(result)
        logger.info(f"  → {result['synced']} emails, errors: {result['errors']}")
    return results
