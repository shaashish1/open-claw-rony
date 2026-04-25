"""
ChartInk Automation — Create 10 scans and set webhooks
"""
import asyncio, os, json
from playwright.async_api import async_playwright

os.makedirs("C:/temp/chartink", exist_ok=True)

LOGIN = "ashish.sharma14@gmail.com"
PASSWORD = "BlockTrade5$"
BASE_WEBHOOK = "https://openalgo.cryptogyani.com/chartink/webhook/"

STRATEGIES = [
    {
        "name": "CI EMA Golden Cross Daily",
        "condition": "( {cash} ( weekly ( [0]EMA( [0]C,50 ) < [0]EMA( [0]C,200 ) AND [1]EMA( [1]C,50 ) >= [1]EMA( [1]C,200 ) ) ) )",
        "webhook": BASE_WEBHOOK + "3b91b063-b985-4014-a3cb-f5ea39c9b5a8",
    },
    {
        "name": "CI RSI Oversold Bounce",
        "condition": "( {cash} ( [0]RSI( [0]C,14 ) < 30 AND [0]RSI( [0]C,14 ) > [1]RSI( [1]C,14 ) ) )",
        "webhook": BASE_WEBHOOK + "8c5becfe-cd44-429e-9bff-191625015a7a",
    },
    {
        "name": "CI Breakout 52W High",
        "condition": "( {cash} ( latest high = Max( 52 , latest high ) ) )",
        "webhook": BASE_WEBHOOK + "9d8e3da7-1c6a-4261-a0c9-45887721f20e",
    },
    {
        "name": "CI MACD Bullish Crossover",
        "condition": "( {cash} ( [0]MACD( [0]C,12,26,9 ) > [0]MACDsignal( [0]C,12,26,9 ) AND [1]MACD( [1]C,12,26,9 ) <= [1]MACDsignal( [1]C,12,26,9 ) ) )",
        "webhook": BASE_WEBHOOK + "09b9b950-bb35-4332-8e6d-14fb3ad4a649",
    },
    {
        "name": "CI Supertrend Buy",
        "condition": "( {cash} ( [0]Supertrend( [0]H,[0]L,[0]C,7,3 ) = 1 AND [1]Supertrend( [1]H,[1]L,[1]C,7,3 ) = -1 ) )",
        "webhook": BASE_WEBHOOK + "c4fb5731-9e53-498d-9283-0122b1d87b07",
    },
    {
        "name": "CI Volume Breakout",
        "condition": "( {cash} ( [0]volume > 2 * [0]SMA( [0]volume,20 ) AND [0]C > [1]H ) )",
        "webhook": BASE_WEBHOOK + "78ef3583-7a9e-4d09-81a1-c27c83204511",
    },
    {
        "name": "CI BB Squeeze Breakout",
        "condition": "( {cash} ( [0]C > [0]BBand-Upper( [0]C,20,2,1 ) AND [1]C <= [1]BBand-Upper( [1]C,20,2,1 ) ) )",
        "webhook": BASE_WEBHOOK + "0eac56c8-8ea8-4c26-b700-665bd6e2fe92",
    },
    {
        "name": "CI CryptoGyani Momentum",
        "condition": "( {cash} ( [0]RSI( [0]C,14 ) > 60 AND [0]EMA( [0]C,20 ) > [0]EMA( [0]C,50 ) AND [0]C > [0]EMA( [0]C,200 ) ) )",
        "webhook": BASE_WEBHOOK + "c519cd72-2671-4d4d-96bc-b6c4136fc6a3",
    },
    {
        "name": "CI Intraday OBV Trend",
        "condition": "( {cash} ( [0]OBV( [0]C,[0]volume ) > [0]EMA( [0]OBV( [0]C,[0]volume ),20 ) AND [0]C > [0]VWAP ) )",
        "webhook": BASE_WEBHOOK + "89a7980f-0492-4dba-828d-bfb2cbf9d492",
    },
    {
        "name": "CI ADX Strong Trend",
        "condition": "( {cash} ( [0]ADX( [0]H,[0]L,[0]C,14 ) > 25 AND [0]PLUSDI( [0]H,[0]L,[0]C,14 ) > [0]MINUSDI( [0]H,[0]L,[0]C,14 ) AND [1]PLUSDI( [1]H,[1]L,[1]C,14 ) <= [1]MINUSDI( [1]H,[1]L,[1]C,14 ) ) )",
        "webhook": BASE_WEBHOOK + "0fce8e4d-4cec-4e27-81f9-344712c80ec4",
    },
]

async def login(page):
    print("Logging in to ChartInk...")
    await page.goto("https://chartink.com/login", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)

    await page.fill('#login-email', LOGIN)
    await page.fill('#login-password', PASSWORD)
    await page.screenshot(path="C:/temp/chartink/01_before_login.png")
    
    # Click the "Log in" button (primary-button class)
    await page.click('button.primary-button')
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)

    url = page.url
    await page.screenshot(path="C:/temp/chartink/02_after_login.png")
    print(f"After login URL: {url}")

    if "login" in url.lower():
        # Check for error messages
        body = await page.inner_text('body')
        print(f"Login error? Body snippet: {body[:300]}")
        return False
    print("✅ Logged in successfully!")
    return True

