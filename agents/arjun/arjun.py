from __future__ import annotations

"""
ARJUN - LinkedIn Job Search Agent for Ashish Sharma (ITGYANI)
Searches LinkedIn public job listings, scores them with Claude Sonnet (Azure Foundry),
saves to SQLite, and sends Telegram alerts for high-scoring matches.

NEVER auto-applies. Find, score, and alert only.
"""

import json
import os
import random
import sqlite3
import time
import urllib.request
import urllib.parse
import urllib.error
import logging
import sys
from datetime import datetime
from typing import List, Dict, Optional, Any

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "arjun.log"), mode="a"),
    ],
)
log = logging.getLogger("ARJUN")

# ─── Config ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "jobs.db")
PROFILE_PATH = os.path.join(BASE_DIR, "profile.json")

AZURE_AI_URL = os.environ.get(
    "AZURE_AI_URL",
    "https://ai-sambhatt3210ai899661109114.services.ai.azure.com/anthropic/v1/messages",
)
AZURE_API_KEY = os.environ.get("AZURE_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-6"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = "427179140"

SCORE_THRESHOLD = 70
MAX_SEARCHES_PER_RUN = 15
MIN_DELAY_S = 3
MAX_DELAY_S = 6

USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]

# ─── Profile ─────────────────────────────────────────────────────────────────
def load_profile() -> Dict[str, Any]:
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)


# ─── Database ────────────────────────────────────────────────────────────────
def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id      TEXT PRIMARY KEY,
            title       TEXT,
            company     TEXT,
            location    TEXT,
            url         TEXT,
            score       INTEGER,
            verdict     TEXT,
            reasons     TEXT,
            missing     TEXT,
            scraped_at  TEXT,
            notified    INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn


def job_exists(conn: sqlite3.Connection, job_id: str) -> bool:
    cur = conn.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
    return cur.fetchone() is not None


