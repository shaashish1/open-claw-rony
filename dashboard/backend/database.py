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


def get_emails(account=None, folder="INBOX", page=1, limit=50, tag_filter=None):
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

    return {
        "per_account": per_account,
        "clients_today": clients_today,
        "job_leads_today": leads_today,
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
