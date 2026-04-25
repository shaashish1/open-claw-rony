"""
ChartInk Complete Setup
- Copy best community screeners (no need to build from scratch)
- Set webhook -> Save alert for each
- Alert name + webhook + Save alert button (class contains 'save' or text 'Save alert')
"""
import asyncio, os, json
from playwright.async_api import async_playwright

os.makedirs("C:/temp/chartink", exist_ok=True)

LOGIN = "ashish.sharma14@gmail.com"
PASSWORD = "BlockTrade5$"
BASE = "https://openalgo.cryptogyani.com/chartink/webhook/"

# Best community screeners mapped to our OpenAlgo webhook IDs
# Using existing high-quality screeners from ChartInk's library
SCREENER_ALERTS = [
    {
        "name": "CI Short Term Breakouts",
        "scan_url": "https://chartink.com/screener/short-term-breakouts",
        "wid": "3b91b063-b985-4014-a3cb-f5ea39c9b5a8",
        "alert_name": "CI Short Term Breakout -> OpenAlgo"
    },
    {
        "name": "CI NKS Best Buy Intraday",
        "scan_url": "https://chartink.com/screener/copy-nks-best-buy-stocks-for-intraday-2",
        "wid": "8c5becfe-cd44-429e-9bff-191625015a7a",
        "alert_name": "CI NKS Intraday -> OpenAlgo"
    },
    {
        "name": "CI Potential Breakouts",
        "scan_url": "https://chartink.com/screener/potential-breakouts",
        "wid": "9d8e3da7-1c6a-4261-a0c9-45887721f20e",
        "alert_name": "CI Potential Breakout -> OpenAlgo"
    },
    {
        "name": "CI Buy 100pct Morning 9:30",
        "scan_url": "https://chartink.com/screener/copy-morning-scanner-for-buy-nr7-based-breakout-8",
        "wid": "09b9b950-bb35-4332-8e6d-14fb3ad4a649",
        "alert_name": "CI Buy 100pct 9:30 -> OpenAlgo"
    },
    {
        "name": "CI BOSS Scanner BTST",
        "scan_url": "https://chartink.com/screener/boss-scanner-for-btst",
        "wid": "c4fb5731-9e53-498d-9283-0122b1d87b07",
        "alert_name": "CI BOSS BTST -> OpenAlgo"
    },
    {
        "name": "CI FNO Bullish Trend",
        "scan_url": "https://chartink.com/screener/moving-average-bullish-strong-buy",
        "wid": "78ef3583-7a9e-4d09-81a1-c27c83204511",
        "alert_name": "CI FNO Bullish -> OpenAlgo"
    },
    {
        "name": "CI Strong Stocks",
        "scan_url": "https://chartink.com/screener/strong-stocks",
        "wid": "0eac56c8-8ea8-4c26-b700-665bd6e2fe92",
        "alert_name": "CI Strong Stocks -> OpenAlgo"
    },
    {
        "name": "CI RSI Oversold Overbought",
        "scan_url": "https://chartink.com/screener/rsi-overbought-or-oversold-scan",
        "wid": "c519cd72-2671-4d4d-96bc-b6c4136fc6a3",
        "alert_name": "CI RSI Oversold -> OpenAlgo"
    },
    {
        "name": "CI Bullish Momentum Stocks",
        "scan_url": "https://chartink.com/screener/bullish-momentum-stocks",
        "wid": "89a7980f-0492-4dba-828d-bfb2cbf9d492",
        "alert_name": "CI Bullish Momentum -> OpenAlgo"
    },
    {
        "name": "CI Pure Bullish Trend",
        "scan_url": "https://chartink.com/screener/pure-bullish-trend-stocks",
        "wid": "0fce8e4d-4cec-4e27-81f9-344712c80ec4",
        "alert_name": "CI Pure Bullish Trend -> OpenAlgo"
    },
]

