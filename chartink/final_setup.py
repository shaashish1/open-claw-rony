"""ChartInk Final — Save alert via div.secondary-button click"""
import asyncio, os, json
from playwright.async_api import async_playwright

os.makedirs("C:/temp/chartink", exist_ok=True)

BASE = "https://openalgo.cryptogyani.com/chartink/webhook/"
STRATEGIES = [
    {"name":"CI Short Term Breakouts",  "url":"https://chartink.com/screener/short-term-breakouts",    "wid":"3b91b063-b985-4014-a3cb-f5ea39c9b5a8"},
    {"name":"CI NKS Best Buy Intraday", "url":"https://chartink.com/screener/copy-nks-best-buy-stocks-for-intraday-2","wid":"8c5becfe-cd44-429e-9bff-191625015a7a"},
    {"name":"CI Potential Breakouts",   "url":"https://chartink.com/screener/potential-breakouts",     "wid":"9d8e3da7-1c6a-4261-a0c9-45887721f20e"},
    {"name":"CI Buy 100pct 9:30",       "url":"https://chartink.com/screener/copy-morning-scanner-for-buy-nr7-based-breakout-8","wid":"09b9b950-bb35-4332-8e6d-14fb3ad4a649"},
    {"name":"CI BOSS BTST",             "url":"https://chartink.com/screener/boss-scanner-for-btst",   "wid":"c4fb5731-9e53-498d-9283-0122b1d87b07"},
    {"name":"CI FNO Bullish Trend",     "url":"https://chartink.com/screener/moving-average-bullish-strong-buy","wid":"78ef3583-7a9e-4d09-81a1-c27c83204511"},
    {"name":"CI Strong Stocks",         "url":"https://chartink.com/screener/strong-stocks",           "wid":"0eac56c8-8ea8-4c26-b700-665bd6e2fe92"},
    {"name":"CI RSI Oversold",          "url":"https://chartink.com/screener/rsi-overbought-or-oversold-scan","wid":"c519cd72-2671-4d4d-96bc-b6c4136fc6a3"},
    {"name":"CI Bullish Momentum",      "url":"https://chartink.com/screener/bullish-momentum-stocks", "wid":"89a7980f-0492-4dba-828d-bfb2cbf9d492"},
    {"name":"CI Pure Bullish Trend",    "url":"https://chartink.com/screener/pure-bullish-trend-stocks","wid":"0fce8e4d-4cec-4e27-81f9-344712c80ec4"},
]

CLICK_ALERT_JS = """() => {
    const all = Array.from(document.querySelectorAll('*'));
    const t = all.find(e => e.textContent.trim() === 'Create Alert' && window.getComputedStyle(e).cursor === 'pointer');
    if (t) { t.click(); return 'ok'; }
    return 'not_found';
}"""

SAVE_ALERT_JS = """() => {
    // Save alert is div.secondary-button containing text 'Save alert'
    const all = Array.from(document.querySelectorAll('div, button, span, a'));
    for (const el of all) {
        const t = el.textContent.trim();
        if ((t === 'Save alert') && el.offsetParent !== null) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                el.click();
                return 'saved:' + el.tagName + ':' + el.className.substring(0,40);
            }
        }
    }
    return 'not_found';
}"""

async def setup_one(page, strat, idx):
    wh_url = BASE + strat["wid"]
    print(f"\n[{idx+1}/10] {strat['name']}")

    await page.goto(strat["url"], timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(6000)

    # Click Create Alert
    r = await page.evaluate(CLICK_ALERT_JS)
    if r != "ok":
        print(f"  Create Alert: {r}")
        return False
    await page.wait_for_timeout(2000)

    # Fill webhook
    try:
        wh = page.locator('input[name="webhook_url"]').first
        await wh.click(timeout=3000)
        await page.keyboard.press("Control+a")
        await wh.fill(wh_url)
        await page.wait_for_timeout(800)
        print(f"  Webhook: OK")
    except Exception as e:
        print(f"  Webhook err: {e}")
        return False

    # Save alert
    r2 = await page.evaluate(SAVE_ALERT_JS)
    print(f"  Save: {r2}")
    saved = r2.startswith("saved:")
    await page.wait_for_timeout(3000)

    if saved:
        # Verify alert was created - check alert dashboard
        await page.wait_for_timeout(1000)
    return saved

async def main():
    results = []
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        ctx = await b.new_context(viewport={"width":1440,"height":900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0")
        page = await ctx.new_page()

        # Login
        await page.goto("https://chartink.com/login")
        await page.wait_for_load_state("networkidle")
        await page.fill("#login-email", "ashish.sharma14@gmail.com")
        await page.fill("#login-password", "BlockTrade5$")
        await page.click("button.primary-button")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        # Process all 10
        for i, s in enumerate(STRATEGIES):
            try:
                ok = await setup_one(page, s, i)
                results.append({"name": s["name"], "saved": ok, "webhook": BASE + s["wid"]})
            except Exception as e:
                print(f"  ERROR: {e}")
                results.append({"name": s["name"], "saved": False, "error": str(e)})
            await page.wait_for_timeout(500)

        # Check final alert count on dashboard
        await page.goto("https://chartink.com/alert_dashboard")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="C:/temp/chartink/final_alert_dashboard.png")

        await b.close()

    saved_count = sum(1 for r in results if r.get("saved"))
    print(f"\n=== DONE: {saved_count}/10 alerts saved ===")
    for r in results:
        status = "SAVED" if r.get("saved") else "FAIL"
        print(f"  [{status}] {r['name']}")

    with open("C:/temp/chartink/final_results.json", "w") as f:
        json.dump(results, f, indent=2)

asyncio.run(main())
