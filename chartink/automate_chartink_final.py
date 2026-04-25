"""
ChartInk Automation FINAL — Based on real UI understanding
Existing alerts: 4 active (darvas box, buy 100% accuracy, NKS best buy, VCP swing)
We need to: 
1. Get all alert details (webhook URLs, scan IDs)
2. Create 10 new alerts with our webhook URLs
Flow: /screener/{scan_id} -> "Create Alert" button -> fill webhook URL
"""
import asyncio, os, json, re
from playwright.async_api import async_playwright

os.makedirs("C:/temp/chartink", exist_ok=True)

LOGIN = "ashish.sharma14@gmail.com"
PASSWORD = "BlockTrade5$"
BASE_WEBHOOK = "https://openalgo.cryptogyani.com/chartink/webhook/"

STRATEGIES = [
    {"name": "CI EMA Golden Cross Daily",   "webhook_id": "3b91b063-b985-4014-a3cb-f5ea39c9b5a8"},
    {"name": "CI RSI Oversold Bounce",      "webhook_id": "8c5becfe-cd44-429e-9bff-191625015a7a"},
    {"name": "CI Breakout 52W High",        "webhook_id": "9d8e3da7-1c6a-4261-a0c9-45887721f20e"},
    {"name": "CI MACD Bullish Crossover",   "webhook_id": "09b9b950-bb35-4332-8e6d-14fb3ad4a649"},
    {"name": "CI Supertrend Buy",           "webhook_id": "c4fb5731-9e53-498d-9283-0122b1d87b07"},
    {"name": "CI Volume Breakout",          "webhook_id": "78ef3583-7a9e-4d09-81a1-c27c83204511"},
    {"name": "CI BB Squeeze Breakout",      "webhook_id": "0eac56c8-8ea8-4c26-b700-665bd6e2fe92"},
    {"name": "CI CryptoGyani Momentum",     "webhook_id": "c519cd72-2671-4d4d-96bc-b6c4136fc6a3"},
    {"name": "CI Intraday OBV Trend",       "webhook_id": "89a7980f-0492-4dba-828d-bfb2cbf9d492"},
    {"name": "CI ADX Strong Trend",         "webhook_id": "0fce8e4d-4cec-4e27-81f9-344712c80ec4"},
]

# ChartInk conditions in their native format (from the screener textarea #comment)
STRATEGY_CONDITIONS = {
    "CI EMA Golden Cross Daily": "( {cash} ( weekly ( [0]ema( [0]close,50 ) < [0]ema( [0]close,200 ) AND [1]ema( [1]close,50 ) >= [1]ema( [1]close,200 ) ) ) )",
    "CI RSI Oversold Bounce":    "( {cash} ( latest rsi( latest close,14 ) < 30 AND latest rsi( latest close,14 ) > [1]rsi( [1]close,14 ) ) )",
    "CI Breakout 52W High":      "( {cash} ( latest high = max( 52,latest high ) ) )",
    "CI MACD Bullish Crossover": "( {cash} ( [0]macd line( 26,12,9 ) > [0]macd signal( 26,12,9 ) AND [1]macd line( 26,12,9 ) <= [1]macd signal( 26,12,9 ) ) )",
    "CI Supertrend Buy":         "( {cash} ( [0]1 day supertrend( 7,3 ) = 1 AND [1]1 day supertrend( 7,3 ) = -1 ) )",
    "CI Volume Breakout":        "( {cash} ( latest volume > 2 * latest sma( latest volume,20 ) AND latest close > [1]high ) )",
    "CI BB Squeeze Breakout":    "( {cash} ( latest close > latest upper bollinger band( 20,2 ) AND [1]close <= [1]upper bollinger band( 20,2 ) ) )",
    "CI CryptoGyani Momentum":   "( {cash} ( latest rsi( latest close,14 ) > 60 AND latest ema( latest close,20 ) > latest ema( latest close,50 ) AND latest close > latest ema( latest close,200 ) ) )",
    "CI Intraday OBV Trend":     "( {cash} ( latest close > latest sma( latest close,20 ) AND latest volume > latest sma( latest volume,10 ) ) )",
    "CI ADX Strong Trend":       "( {cash} ( latest adx( 14 ) > 25 AND latest plus di( 14 ) > latest minus di( 14 ) AND [1]plus di( 14 ) <= [1]minus di( 14 ) ) )",
}

