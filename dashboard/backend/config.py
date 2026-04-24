from __future__ import annotations
"""
ITGYANI Dashboard — Email Account Configuration
RULE: DRAFT ONLY - Never call SMTP send
"""
import os
import ssl
from pathlib import Path

# ── Account definitions ──────────────────────────────────────────────────────
# NOTE: ashish.sharma14@gmail.com (personal Gmail) intentionally excluded.
# Handled manually by Ashish for privacy/safety reasons.

ACCOUNTS = [
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

# ── SMTP config ───────────────────────────────────────────────────────────────
SMTP_CONFIG = {
    "imap.gmail.com": {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "use_tls": True,
    },
    "194.233.64.74": {
        "smtp_host": "194.233.64.74",
        "smtp_port": 587,
        "use_tls": True,
    },
}

# Our own domains — used to filter out internal addresses in marketing extraction
OWN_DOMAINS = {
    "itgyani.com",
    "cryptogyani.com",
    "kharadionline.com",
    "theemployeefactory.com",
    "technoflairlab.com",
}

# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = "427179140"

# ── Database ──────────────────────────────────────────────────────────────────
# In Docker: /app/data/dashboard.db | Locally: ../data/dashboard.db
# Always use directory relative to this file
_base = Path(__file__).parent.parent
if Path("/app/data").exists():
    _base = Path("/app")
elif Path("/opt/itgyani-dashboard/data").exists():
    _base = Path("/opt/itgyani-dashboard")
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