def save_job(conn: sqlite3.Connection, job: Dict[str, Any]) -> None:
    conn.execute("""
        INSERT OR REPLACE INTO jobs
            (job_id, title, company, location, url, score, verdict, reasons, missing, scraped_at, notified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job["job_id"],
        job["title"],
        job["company"],
        job["location"],
        job["url"],
        job.get("score", 0),
        job.get("verdict", "skip"),
        json.dumps(job.get("reasons", [])),
        json.dumps(job.get("missing", [])),
        job.get("scraped_at", datetime.utcnow().isoformat()),
        job.get("notified", 0),
    ))
    conn.commit()


def mark_notified(conn: sqlite3.Connection, job_id: str) -> None:
    conn.execute("UPDATE jobs SET notified = 1 WHERE job_id = ?", (job_id,))
    conn.commit()


# ─── LinkedIn Scraper ─────────────────────────────────────────────────────────
def build_search_url(role: str, location: str) -> str:
    params = urllib.parse.urlencode({
        "keywords": role,
        "location": location,
        "f_TPR": "r86400",  # last 24 hours
        "sortBy": "DD",
    })
    return f"https://www.linkedin.com/jobs/search/?{params}"


def random_delay() -> None:
    delay = random.uniform(MIN_DELAY_S, MAX_DELAY_S)
    log.info(f"Sleeping {delay:.1f}s...")
    time.sleep(delay)


def scrape_linkedin_jobs(
    page: Any,
    role: str,
    location: str,
) -> List[Dict[str, Any]]:
    """Scrape LinkedIn public job search page for a given role + location."""
    url = build_search_url(role, location)
    log.info(f"Searching: {role} in {location}")
    log.info(f"URL: {url}")

    jobs: List[Dict[str, Any]] = []

    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        random_delay()

        # Check for captcha / auth wall
        current_url = page.url
        if "authwall" in current_url or "checkpoint" in current_url:
            log.warning("LinkedIn auth wall detected — stopping gracefully.")
            return []

        # Wait for job cards to appear
        try:
            page.wait_for_selector(".jobs-search__results-list, .base-search-card", timeout=12000)
        except Exception:
            log.warning(f"No job cards found for {role} in {location} — possibly blocked or no results.")
            return []

        # Extract job cards
        job_cards = page.query_selector_all(".base-card")
        if not job_cards:
            job_cards = page.query_selector_all("[data-entity-urn]")

        log.info(f"Found {len(job_cards)} job cards")

        for card in job_cards[:20]:  # cap per search
            try:
                job = extract_job_from_card(card)
                if job:
                    jobs.append(job)
            except Exception as e:
                log.debug(f"Error extracting card: {e}")
                continue

    except Exception as e:
        log.error(f"Error scraping {role} in {location}: {e}")

    return jobs


def extract_job_from_card(card: Any) -> Optional[Dict[str, Any]]:
    """Extract structured job data from a LinkedIn job card element."""

    # Job URL and ID
    link_el = card.query_selector("a.base-card__full-link, a[href*='/jobs/view/']")
    if not link_el:
        return None

    job_url = link_el.get_attribute("href") or ""
    if not job_url:
        return None

    # Normalize URL — strip query params for dedup
    job_url_clean = job_url.split("?")[0].rstrip("/")

    # Extract job_id from URL (LinkedIn uses numeric IDs)
    job_id = ""
    parts = job_url_clean.split("/")
    for part in reversed(parts):
        if part.isdigit():
            job_id = part
            break
    if not job_id:
        # Fallback: use URL hash
        job_id = str(abs(hash(job_url_clean)))

    # Title
    title_el = card.query_selector(
        "h3.base-search-card__title, .job-search-card__title, h3"
    )
    title = title_el.inner_text().strip() if title_el else "Unknown Title"

    # Company
    company_el = card.query_selector(
        "h4.base-search-card__subtitle, a.hidden-nested-link, .job-search-card__company-name"
    )
    company = company_el.inner_text().strip() if company_el else "Unknown Company"

    # Location
    location_el = card.query_selector(
        ".job-search-card__location, .base-search-card__metadata span"
    )
    location = location_el.inner_text().strip() if location_el else ""

    # Posted date (metadata)
    date_el = card.query_selector("time, .job-search-card__listdate")
    posted_date = ""
    if date_el:
        posted_date = date_el.get_attribute("datetime") or date_el.inner_text().strip()

    # Description snippet (from card if available)
    desc_el = card.query_selector(".base-search-card__snippet, .job-search-card__snippet")
    description_snippet = desc_el.inner_text().strip() if desc_el else ""

    return {
        "job_id": job_id,
        "title": title,
        "company": company,
        "location": location,
        "posted_date": posted_date,
        "job_url": job_url_clean,
        "description_snippet": description_snippet,
    }


# ─── AI Scoring ──────────────────────────────────────────────────────────────
def score_job_with_claude(job: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """Score a job against Ashish's profile using Azure Foundry Claude Sonnet."""

    prompt = f"""You are a senior recruiter helping evaluate job fit.

CANDIDATE PROFILE:
- Name: {profile['name']}
- Experience: {profile['experience_years']}+ years in Digital IT, AI Leadership, Cloud
- Current Role: {profile['current_role']}
- Target Roles: {', '.join(profile['target_roles'])}
- Target Locations: {', '.join(profile['target_locations'])}
- Key Skills: {', '.join(profile['skills'][:15])}
- Needs visa sponsorship: {profile['needs_visa_sponsorship']}
- Min Salary: {profile['min_salary_lpa']} LPA INR equivalent

JOB POSTING:
- Title: {job['title']}
- Company: {job['company']}
- Location: {job['location']}
- Posted: {job.get('posted_date', 'N/A')}
- Description: {job.get('description_snippet', 'N/A')}
- URL: {job['job_url']}

Score this job 0-100 for fit with the candidate profile.
Consider: role alignment, location match, seniority level, likely visa sponsorship availability.
Return ONLY valid JSON (no markdown, no explanation outside JSON):
{{"score": <0-100>, "reasons": ["reason1", "reason2"], "missing": ["gap1", "gap2"], "verdict": "<apply|review|skip>"}}

Verdict guide: apply=score≥75, review=50-74, skip<50"""

    payload = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        AZURE_AI_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-api-key": AZURE_API_KEY,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            # Claude response structure
            content = body.get("content", [])
            if content and isinstance(content, list):
                text = content[0].get("text", "{}")
            else:
                text = "{}"

            # Parse the JSON scoring response
            scoring = json.loads(text.strip())
            return {
                "score": int(scoring.get("score", 0)),
                "reasons": scoring.get("reasons", []),
                "missing": scoring.get("missing", []),
                "verdict": scoring.get("verdict", "skip"),
            }

    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if hasattr(e, "read") else str(e)
        log.error(f"Claude API HTTP error {e.code}: {err_body[:300]}")
    except urllib.error.URLError as e:
        log.error(f"Claude API URL error: {e.reason}")
    except json.JSONDecodeError as e:
        log.error(f"Claude response JSON parse error: {e}")
    except Exception as e:
        log.error(f"Claude scoring error: {e}")

    return {"score": 0, "reasons": ["scoring_failed"], "missing": [], "verdict": "skip"}


# ─── Telegram ────────────────────────────────────────────────────────────────
def send_telegram_alert(job: Dict[str, Any], scoring: Dict[str, Any]) -> bool:
    """Send a Telegram message for high-scoring jobs."""
    if not TELEGRAM_BOT_TOKEN:
        log.warning("TELEGRAM_BOT_TOKEN not set — skipping alert.")
        return False

    reasons_text = "\n  • " + "\n  • ".join(scoring.get("reasons", [])) if scoring.get("reasons") else " N/A"
    missing_text = "\n  • " + "\n  • ".join(scoring.get("missing", [])) if scoring.get("missing") else " None"

    message = (
        f"💼 New Job Match (Score: {scoring['score']}/100)\n"
        f"*{job['title']}* at {job['company']}\n"
        f"📍 {job['location']}\n"
        f"🔗 {job['job_url']}\n\n"
        f"✅ Why:{reasons_text}\n\n"
        f"⚠️ Missing:{missing_text}"
    )

    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }).encode("utf-8")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("ok"):
                log.info(f"Telegram alert sent for: {job['title']} at {job['company']}")
                return True
            else:
                log.error(f"Telegram API error: {result}")
    except Exception as e:
        log.error(f"Telegram send error: {e}")

    return False