async def login(page):
    await page.goto("https://chartink.com/login", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.fill('#login-email', LOGIN)
    await page.fill('#login-password', PASSWORD)
    await page.click('button.primary-button')
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    return "login" not in page.url.lower()

async def get_alert_details(page):
    """Get details of existing 4 alerts by clicking each one"""
    print("Getting existing alert details...")
    await page.goto("https://chartink.com/alert_dashboard", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    
    # Get all alert links
    alert_links = await page.locator('a[href*="alert"]').all()
    alerts = []
    for link in alert_links:
        try:
            href = await link.get_attribute("href")
            txt = await link.inner_text()
            if href and '/alert' in href and txt.strip():
                alerts.append({"name": txt.strip(), "url": "https://chartink.com" + href if href.startswith('/') else href})
        except: pass
    
    print(f"Found {len(alerts)} alert links: {[a['name'] for a in alerts]}")
    return alerts

async def click_alert_and_inspect(page, alert_url, alert_name):
    """Click an alert to see its details and webhook config"""
    print(f"\nInspecting alert: {alert_name}")
    await page.goto(alert_url, timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    await page.screenshot(path=f"C:/temp/chartink/alert_detail_{alert_name[:20].replace(' ','_')}.png")
    
    url = page.url
    print(f"  URL: {url}")
    
    # Get form inputs
    inputs = await page.locator('input:visible').all()
    for inp in inputs:
        try:
            t = await inp.get_attribute("type")
            n = await inp.get_attribute("name")
            i = await inp.get_attribute("id")
            v = await inp.get_attribute("value")
            ph = await inp.get_attribute("placeholder")
            print(f"  INPUT t={t} n={n} id={i} ph={ph} val={str(v)[:80] if v else ''}")
        except: pass

async def create_scan_and_alert(page, strat, idx):
    """Create a new scan and immediately set a webhook alert"""
    print(f"\n[{idx+1}/10] Creating: {strat['name']}")
    webhook_url = BASE_WEBHOOK + strat["webhook_id"]
    condition = STRATEGY_CONDITIONS[strat["name"]]
    
    # Step 1: Go to /screener to create new scan
    await page.goto("https://chartink.com/screener", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    # The scan title (atlas-input) - there are 3, first one is the scan name
    # From inspector: class="atlas-input pl-1 !text-input !py-0 font-..."
    name_inputs = await page.locator('input.atlas-input').all()
    print(f"  Name inputs: {len(name_inputs)}")
    if name_inputs:
        try:
            # The scan name appears to be the first atlas-input
            first_input = name_inputs[0]
            await first_input.triple_click()
            await first_input.fill(strat["name"])
            print(f"  Name: filled '{strat['name']}'")
        except Exception as e:
            print(f"  Name fill err: {e}")
    
    # Step 2: Paste condition into the textarea
    # There are 2 textareas: first is the main AI prompt, second is "Prompt filters"
    # The main condition textarea has name="comment"
    try:
        textarea = page.locator('#comment, textarea[name="comment"]').first
        if await textarea.is_visible(timeout=3000):
            await textarea.triple_click()
            await textarea.fill(condition)
            print(f"  Condition: filled")
    except Exception as e:
        print(f"  Condition fill err: {e}")
    
    # Step 3: Run the scan 
    try:
        run_btn = page.locator('button:has-text("Run Scan")').first
        if await run_btn.is_visible(timeout=3000):
            await run_btn.click()
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            print(f"  Run Scan: clicked -> {page.url}")
    except Exception as e:
        print(f"  Run Scan err: {e}")
    
    await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_ran.png")
    
    # Step 4: Save (More -> Save)
    # Look for "More" button with a copy/save icon
    scan_saved = False
    scan_url = page.url
    
    try:
        more_btn = page.locator('button:has-text("More")').first
        await more_btn.wait_for(state="visible", timeout=5000)
        await more_btn.click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_more.png")
        
        # Look for save in dropdown
        for save_text in ["Save", "Save Scan", "Save as", "Save Copy"]:
            try:
                save_el = page.locator(f'button:has-text("{save_text}"), a:has-text("{save_text}")').first
                if await save_el.is_visible(timeout=1500):
                    await save_el.click()
                    await page.wait_for_timeout(2000)
                    scan_url = page.url
                    scan_saved = True
                    print(f"  Saved -> {scan_url}")
                    break
            except: pass
    except Exception as e:
        print(f"  More/Save err: {e}")
    
    await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_saved.png")
    
    # Step 5: Create Alert
    alert_set = False
    try:
        alert_btn = page.locator('button:has-text("Create Alert")').first
        await alert_btn.wait_for(state="visible", timeout=5000)
        await alert_btn.click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_alert_modal.png")
        print("  Create Alert clicked")
        
        # Fill webhook URL in modal
        for sel in ['input[type="url"]', 'input[placeholder*="webhook" i]',
                    'input[placeholder*="http" i]', '#webhook_url', 'input[name="webhook_url"]']:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=2000):
                    await el.fill(webhook_url)
                    print(f"  Webhook filled via {sel}: {webhook_url}")
                    alert_set = True
                    break
            except: pass
        
        # Submit alert form
        for sel in ['button:has-text("Save Alert")', 'button:has-text("Create")',
                    'button:has-text("Save")', 'button[type="submit"]']:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=2000):
                    await el.click()
                    await page.wait_for_timeout(2000)
                    print(f"  Alert submitted via {sel}")
                    break
            except: pass
            
    except Exception as e:
        print(f"  Alert creation err: {e}")
    
    await page.screenshot(path=f"C:/temp/chartink/scan_{idx+1:02d}_done.png")
    
    return {
        "name": strat["name"],
        "scan_saved": scan_saved,
        "alert_set": alert_set,
        "scan_url": scan_url,
        "webhook_url": webhook_url
    }

async def inspect_create_alert_modal(page):
    """Inspect what the Create Alert modal looks like"""
    await page.goto("https://chartink.com/screener", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    # Click Create Alert directly from /screener page
    try:
        btn = page.locator('button:has-text("Create Alert")').first
        await btn.wait_for(state="visible", timeout=5000)
        await btn.click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path="C:/temp/chartink/create_alert_modal.png")
        print("Create Alert modal opened")
        
        # Dump modal HTML
        modal_html = await page.locator('[role="dialog"], .modal, .popup, .alert-modal, [class*="modal"]').first.inner_html()
        print(f"Modal HTML (500 chars): {modal_html[:500]}")
        
        inputs = await page.locator('input:visible').all()
        print(f"Inputs in modal: {len(inputs)}")
        for inp in inputs:
            try:
                t = await inp.get_attribute("type")
                n = await inp.get_attribute("name")
                i = await inp.get_attribute("id")
                ph = await inp.get_attribute("placeholder")
                print(f"  t={t} n={n} id={i} ph={ph}")
            except: pass
        
        buttons = await page.locator('button:visible').all()
        print("Buttons visible:")
        for b in buttons:
            try: print(f"  {await b.inner_text()}")
            except: pass
            
    except Exception as e:
        print(f"Modal inspect error: {e}")
        await page.screenshot(path="C:/temp/chartink/create_alert_fail.png")

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
        
        # First inspect the Create Alert modal
        await inspect_create_alert_modal(page)
        
        # Also check existing alert details
        alerts = await get_alert_details(page)
        if alerts:
            await click_alert_and_inspect(page, alerts[0]["url"], alerts[0]["name"])
        
        await browser.close()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
