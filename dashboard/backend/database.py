from __future__ import annotations
"""
ITGYANI Dashboard — SQLite database layer
RULE: DRAFT ONLY - Never call SMTP send
"""
import sqlite3
import json
from contextlib import contextmanager
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with db_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                account     TEXT NOT NULL,
                folder      TEXT NOT NULL DEFAULT 'INBOX',
                uid         TEXT NOT NULL,
                from_addr   TEXT,
                to_addr     TEXT,
                subject     TEXT,
                date_str    TEXT,
                date_ts     INTEGER,
                snippet     TEXT,
                body_html   TEXT,
                body_text   TEXT,
                is_read     INTEGER DEFAULT 0,
                tags        TEXT DEFAULT '[]',
                synced_at   INTEGER,
                UNIQUE(account, folder, uid)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                account     TEXT NOT NULL,
                uid         TEXT NOT NULL,
                reply_text  TEXT NOT NULL,
                created_at  INTEGER NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS telegram_sent (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                account     TEXT NOT NULL,
                uid         TEXT NOT NULL,
                tag         TEXT NOT NULL,
                sent_at     INTEGER NOT NULL,
                UNIQUE(account, uid, tag)
            )
        """)

        # Indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_emails_account ON emails(account)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_emails_date ON emails(date_ts)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_emails_tags ON emails(tags)")

        # deleted flag column — add if missing (idempotent migration)
        try:
            cur.execute("ALTER TABLE emails ADD COLUMN deleted INTEGER DEFAULT 0")
        except Exception:
            pass  # column already exists

        cur.execute("CREATE INDEX IF NOT EXISTS idx_emails_deleted ON emails(deleted)")

        # sent_emails log
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sent_emails (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                account         TEXT NOT NULL,
                in_reply_to_uid TEXT,
                to_addr         TEXT,
                subject         TEXT,
                body_text       TEXT,
                sent_at         INTEGER NOT NULL
            )
        """)

        # marketing_contacts
        cur.execute("""
            CREATE TABLE IF NOT EXISTS marketing_contacts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                email           TEXT NOT NULL UNIQUE,
                name            TEXT,
                source_account  TEXT,
                source_domain   TEXT,
                first_seen_ts   INTEGER,
                tags            TEXT DEFAULT '[]',
                unsubscribed    INTEGER DEFAULT 0
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mc_domain ON marketing_contacts(source_domain)")

        # marketing_phones
        cur.execute("""
            CREATE TABLE IF NOT EXISTS marketing_phones (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                phone             TEXT NOT NULL UNIQUE,
                name              TEXT,
                email             TEXT,
                source            TEXT DEFAULT 'manual',
                country_code      TEXT,
                whatsapp_opted_in INTEGER DEFAULT 0,
                added_ts          INTEGER,
                tags              TEXT DEFAULT '[]',
                notes             TEXT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mp_country ON marketing_phones(country_code)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mp_whatsapp ON marketing_phones(whatsapp_opted_in)")


# ── Email CRUD ────────────────────────────────────────────────────────────────

def upsert_email(account, folder, uid, from_addr, to_addr, subject,
                 date_str, date_ts, snippet, body_html, body_text,
                 is_read, tags, synced_at):
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO emails
                (account, folder, uid, from_addr, to_addr, subject, date_str,
                 date_ts, snippet, body_html, body_text, is_read, tags, synced_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(account, folder, uid) DO UPDATE SET
                is_read   = excluded.is_read,
                tags      = excluded.tags,
                synced_at = excluded.synced_at,
                body_html = COALESCE(excluded.body_html, emails.body_html),
                body_text = COALESCE(excluded.body_text, emails.body_text)
        """, (account, folder, uid, from_addr, to_addr, subject, date_str,
              date_ts, snippet, body_html, body_text, is_read,
              json.dumps(tags), synced_at))


def mark_deleted(account: str, uid: str) -> None:
    """Set deleted=1 in DB for a given email (keeps the row for backup)."""
    with db_cursor() as cur:
        cur.execute(
            "UPDATE emails SET deleted = 1 WHERE account = ? AND uid = ?",
            (account, uid),
        )


def mark_restored(account: str, uid: str) -> None:
    """Clear the deleted flag."""
    with db_cursor() as cur:
        cur.execute(
            "UPDATE emails SET deleted = 0 WHERE account = ? AND uid = ?",
            (account, uid),
        )


def log_sent_email(account: str, in_reply_to_uid: str, to_addr: str,
                   subject: str, body_text: str, sent_at: int) -> int:
    """Log a sent email to the sent_emails table."""
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO sent_emails
                (account, in_reply_to_uid, to_addr, subject, body_text, sent_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (account, in_reply_to_uid, to_addr, subject, body_text, sent_at))
        return cur.lastrowid


def get_emails(account=None, folder="INBOX", page=1, limit=50, tag_filter=None,
               include_deleted=False):
    offset = (page - 1) * limit
    conditions = []
    params = []

    if account:
        conditions.append("account = ?")
        params.append(account)
    if folder:
        conditions.append("folder = ?")
        params.append(folder)
    if tag_filter:
        conditions.append("tags LIKE ?")
        params.append(f'%"{tag_filter}"%')
    if include_deleted:
        conditions.append("deleted = 1")
    else:
        conditions.append("(deleted IS NULL OR deleted = 0)")

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params += [limit, offset]

    with db_cursor() as cur:
        cur.execute(f"""
            SELECT id, account, folder, uid, from_addr, to_addr, subject,
                   date_str, date_ts, snippet, is_read, tags
            FROM emails
            {where}
            ORDER BY date_ts DESC
            LIMIT ? OFFSET ?
        """, params)
        rows = cur.fetchall()

    result = []
    for row in rows:
        d = dict(row)
        d["tags"] = json.loads(d["tags"] or "[]")
        result.append(d)
    return result


def get_email_body(account, uid):
    with db_cursor() as cur:
        cur.execute("""
            SELECT body_html, body_text, from_addr, to_addr, subject, date_str, tags
            FROM emails WHERE account = ? AND uid = ?
        """, (account, uid))
        row = cur.fetchone()
    if not row:
        return None
    d = dict(row)
    d["tags"] = json.loads(d["tags"] or "[]")
    return d


def get_unread_count(account):
    with db_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) as cnt FROM emails WHERE account = ? AND is_read = 0",
            (account,)
        )
        row = cur.fetchone()
    return row["cnt"] if row else 0


def get_stats():
    with db_cursor() as cur:
        # Per-account totals + unread
        cur.execute("""
            SELECT account,
                   COUNT(*) as total,
                   SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread
            FROM emails
            GROUP BY account
        """)
        per_account = [dict(r) for r in cur.fetchall()]

        # Today's client/job-lead counts (epoch for today UTC)
        import time
        today_start = int(time.time()) - (int(time.time()) % 86400)
        cur.execute("""
            SELECT COUNT(*) as cnt FROM emails
            WHERE tags LIKE '%"client"%' AND date_ts >= ?
        """, (today_start,))
        clients_today = cur.fetchone()["cnt"]

        cur.execute("""
            SELECT COUNT(*) as cnt FROM emails
            WHERE tags LIKE '%"job-lead"%' AND date_ts >= ?
        """, (today_start,))
        leads_today = cur.fetchone()["cnt"]

        # Total emails
        cur.execute("SELECT COUNT(*) as cnt FROM emails")
        total_emails = cur.fetchone()["cnt"]

        # Tag counts (all time)
        import json as _json
        cur.execute("SELECT tags FROM emails WHERE tags != '[]'")
        from collections import Counter
        tag_counts = Counter()
        for row in cur.fetchall():
            try:
                for t in _json.loads(row["tags"]):
                    tag_counts[t] += 1
            except Exception:
                pass

    return {
        "per_account": per_account,
        "clients_today": clients_today,
        "job_leads_today": leads_today,
        "total_emails": total_emails,
        "tag_counts": dict(tag_counts),
    }


# ── Drafts ────────────────────────────────────────────────────────────────────

def save_draft(account, uid, reply_text, created_at):
    # RULE: DRAFT ONLY - Never call SMTP send
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO drafts (account, uid, reply_text, created_at)
            VALUES (?, ?, ?, ?)
        """, (account, uid, reply_text, created_at))
        return cur.lastrowid


def get_drafts():
    with db_cursor() as cur:
        cur.execute("""
            SELECT d.id, d.account, d.uid, d.reply_text, d.created_at,
                   e.subject, e.from_addr
            FROM drafts d
            LEFT JOIN emails e ON e.account = d.account AND e.uid = d.uid
            ORDER BY d.created_at DESC
        """)
        return [dict(r) for r in cur.fetchall()]


# ── Telegram dedup ────────────────────────────────────────────────────────────

def get_unsent_alerts():
    """Return emails tagged client/job-lead not yet sent to Telegram."""
    with db_cursor() as cur:
        cur.execute("""
            SELECT e.account, e.uid, e.from_addr, e.subject, e.tags
            FROM emails e
            WHERE (e.tags LIKE '%"client"%' OR e.tags LIKE '%"job-lead"%')
            AND NOT EXISTS (
                SELECT 1 FROM telegram_sent ts
                WHERE ts.account = e.account AND ts.uid = e.uid
            )
            ORDER BY e.date_ts DESC
            LIMIT 20
        """)
        rows = cur.fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["tags"] = json.loads(d["tags"] or "[]")
        result.append(d)
    return result


def mark_alert_sent(account, uid, tag, sent_at):
    with db_cursor() as cur:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO telegram_sent (account, uid, tag, sent_at)
                VALUES (?, ?, ?, ?)
            """, (account, uid, tag, sent_at))
        except Exception:
            pass


# ── Marketing Contacts ─────────────────────────────────────────────────────────

def upsert_marketing_contact(email: str, name: str, source_account: str,
                             source_domain: str, first_seen_ts: int,
                             tags: list) -> None:
    """Insert or update a marketing contact."""
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO marketing_contacts
                (email, name, source_account, source_domain, first_seen_ts, tags)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                name           = COALESCE(excluded.name, marketing_contacts.name),
                source_account = COALESCE(excluded.source_account, marketing_contacts.source_account),
                source_domain  = COALESCE(excluded.source_domain, marketing_contacts.source_domain),
                first_seen_ts  = MIN(excluded.first_seen_ts, marketing_contacts.first_seen_ts)
        """, (email, name, source_account, source_domain, first_seen_ts,
               json.dumps(tags)))


def extract_marketing_contacts() -> int:
    """
    Scan all emails in DB, extract From addresses, and upsert into
    marketing_contacts, skipping no-reply/internal/own-domain senders.
    Returns count of contacts upserted.
    """
    import re as _re
    from email.utils import parseaddr as _parseaddr
    from config import OWN_DOMAINS

    SKIP_PREFIXES = (
        "no-reply@", "noreply@", "mailer-daemon@",
        "notifications@", "support@", "postmaster@",
        "bounce@", "do-not-reply@", "donotreply@",
    )

    seen = {}  # type: dict

    with db_cursor() as cur:
        cur.execute("""
            SELECT account, from_addr, date_ts
            FROM emails
            WHERE from_addr IS NOT NULL AND from_addr != ''
        """)
        rows = cur.fetchall()

    for row in rows:
        raw_from = row["from_addr"] or ""
        account = row["account"] or ""
        date_ts = row["date_ts"] or 0

        display_name, addr = _parseaddr(raw_from)
        addr = addr.lower().strip()
        if not addr or "@" not in addr:
            continue

        domain = addr.split("@", 1)[1]
        if domain in OWN_DOMAINS:
            continue

        # Skip noise address prefixes
        if any(addr.startswith(p) for p in SKIP_PREFIXES):
            continue

        # Keep earliest timestamp per address
        if addr not in seen or date_ts < seen[addr]["ts"]:
            seen[addr] = {
                "name": display_name.strip(),
                "source_account": account,
                "source_domain": domain,
                "ts": date_ts,
            }

    count = 0
    for addr, info in seen.items():
        try:
            upsert_marketing_contact(
                email=addr,
                name=info["name"],
                source_account=info["source_account"],
                source_domain=info["source_domain"],
                first_seen_ts=info["ts"],
                tags=[],
            )
            count += 1
        except Exception:
            pass

    return count


def get_marketing_contacts(page: int = 1, limit: int = 50,
                           source_domain: str = None,
                           tag: str = None) -> list:
    offset = (page - 1) * limit
    conditions = []  # type: list
    params = []  # type: list

    if source_domain:
        conditions.append("source_domain = ?")
        params.append(source_domain)
    if tag:
        conditions.append("tags LIKE ?")
        params.append(f'%"{tag}"%')

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params += [limit, offset]

    with db_cursor() as cur:
        cur.execute(f"""
            SELECT id, email, name, source_account, source_domain,
                   first_seen_ts, tags, unsubscribed
            FROM marketing_contacts
            {where}
            ORDER BY first_seen_ts DESC
            LIMIT ? OFFSET ?
        """, params)
        rows = cur.fetchall()

    result = []
    for row in rows:
        d = dict(row)
        d["tags"] = json.loads(d.get("tags") or "[]")
        result.append(d)
    return result


def get_marketing_stats() -> dict:
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM marketing_contacts")
        total_emails = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) as cnt FROM marketing_contacts WHERE unsubscribed = 1")
        unsub = cur.fetchone()["cnt"]

        cur.execute("""
            SELECT source_domain, COUNT(*) as cnt
            FROM marketing_contacts
            GROUP BY source_domain
            ORDER BY cnt DESC
        """)
        by_domain_rows = cur.fetchall()

        cur.execute("SELECT COUNT(*) as cnt FROM marketing_phones")
        total_phones = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) as cnt FROM marketing_phones WHERE whatsapp_opted_in = 1")
        whatsapp_opted_in = cur.fetchone()["cnt"]

    by_domain = {row["source_domain"]: row["cnt"] for row in by_domain_rows}
    return {
        "total_emails": total_emails,
        "total_phones": total_phones,
        "whatsapp_opted_in": whatsapp_opted_in,
        "unsubscribed": unsub,
        "by_domain": by_domain,
    }


