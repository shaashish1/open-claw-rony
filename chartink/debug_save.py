import asyncio, os
from playwright.async_api import async_playwright

os.makedirs("C:/temp/chartink", exist_ok=True)

BASE = "https://openalgo.cryptogyani.com/chartink/webhook/"
STRATEGIES = [
    {"name":"CI Short Term Breakouts",   "url":"https://chartink.com/screener/short-term-breakouts",    "wid":"3b91b063-b985-4014-a3cb-f5ea39c9b5a8"},
    {"name":"CI NKS Best Buy Intraday",  "url":"https://chartink.com/screener/copy-nks-best-buy-stocks-for-intraday-2","wid":"8c5becfe-cd44-429e-9bff-191625015a7a"},
    {"name":"CI Potential Breakouts",    "url":"https://chartink.com/screener/potential-breakouts",      "wid":"9d8e3da7-1c6a-4261-a0c9-45887721f20e"},
    {"name":"CI Buy 100pct 9:30",        "url":"https://chartink.com/screener/copy-morning-scanner-for-buy-nr7-based-breakout-8","wid":"09b9b950-bb35-4332-8e6d-14fb3ad4a649"},
    {"name":"CI BOSS BTST",              "url":"https://chartink.com/screener/boss-scanner-for-btst",    "wid":"c4fb5731-9e53-498d-9283-0122b1d87b07"},
    {"name":"CI FNO Bullish Trend",      "url":"https://chartink.com/screener/moving-average-bullish-strong-buy","wid":"78ef3583-7a9e-4d09-81a1-c27c83204511"},
    {"name":"CI Strong Stocks",          "url":"https://chartink.com/screener/strong-stocks",            "wid":"0eac56c8-8ea8-4c26-b700-665bd6e2fe92"},
    {"name":"CI RSI Oversold",           "url":"https://chartink.com/screener/rsi-overbought-or-oversold-scan","wid":"c519cd72-2671-4d4d-96bc-b6c4136fc6a3"},
    {"name":"CI Bullish Momentum",       "url":"https://chartink.com/screener/bullish-momentum-stocks",  "wid":"89a7980f-0492-4dba-828d-bfb2cbf9d492"},
    {"name":"CI Pure Bullish Trend",     "url":"https://chartink.com/screener/pure-bullish-trend-stocks","wid":"0fce8e4d-4cec-4e27-81f9-344712c80ec4"},
]

CLICK_ALERT_JS = """
() => {
    const all = Array.from(document.querySelectorAll('*'));
    const t = all.find(e => {
        const txt = e.textContent.trim();
        return txt === 'Create Alert' && window.getComputedStyle(e).cursor === 'pointer';
    });
    if (t) { t.click(); return 'clicked:' + t.tagName; }
    return 'not_found';
}
"""

SAVE_ALERT_JS = """
() => {
    // Try all elements with 'Save' text
    const all = Array.from(document.querySelectorAll('button, div, span, a'));
    for (const el of all) {
        const txt = el.textContent.trim().toLowerCase();
        if ((txt === 'save alert' || txt === 'save') && el.offsetParent !== null) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                el.click();
                return 'saved:' + el.tagName + ':' + el.textContent.trim();
            }
        }
    }
    // Return all visible buttons for debug
    const btns = Array.from(document.querySelectorAll('button')).filter(b => b.offsetParent !== null);
    return 'not_found. visible_btns=' + btns.map(b => b.textContent.trim().substring(0,20)).join('|');
}
"""

async def process(page, strat, idx):
    wh_url = BASE + strat["wid"]
    print(f"\n[{idx+1}/10] {strat['name']}")
    
    await page.goto(strat["url"], timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(6000)
    
    # Click Create Alert
    r = await page.evaluate(CLICK_ALERT_JS)
    print(f"  Create Alert: {r}")
    await page.wait_for_timeout(2000)
    
    # Fill webhook
    try:
        wh = page.locator('input[name="webhook_url"]').first
        await wh.click(timeout=3000)
        await wh.fill(wh_url)
        print(f"  Webhook: filled")
    except Exception as e:
        print(f"  Webhook err: {e}")
        return False
    
    await page.wait_for_timeout(500)
    
    # Try Save
    r2 = await page.evaluate(SAVE_ALERT_JS)
    print(f"  Save: {r2}")
    saved = r2.startswith("saved:")
    
    if not saved:
        # Screenshot to see what we're looking at
        await page.screenshot(path=f"C:/temp/chartink/debug_{idx+1}.png")
    
    await page.wait_for_timeout(2000)
    return saved

async def main():
    results = []
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        ctx = await b.new_context(viewport={"width":1440,"height":900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await ctx.new_page()
        
        # Login
        await page.goto("https://chartink.com/login")
        await page.wait_for_load_state("networkidle")
        await page.fill("#login-email", "ashish.sharma14@gmail.com")
        await page.fill("#login-password", "BlockTrade5$")
        await page.click("button.primary-button")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        print(f"Login: {page.url}")
        
        # Debug first one
        s = STRATEGIES[0]
        await page.goto(s["url"])
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(6000)
        
        r = await page.evaluate(CLICK_ALERT_JS)
        print(f"Create Alert: {r}")
        await page.wait_for_timeout(2000)
        
        wh = page.locator('input[name="webhook_url"]').first
        await wh.click(timeout=3000)
        await wh.fill(BASE + s["wid"])
        await page.wait_for_timeout(1000)
        
        # Get ALL elements with text 'Save' or 'save alert'
        debug = await page.evaluate("""
            () => {
                const all = Array.from(document.querySelectorAll('*'));
                const found = all.filter(e => {
                    const t = e.textContent.trim().toLowerCase();
                    return (t === 'save alert' || t === 'save' || t === 'save alert') && e.children.length <= 1;
                }).map(e => ({
                    tag: e.tagName,
                    text: e.textContent.trim(),
                    visible: e.offsetParent !== null,
                    cls: e.className.substring(0,60),
                    rect: e.getBoundingClientRect()
                }));
                return found;
            }
        """)
        print(f"\nElements with Save text: {len(debug)}")
        for d in debug:
            print(f"  {d['tag']} vis={d['visible']} text={d['text']} cls={d['cls'][:50]}")
        
        await page.screenshot(path="C:/temp/chartink/save_debug.png")
        await b.close()

asyncio.run(main())