async def login(page):
    await page.goto("https://chartink.com/login", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.fill('#login-email', LOGIN)
    await page.fill('#login-password', PASSWORD)
    await page.click('button.primary-button')
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    return "login" not in page.url.lower()

async def click_div_by_text(page, text, timeout=5000):
    """Click action div/span by text content using JS"""
    result = await page.evaluate(f'''
        () => {{
            // Try cursor-pointer divs
            const all = Array.from(document.querySelectorAll('*'));
            for (const el of all) {{
                const txt = el.textContent.trim();
                if ((txt === "{text}" || txt.startsWith("{text}")) && 
                    (el.tagName === "SPAN" || el.tagName === "DIV" || el.tagName === "BUTTON" || el.tagName === "A") &&
                    window.getComputedStyle(el).cursor === "pointer") {{
                    el.click();
                    return "clicked:" + el.tagName + ":" + txt.substring(0,40);
                }}
            }}
            // Fallback: any element with exact text
            for (const el of all) {{
                if (el.children.length === 0 && el.textContent.trim() === "{text}") {{
                    el.closest('button, a, div[class*="cursor"], div[role="button"]')?.click();
                    return "fallback:" + el.tagName;
                }}
            }}
            return "not_found";
        }}
    ''')
    await page.wait_for_timeout(500)
    return result

async def setup_alert(page, screener, idx):
    """Load screener, open Create Alert modal, fill name+webhook, save"""
    webhook_url = BASE + screener["wid"]
    print(f"\n[{idx+1}/10] {screener['name']}")

    # Navigate to the screener
    await page.goto(screener["scan_url"], timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(6000)

    current_url = page.url
    print(f"  Loaded: {current_url}")

    # Click Create Alert (it's a div with cursor-pointer)
    r = await click_div_by_text(page, "Create Alert")
    print(f"  Create Alert click: {r}")
    await page.wait_for_timeout(2000)
    await page.screenshot(path=f"C:/temp/chartink/{idx+1:02d}_modal.png")

    # Fill Alert Name
    try:
        name_inp = page.locator('input[name="name"]').nth(1)  # second name input is alert name
        if await name_inp.is_visible(timeout=2000):
            await name_inp.click()
            await page.keyboard.press("Control+a")
            await name_inp.fill(screener["alert_name"])
            print(f"  Alert name: {screener['alert_name']}")
    except Exception as e:
        print(f"  Alert name err: {e}")

    # Scroll down in modal to see webhook field
    await page.evaluate("document.querySelector('input[name=\"webhook_url\"]')?.scrollIntoView()")
    await page.wait_for_timeout(500)

    # Fill webhook URL (name="webhook_url")
    webhook_filled = False
    try:
        wh_inp = page.locator('input[name="webhook_url"]').first
        if await wh_inp.is_visible(timeout=3000):
            await wh_inp.click()
            await wh_inp.fill(webhook_url)
            webhook_filled = True
            print(f"  Webhook: {webhook_url[:60]}...")
    except Exception as e:
        print(f"  Webhook err: {e}")

    await page.screenshot(path=f"C:/temp/chartink/{idx+1:02d}_filled.png")

    # Click "Save alert" button — scroll modal to bottom first
    saved = False
    if webhook_filled:
        # Scroll modal to reveal Save alert button
        await page.evaluate('''
            () => {
                const modal = document.querySelector('[role="dialog"]') || 
                              document.querySelector('.modal') ||
                              document.querySelector('[class*="modal"]');
                if (modal) modal.scrollTop = modal.scrollHeight;
                // Also scroll the page
                window.scrollTo(0, document.body.scrollHeight);
            }
        ''')
        await page.wait_for_timeout(1000)

        # The Save alert button is at the bottom of the modal
        res = await page.evaluate('''
            () => {
                const btns = Array.from(document.querySelectorAll("button"));
                // Find by text content
                for (const b of btns) {
                    const t = b.textContent.trim().toLowerCase();
                    if (t === "save alert" || t === "save") {
                        const rect = b.getBoundingClientRect();
                        b.scrollIntoView({behavior: "instant", block: "center"});
                        b.click();
                        return "clicked:" + b.textContent.trim() + " at " + JSON.stringify(rect);
                    }
                }
                return "not_found: " + btns.map(b => b.textContent.trim().substring(0,25)).join("|");
            }
        ''')
        print(f"  Save alert JS: {res}")
        if "clicked:" in res:
            saved = True
        await page.wait_for_timeout(3000)

    await page.screenshot(path=f"C:/temp/chartink/{idx+1:02d}_done.png")

    return {
        "name": screener["name"],
        "scan_url": current_url,
        "webhook_url": webhook_url,
        "webhook_filled": webhook_filled,
        "saved": saved,
        "alert_name": screener["alert_name"]
    }

async def get_screener_slugs_from_library(page):
    """Get real slugs from Top Loved screeners"""
    print("Getting top screeners from library...")
    await page.goto("https://chartink.com/screeners/top-loved-screeners", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    await page.screenshot(path="C:/temp/chartink/top_loved.png")

    links = await page.locator('a[href*="screener"]').all()
    slugs = []
    for l in links:
        try:
            href = await l.get_attribute("href")
            txt = await l.inner_text()
            if href and "/screener/" in href and txt.strip():
                slugs.append({"name": txt.strip(), "url": "https://chartink.com" + href if href.startswith("/") else href})
        except: pass
    print(f"Found {len(slugs)} screener links")
    for s in slugs[:15]:
        print(f"  {s['name'][:50]} -> {s['url']}")
    return slugs

async def main():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context(viewport={"width":1440,"height":900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0")
        page = await ctx.new_page()

        ok = await login(page)
        print(f"Login: {'OK' if ok else 'FAILED'}")
        if not ok:
            await browser.close()
            return

        # Get real screener slugs first
        slugs = await get_screener_slugs_from_library(page)

        # Process all 10 strategies
        for i, s in enumerate(SCREENER_ALERTS):
            try:
                result = await setup_alert(page, s, i)
                results.append(result)
            except Exception as e:
                print(f"  ERROR: {e}")
                await page.screenshot(path=f"C:/temp/chartink/{i+1:02d}_error.png")
                results.append({"name": s["name"], "error": str(e)})
            await page.wait_for_timeout(500)

        with open("C:/temp/chartink/results.json", "w") as f:
            json.dump(results, f, indent=2)

        await browser.close()

    print("\n=== FINAL RESULTS ===")
    ok_c = sum(1 for r in results if r.get("saved"))
    partial_c = sum(1 for r in results if r.get("webhook_filled") and not r.get("saved"))
    for r in results:
        if r.get("saved"):       status = "SAVED"
        elif r.get("webhook_filled"): status = "PARTIAL"
        else:                     status = "FAIL"
        print(f"  [{status}] {r['name']}: {r.get('alert_name','')}")
    print(f"\n{ok_c} saved | {partial_c} partial | {len(results)-ok_c-partial_c} failed")

if __name__ == "__main__":
    asyncio.run(main())