# ── Marketing Phones ──────────────────────────────────────────────────────────

def add_marketing_phone(phone: str, name: str, email: str, source: str,
                        country_code: str, whatsapp_opted_in: int,
                        tags: list, notes: str, added_ts: int) -> int:
    """Insert a new phone number. Returns the new row id."""
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO marketing_phones
                (phone, name, email, source, country_code,
                 whatsapp_opted_in, tags, notes, added_ts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (phone, name, email, source, country_code,
               whatsapp_opted_in, json.dumps(tags), notes, added_ts))
        return cur.lastrowid


def get_marketing_phones(page: int = 1, limit: int = 50,
                         country_code: str = None,
                         whatsapp_opted_in: int = None) -> list:
    offset = (page - 1) * limit
    conditions = []  # type: list
    params = []      # type: list

    if country_code:
        conditions.append("country_code = ?")
        params.append(country_code)
    if whatsapp_opted_in is not None:
        conditions.append("whatsapp_opted_in = ?")
        params.append(whatsapp_opted_in)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params += [limit, offset]

    with db_cursor() as cur:
        cur.execute(f"""
            SELECT id, phone, name, email, source, country_code,
                   whatsapp_opted_in, added_ts, tags, notes
            FROM marketing_phones
            {where}
            ORDER BY added_ts DESC
            LIMIT ? OFFSET ?
        """, params)
        rows = cur.fetchall()

    result = []
    for row in rows:
        d = dict(row)
        d["tags"] = json.loads(d.get("tags") or "[]")
        result.append(d)
    return result


def get_all_marketing_export() -> dict:
    """Return all contacts and phones for full JSON export."""
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, email, name, source_account, source_domain,
                   first_seen_ts, tags, unsubscribed
            FROM marketing_contacts
            ORDER BY first_seen_ts DESC
        """)
        contact_rows = cur.fetchall()

        cur.execute("""
            SELECT id, phone, name, email, source, country_code,
                   whatsapp_opted_in, added_ts, tags, notes
            FROM marketing_phones
            ORDER BY added_ts DESC
        """)
        phone_rows = cur.fetchall()

    contacts = []
    for row in contact_rows:
        d = dict(row)
        d["tags"] = json.loads(d.get("tags") or "[]")
        contacts.append(d)

    phones = []
    for row in phone_rows:
        d = dict(row)
        d["tags"] = json.loads(d.get("tags") or "[]")
        phones.append(d)

    return {"contacts": contacts, "phones": phones}