async def explore_screener_create(page):
    """Understand the scan creation UI"""
    print("\nExploring scan creation page...")
    await page.goto("https://chartink.com/screener/create", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    await page.screenshot(path="C:/temp/chartink/03_create_page.png")
    
    url = page.url
    title = await page.title()
    print(f"Create URL: {url}, Title: {title}")
    
    # Dump inputs and textareas
    inputs = await page.locator('input:not([type="hidden"])').all()
    textareas = await page.locator('textarea').all()
    
    print(f"Inputs: {len(inputs)}, Textareas: {len(textareas)}")
    for el in inputs:
        try:
            t = await el.get_attribute("type")
            n = await el.get_attribute("name")
            i = await el.get_attribute("id")
            ph = await el.get_attribute("placeholder")
            cls = await el.get_attribute("class")
            print(f"  INPUT type={t} name={n} id={i} placeholder={ph} class={cls[:40] if cls else ''}")
        except: pass
    for el in textareas:
        try:
            n = await el.get_attribute("name")
            i = await el.get_attribute("id")
            ph = await el.get_attribute("placeholder")
            print(f"  TEXTAREA name={n} id={i} placeholder={ph}")
        except: pass
    
    # Buttons
    btns = await page.locator('button').all()
    print(f"Buttons: {len(btns)}")
    for b in btns:
        try:
            txt = await b.inner_text()
            cls = await b.get_attribute("class")
            print(f"  BTN text={txt[:40]} class={cls[:40] if cls else ''}")
        except: pass
    
    return url

async def try_api_scan_create(session_cookies, strat):
    """Try to create scan via ChartInk's own API endpoints"""
    import urllib.request, urllib.parse
    
    # ChartInk uses CSRF token — get it first
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in session_cookies])
    
    headers = {
        "Cookie": cookie_str,
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://chartink.com/screener/create",
    }
    
    print(f"  Trying API create for: {strat['name']}")
    return None

async def create_scan_via_ui(page, strat, idx):
    """Create scan using the actual UI"""
    print(f"\n[{idx+1}/10] Creating: {strat['name']}")
    
    await page.goto("https://chartink.com/screener/create", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_a_loaded.png")

    # Try to fill scan name — common selectors
    name_filled = False
    for sel in ['#scan_name', 'input[name="scan_name"]', 'input[placeholder*="name" i]',
                'input[placeholder*="scan" i]', '.scan-title input', '#name']:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1500):
                await el.fill(strat["name"])
                name_filled = True
                print(f"  ✅ Name via {sel}")
                break
        except: pass

    # Try condition area
    cond_filled = False
    for sel in ['textarea[name="condition"]', '#condition', 'textarea[placeholder*="condition" i]',
                '.condition-editor textarea', 'textarea', '#scan_condition']:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1500):
                await el.fill(strat["condition"])
                cond_filled = True
                print(f"  ✅ Condition via {sel}")
                break
        except: pass

    await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_b_filled.png")

    # Try save
    saved = False
    for sel in ['button:has-text("Save Scan")', 'button:has-text("Save")',
                'button:has-text("Create")', 'input[value="Save"]',
                '.btn-success', '.save-scan-btn']:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1500):
                await el.click()
                saved = True
                print(f"  ✅ Save via {sel}")
                break
        except: pass

    await page.wait_for_timeout(3000)
    await page.wait_for_load_state("networkidle")
    final_url = page.url
    await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_c_saved.png")

    print(f"  name_filled={name_filled} cond_filled={cond_filled} saved={saved}")
    print(f"  URL after: {final_url}")
    return {"name": strat["name"], "url": final_url, "name_filled": name_filled,
            "cond_filled": cond_filled, "saved": saved}

async def main():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
        page = await ctx.new_page()

        # Login
        ok = await login(page)
        if not ok:
            print("❌ LOGIN FAILED — check screenshots in C:/temp/chartink/")
            await browser.close()
            return

        # Explore create page first
        await explore_screener_create(page)

        # Create all 10 scans
        for i, strat in enumerate(STRATEGIES):
            try:
                r = await create_scan_via_ui(page, strat, i)
                results.append(r)
            except Exception as e:
                print(f"  ❌ Error on {strat['name']}: {e}")
                await page.screenshot(path=f"C:/temp/chartink/scan_{i+1:02d}_error.png")
                results.append({"name": strat["name"], "error": str(e)})
            await page.wait_for_timeout(500)

        # Save results
        with open("C:/temp/chartink/results.json", "w") as f:
            json.dump(results, f, indent=2)

        await browser.close()

    print("\n\n=== SUMMARY ===")
    for r in results:
        status = "✅" if r.get("saved") else "❌"
        print(f"{status} {r['name']}: {r.get('url', r.get('error', 'unknown'))}")
    print("\nScreenshots: C:/temp/chartink/")

if __name__ == "__main__":
    asyncio.run(main())
