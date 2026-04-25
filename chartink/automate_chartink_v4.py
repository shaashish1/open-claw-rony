"""
ChartInk Automation v4 — Full flow based on actual UI
- Login -> Dashboard shows existing scans
- "Create a new scanner" -> /screener -> build scan visually OR paste raw condition
- After saving, set alert via Alerts tab -> webhook
"""
import asyncio, os, json, re
from playwright.async_api import async_playwright

os.makedirs("C:/temp/chartink", exist_ok=True)

LOGIN = "ashish.sharma14@gmail.com"
PASSWORD = "BlockTrade5$"
BASE_WEBHOOK = "https://openalgo.cryptogyani.com/chartink/webhook/"

STRATEGIES = [
    {"name": "CI EMA Golden Cross Daily",    "webhook_id": "3b91b063-b985-4014-a3cb-f5ea39c9b5a8",
     "condition": "( {cash} ( weekly ( [0]ema( [0]close,50 ) < [0]ema( [0]close,200 ) AND [1]ema( [1]close,50 ) >= [1]ema( [1]close,200 ) ) ) )"},
    {"name": "CI RSI Oversold Bounce",       "webhook_id": "8c5becfe-cd44-429e-9bff-191625015a7a",
     "condition": "( {cash} ( [0]rsi( [0]close,14 ) < 30 AND [0]rsi( [0]close,14 ) > [1]rsi( [1]close,14 ) ) )"},
    {"name": "CI Breakout 52W High",         "webhook_id": "9d8e3da7-1c6a-4261-a0c9-45887721f20e",
     "condition": "( {cash} ( latest high = max( 52 , latest high ) ) )"},
    {"name": "CI MACD Bullish Crossover",    "webhook_id": "09b9b950-bb35-4332-8e6d-14fb3ad4a649",
     "condition": "( {cash} ( [0]macd line( 26 , 12 , 9 ) > [0]macd signal( 26 , 12 , 9 ) AND [1]macd line( 26 , 12 , 9 ) <= [1]macd signal( 26 , 12 , 9 ) ) )"},
    {"name": "CI Supertrend Buy",            "webhook_id": "c4fb5731-9e53-498d-9283-0122b1d87b07",
     "condition": "( {cash} ( [0]1 minute supertrend( 7 , 3 ) = 1 AND [1]1 minute supertrend( 7 , 3 ) = -1 ) )"},
    {"name": "CI Volume Breakout",           "webhook_id": "78ef3583-7a9e-4d09-81a1-c27c83204511",
     "condition": "( {cash} ( latest volume > 2 * latest sma( latest volume , 20 ) AND latest close > [1]high ) )"},
    {"name": "CI BB Squeeze Breakout",       "webhook_id": "0eac56c8-8ea8-4c26-b700-665bd6e2fe92",
     "condition": "( {cash} ( latest close > latest upper bollinger band( 20 , 2 ) AND [1]close <= [1]upper bollinger band( 20 , 2 ) ) )"},
    {"name": "CI CryptoGyani Momentum",      "webhook_id": "c519cd72-2671-4d4d-96bc-b6c4136fc6a3",
     "condition": "( {cash} ( latest rsi( latest close , 14 ) > 60 AND latest ema( latest close , 20 ) > latest ema( latest close , 50 ) AND latest close > latest ema( latest close , 200 ) ) )"},
    {"name": "CI Intraday OBV Trend",        "webhook_id": "89a7980f-0492-4dba-828d-bfb2cbf9d492",
     "condition": "( {cash} ( latest close > latest sma( latest close , 20 ) AND latest volume > latest sma( latest volume , 10 ) ) )"},
    {"name": "CI ADX Strong Trend",          "webhook_id": "0fce8e4d-4cec-4e27-81f9-344712c80ec4",
     "condition": "( {cash} ( latest adx( 14 ) > 25 AND latest plus di( 14 ) > latest minus di( 14 ) AND [1]plus di( 14 ) <= [1]minus di( 14 ) ) )"},
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

async def explore_screener_new(page):
    """Explore the /screener/new page and find how to paste raw conditions"""
    print("Exploring /screener (new scanner)...")
    await page.goto("https://chartink.com/screener", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    await page.screenshot(path="C:/temp/chartink/screener_new.png")
    print(f"URL: {page.url}")

async def check_alert_dashboard(page):
    """Check the Alerts tab on the dashboard"""
    print("\nChecking Alerts dashboard (/alert_dashboard)...")
    await page.goto("https://chartink.com/alert_dashboard", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    await page.screenshot(path="C:/temp/chartink/alert_dashboard.png")
    
    # Dump inputs/buttons
    inputs = await page.locator('input:visible').all()
    buttons = await page.locator('button:visible').all()
    print(f"Alert page inputs: {len(inputs)}, buttons: {len(buttons)}")
    for b in buttons[:20]:
        try: print(f"  BTN: {await b.inner_text()}")
        except: pass
    
    # Try to find "Create alert" or similar
    html = await page.content()
    # Find webhook mentions
    if 'webhook' in html.lower():
        idx = html.lower().find('webhook')
        print(f"Webhook context: {html[max(0,idx-100):idx+200]}")

async def create_scan_via_copy(page, strat, idx):
    """
    Strategy: Use /screener/copy-{slug} pattern or use the API directly.
    ChartInk uses a specific format for scan conditions.
    Let's try the clipboard approach — paste raw condition into the UI.
    """
    print(f"\n[{idx+1}/10] {strat['name']}")
    
    # Go to /screener to create new
    await page.goto("https://chartink.com/screener", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    
    await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_a.png")
    
    # The condition textarea has name="comment" and id="comment"
    # Try to fill it with our condition
    try:
        textarea = page.locator('textarea[name="comment"]').first
        if await textarea.is_visible(timeout=3000):
            await textarea.fill(strat["condition"])
            print(f"  Condition pasted into textarea")
    except Exception as e:
        print(f"  Textarea error: {e}")
    
    # Click "Run Scan" to execute
    try:
        await page.click('button:has-text("Run Scan")', timeout=5000)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)
        print(f"  Run Scan clicked -> {page.url}")
    except Exception as e:
        print(f"  Run Scan error: {e}")
    
    await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_b_ran.png")
    
    # Now save: look for "More" button -> "Save Scan"
    try:
        more_btn = page.locator('button:has-text("More")').first
        if await more_btn.is_visible(timeout=3000):
            await more_btn.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_c_more.png")
            print("  More menu opened")
            
            # Look for save option in dropdown
            for sel in ['button:has-text("Save")', 'a:has-text("Save")', '[data-action="save"]']:
                try:
                    el = page.locator(sel).first
                    if await el.is_visible(timeout=2000):
                        await el.click()
                        await page.wait_for_timeout(2000)
                        print(f"  Save clicked via {sel}")
                        break
                except: pass
    except Exception as e:
        print(f"  More/Save error: {e}")
    
    # Check for name input after save
    try:
        name_input = page.locator('input[placeholder*="name" i], #scan-name, .scan-name-input').first
        if await name_input.is_visible(timeout=3000):
            await name_input.fill(strat["name"])
            print(f"  Name filled")
    except: pass
    
    await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_d_saved.png")
    final_url = page.url
    print(f"  Final URL: {final_url}")
    
    # Extract scan ID from URL if possible
    m = re.search(r'/screener/(\d+)', final_url)
    scan_id = m.group(1) if m else None
    return scan_id, final_url

async def set_webhook_for_scan(page, scan_url, webhook_url, scan_name):
    """Set webhook alert for a saved scan"""
    print(f"\nSetting webhook for: {scan_name}")
    await page.goto(scan_url, timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    # Click "Create Alert" button 
    alert_clicked = False
    for sel in ['button:has-text("Create Alert")', 'a:has-text("Create Alert")',
                'button:has-text("Alert")', '.create-alert-btn', '[data-alert]']:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=2000):
                await el.click()
                await page.wait_for_timeout(2000)
                alert_clicked = True
                print(f"  Alert btn: {sel}")
                break
        except: pass
    
    await page.screenshot(path=f"C:/temp/chartink/webhook_{scan_name[:15]}.png")
    
    # Fill webhook URL
    for sel in ['input[type="url"]', 'input[placeholder*="webhook" i]',
                'input[placeholder*="http" i]', 'input[name*="webhook" i]']:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=2000):
                await el.fill(webhook_url)
                print(f"  Webhook filled via {sel}")
                break
        except: pass
    
    return alert_clicked

async def inspect_screener_page(page):
    """Deep inspect of the screener page to find save button"""
    await page.goto("https://chartink.com/screener", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    # Check the "More" button dropdown
    try:
        more_btn = page.locator('button:has-text("More")').first
        await more_btn.click(timeout=3000)
        await page.wait_for_timeout(1000)
        await page.screenshot(path="C:/temp/chartink/more_dropdown.png")
        
        # Get all visible items
        items = await page.locator(':visible').all()
        print("Items after More click:")
        for item in items:
            try:
                tag = await item.evaluate("el => el.tagName")
                txt = await item.inner_text()
                if txt.strip() and tag in ['BUTTON', 'A', 'LI', 'SPAN']:
                    print(f"  {tag}: {txt[:50]}")
            except: pass
    except Exception as e:
        print(f"More btn: {e}")
    
    # Also check the title bar area for scan name input
    # Look for atlas-input class
    atlas_inputs = await page.locator('.atlas-input, input.atlas-input').all()
    print(f"Atlas inputs: {len(atlas_inputs)}")
    for ai in atlas_inputs:
        try:
            v = await ai.get_attribute("value")
            ph = await ai.get_attribute("placeholder")
            visible = await ai.is_visible()
            print(f"  atlas-input: val={v} ph={ph} visible={visible}")
        except: pass

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()
        
        ok = await login(page)
        if not ok:
            print("LOGIN FAILED")
            await browser.close()
            return
        print("Logged in OK")
        
        await check_alert_dashboard(page)
        await inspect_screener_page(page)
        
        await browser.close()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
