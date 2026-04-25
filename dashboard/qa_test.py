"""
Rony QA Test — opens each URL, takes screenshot, checks for content.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS = Path("C:/temp/dashboard_qa")
SCREENSHOTS.mkdir(parents=True, exist_ok=True)

URLS = [
    ("ops_dashboard",    "https://dashboard.itgyani.com/ops",     ["ITGYANI OS", "Agents", "System Health"]),
    ("api_ops_status",   "https://dashboard.itgyani.com/api/ops/status", ["containers", "strategies"]),
    ("api_ops_mom",      "https://dashboard.itgyani.com/api/ops/mom",    ["["]),
    ("openalgo",         "https://openalgo.cryptogyani.com",       ["OpenAlgo", "Dashboard"]),
    ("n8n",              "https://n8n.itgyani.com",                ["n8n"]),
    ("chartink_alerts",  "https://chartink.com/alert_dashboard",   ["alert", "webhook"]),
    ("jira_sprint",      "https://itgyani.atlassian.net/jira/software/projects/IT/boards/7", ["IT", "Sprint", "board"]),
    ("cryptogyani",      "https://cryptogyani.com",                ["CryptoGyani"]),
    ("itgyani_site",     "https://itgyani.com",                    ["ITGYANI"]),
]

async def test_url(page, name, url, checks):
    print(f"\n[{name}] Opening {url}")
    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(3)
        await page.screenshot(path=str(SCREENSHOTS / f"{name}.png"), full_page=False)
        
        code = resp.status if resp else 0
        content = await page.content()
        
        passed = []
        failed = []
        for check in checks:
            if check.lower() in content.lower():
                passed.append(check)
            else:
                failed.append(check)
        
        title = await page.title()
        status = "✅ PASS" if not failed else "⚠️  PARTIAL" if passed else "❌ FAIL"
        print(f"  {status} | HTTP {code} | Title: {title[:60]}")
        if failed:
            print(f"  Missing: {failed}")
        return {"name": name, "url": url, "code": code, "title": title, "passed": passed, "failed": failed}
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return {"name": name, "url": url, "code": 0, "error": str(e)}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.set_default_timeout(20000)
        
        results = []
        for name, url, checks in URLS:
            r = await test_url(page, name, url, checks)
            results.append(r)
        
        await browser.close()
        
        print("\n" + "="*60)
        print("QA SUMMARY")
        print("="*60)
        for r in results:
            if "error" in r:
                print(f"❌ {r['name']:25} ERROR: {r['error'][:50]}")
            elif r["failed"]:
                print(f"⚠️  {r['name']:25} HTTP {r['code']} | Missing: {r['failed']}")
            else:
                print(f"✅ {r['name']:25} HTTP {r['code']} | {r.get('title','')[:40]}")
        
        print(f"\nScreenshots: {SCREENSHOTS}")

asyncio.run(main())
