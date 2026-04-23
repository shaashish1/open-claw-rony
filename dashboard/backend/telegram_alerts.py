"""
ITGYANI Dashboard — Telegram alert dispatcher
RULE: DRAFT ONLY - Never call SMTP send
"""
import time
import logging
import httpx

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ACCOUNTS_BY_EMAIL
import database as db

logger = logging.getLogger("telegram_alerts")


async def send_telegram_message(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "placeholder":
        logger.debug("TELEGRAM_BOT_TOKEN not configured — skipping alert")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


async def dispatch_alerts():
    """Check for new tagged emails and send Telegram alerts (deduped)."""
    now = int(time.time())
    unsent = db.get_unsent_alerts()

    for item in unsent:
        account = item["account"]
        uid = item["uid"]
        tags = item["tags"]
        from_addr = item.get("from_addr", "Unknown")
        subject = item.get("subject", "(no subject)")

        acc_cfg = ACCOUNTS_BY_EMAIL.get(account, {})
        label = acc_cfg.get("label", account)

        alert_tags = [t for t in tags if t in ("client", "job-lead")]
        for tag in alert_tags:
            tag_label = "Client" if tag == "client" else "Job Lead"
            text = (
                f"📧 <b>[{label}]</b> New {tag_label}\n"
                f"<b>From:</b> {from_addr}\n"
                f"<b>Subject:</b> {subject}"
            )
            sent = await send_telegram_message(text)
            if sent:
                db.mark_alert_sent(account, uid, tag, now)
                logger.info(f"Alert sent for {account}/{uid} [{tag}]")