# ─── Main Agent ──────────────────────────────────────────────────────────────
def run_agent() -> None:
    log.info("=" * 60)
    log.info("ARJUN Job Search Agent — Starting run")
    log.info(f"Timestamp: {datetime.utcnow().isoformat()}")
    log.info("=" * 60)

    profile = load_profile()
    conn = init_db()

    # Build search matrix: roles × locations (capped at MAX_SEARCHES_PER_RUN)
    search_roles: List[str] = profile["keywords"]
    search_locations: List[str] = profile["target_locations"]

    search_pairs: List[tuple] = []
    for role in search_roles:
        for loc in search_locations:
            search_pairs.append((role, loc))

    # Shuffle and cap
    random.shuffle(search_pairs)
    search_pairs = search_pairs[:MAX_SEARCHES_PER_RUN]

    log.info(f"Running {len(search_pairs)} searches across {len(search_roles)} roles × {len(search_locations)} locations")

    # Stats
    stats = {
        "searches": 0,
        "jobs_found": 0,
        "new_jobs": 0,
        "scored": 0,
        "alerted": 0,
        "blocked": False,
    }

    # ── Playwright setup ──────────────────────────────────────────────────────
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    except ImportError:
        log.error("Playwright not installed. Run: pip install playwright==1.44.0 && playwright install chromium")
        sys.exit(1)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1366,768",
            ],
        )

        ua = random.choice(USER_AGENTS)
        context = browser.new_context(
            user_agent=ua,
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="Asia/Singapore",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
            },
        )

        # Mask webdriver fingerprint
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()
        log.info(f"Browser launched with UA: {ua[:60]}...")

        for role, location in search_pairs:
            if stats["blocked"]:
                log.warning("Blocked flag set — stopping search loop.")
                break

            stats["searches"] += 1

            jobs = scrape_linkedin_jobs(page, role, location)

            # Check if blocked mid-run
            if page.url and ("authwall" in page.url or "checkpoint" in page.url):
                log.warning("Blocked by LinkedIn — stopping gracefully.")
                stats["blocked"] = True
                break

            stats["jobs_found"] += len(jobs)

            for job in jobs:
                job_id = job["job_id"]

                if job_exists(conn, job_id):
                    log.debug(f"Already seen: {job['title']} [{job_id}]")
                    continue

                stats["new_jobs"] += 1
                log.info(f"New job: {job['title']} @ {job['company']} | {job['location']}")

                # Score with Claude
                scoring = score_job_with_claude(job, profile)
                stats["scored"] += 1
                log.info(f"  Score: {scoring['score']}/100 | Verdict: {scoring['verdict']}")

                # Merge and save
                full_record = {**job, **scoring, "scraped_at": datetime.utcnow().isoformat(), "notified": 0}
                save_job(conn, full_record)

                # Alert if high score
                if scoring["score"] >= SCORE_THRESHOLD:
                    sent = send_telegram_alert(job, scoring)
                    if sent:
                        mark_notified(conn, job_id)
                        stats["alerted"] += 1

                # Polite delay between AI calls
                time.sleep(random.uniform(1.0, 2.5))

            # Delay between page loads
            if stats["searches"] < len(search_pairs):
                random_delay()

        browser.close()

    conn.close()

    log.info("=" * 60)
    log.info("ARJUN Run Complete")
    log.info(f"  Searches:    {stats['searches']}")
    log.info(f"  Jobs found:  {stats['jobs_found']}")
    log.info(f"  New jobs:    {stats['new_jobs']}")
    log.info(f"  Scored:      {stats['scored']}")
    log.info(f"  Alerted:     {stats['alerted']}")
    log.info(f"  Blocked:     {stats['blocked']}")
    log.info("=" * 60)


if __name__ == "__main__":
    run_agent()
