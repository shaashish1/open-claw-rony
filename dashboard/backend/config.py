from __future__ import annotations
"""
ITGYANI Dashboard — Email Account Configuration
RULE: DRAFT ONLY - Never call SMTP send
"""
import os
import ssl
from pathlib import Path

# ── Account definitions ──────────────────────────────────────────────────────
ACCOUNTS = [
    {
        "email": os.getenv("GMAIL_PERSONAL_EMAIL", "ashish.sharma14@gmail.com"),
        "imap_host": "imap.gmail.com",
        "imap_port": 993,
        "password": os.getenv("GMAIL_PERSONAL_PASS", ""),
        "ssl_verify": True,
        "label": "Gmail Personal",
    },
    {
        "email": os.getenv("GMAIL_ITGYANI_EMAIL", "ashish@itgyani.com"),
        "imap_host": "imap.gmail.com",
        "imap_port": 993,
        "password": os.getenv("GMAIL_ITGYANI_PASS", ""),
        "ssl_verify": True,
        "label": "ITGYANI",
    },
    {
        "email": os.getenv("VPS_CRYPTOGYANI_EMAIL", "ashish@cryptogyani.com"),
        "imap_host": "194.233.64.74",
        "imap_port": 993,
        "password": os.getenv("VPS_CRYPTOGYANI_PASS", ""),
        "ssl_verify": False,
        "label": "CryptoGyani Ashish",
    },
    {
        "email": os.getenv("VPS_CRYPTOGYANI_INFO_EMAIL", "info@cryptogyani.com"),
        "imap_host": "194.233.64.74",
        "imap_port": 993,
        "password": os.getenv("VPS_CRYPTOGYANI_INFO_PASS", ""),
        "ssl_verify": False,
        "label": "CryptoGyani Info",
    },
    {
        "email": os.getenv("VPS_CRYPTOGYANI_TRADING_EMAIL", "trading@cryptogyani.com"),
        "imap_host": "194.233.64.74",
        "imap_port": 993,
        "password": os.getenv("VPS_CRYPTOGYANI_TRADING_PASS", ""),
        "ssl_verify": False,
        "label": "CryptoGyani Trading",
    },
    {
        "email": os.getenv("VPS_TEF_EMAIL", "ashish@theemployeefactory.com"),
        "imap_host": "194.233.64.74",
        "imap_port": 993,
        "password": os.getenv("VPS_TEF_PASS", ""),
        "ssl_verify": False,
        "label": "Employee Factory",
    },
    {
        "email": os.getenv("VPS_TEF_SUPPORT_EMAIL", "support@theemployeefactory.com"),
        "imap_host": "194.233.64.74",
        "imap_port": 993,
        "password": os.getenv("VPS_TEF_SUPPORT_PASS", ""),
        "ssl_verify": False,
        "label": "Employee Factory Support",
    },
    {
        "email": os.getenv("VPS_TECHNOFLAIRLAB_EMAIL", "ashish@technoflairlab.com"),
        "imap_host": "194.233.64.74",
        "imap_port": 993,
        "password": os.getenv("VPS_TECHNOFLAIRLAB_PASS", ""),
        "ssl_verify": False,
        "label": "TechnoFlairLab",
    },
    {
        "email": os.getenv("VPS_KHARADI_EMAIL", "info@kharadionline.com"),
        "imap_host": "194.233.64.74",
        "imap_port": 993,
        "password": os.getenv("VPS_KHARADI_PASS", ""),
        "ssl_verify": False,
        "label": "Kharadi Online",
    },
]

ACCOUNTS_BY_EMAIL = {a["email"]: a for a in ACCOUNTS}

# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = "427179140"

# ── Database ──────────────────────────────────────────────────────────────────
# In Docker: /app/data/dashboard.db | Locally: ../data/dashboard.db
_base = Path("/app") if Path("/app").exists() else Path(__file__).parent.parent
DB_PATH = str(_base / "data" / "dashboard.db")

# ── Tagging rules ─────────────────────────────────────────────────────────────
TAG_RULES = {
    "client": [
        "invoice", "project", "proposal", "contract",
        "payment", "client", "work",
    ],
    "job-lead": [
        "job", "opportunity", "hiring", "position",
        "recruiter", "apply", "career", "linkedin", "indeed", "naukri",
    ],
    "payment": [
        "payment", "invoice", "paid", "receipt", "transaction",
    ],
}
