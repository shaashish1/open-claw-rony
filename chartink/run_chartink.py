"""
ChartInk Final Automation — Correct flow:
1. Login
2. For each strategy:
   a. Go to /screener/create
   b. Fill scan name (atlas-input)
   c. Add conditions via the condition builder
   d. Run Scan
   e. Click "Create Alert" -> fill webhook URL -> save
"""
import asyncio, os, json
from playwright.async_api import async_playwright

os.makedirs("C:/temp/chartink", exist_ok=True)

LOGIN = "ashish.sharma14@gmail.com"
PASSWORD = "BlockTrade5$"
BASE = "https://openalgo.cryptogyani.com/chartink/webhook/"

STRATEGIES = [
    {"name": "CI EMA Golden Cross",    "id": "3b91b063-b985-4014-a3cb-f5ea39c9b5a8"},
    {"name": "CI RSI Oversold Bounce", "id": "8c5becfe-cd44-429e-9bff-191625015a7a"},
    {"name": "CI 52W Breakout",        "id": "9d8e3da7-1c6a-4261-a0c9-45887721f20e"},
    {"name": "CI MACD Cross",          "id": "09b9b950-bb35-4332-8e6d-14fb3ad4a649"},
    {"name": "CI Supertrend Buy",      "id": "c4fb5731-9e53-498d-9283-0122b1d87b07"},
    {"name": "CI Volume Breakout",     "id": "78ef3583-7a9e-4d09-81a1-c27c83204511"},
    {"name": "CI BB Breakout",         "id": "0eac56c8-8ea8-4c26-b700-665bd6e2fe92"},
    {"name": "CI CG Momentum",         "id": "c519cd72-2671-4d4d-96bc-b6c4136fc6a3"},
    {"name": "CI OBV Trend",           "id": "89a7980f-0492-4dba-828d-bfb2cbf9d492"},
    {"name": "CI ADX Trend",           "id": "0fce8e4d-4cec-4e27-81f9-344712c80ec4"},
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

async def inspect_alert_modal(page):
    """Click Create Alert on saved scan and inspect the modal"""
    # Use the darvas scan which we know has conditions
    await page.goto("https://chartink.com/screener/copy-darvas-box-breakout-r-111", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    # Click Create Alert
    try:
        await page.click('button:has-text("Create Alert")', timeout=5000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path="C:/temp/chartink/alert_modal.png")
        print("Alert modal opened")
        
        # Dump all visible HTML in dialog
        dialog_html = ""
        for sel in ['[role="dialog"]', '.modal', '[class*="modal"]', '[class*="dialog"]', '[class*="alert"]']:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=1000):
                    dialog_html = await el.inner_html()
                    print(f"Dialog via {sel}: {dialog_html[:800]}")
                    break
            except: pass
        
        if not dialog_html:
            # Dump new visible inputs/buttons
            inputs = await page.locator('input:visible').all()
            print(f"Visible inputs after modal: {len(inputs)}")
            for inp in inputs:
                try:
                    t = await inp.get_attribute("type")
                    n = await inp.get_attribute("name")
                    i = await inp.get_attribute("id")
                    ph = await inp.get_attribute("placeholder")
                    v = await inp.get_attribute("value")
                    print(f"  t={t} n={n} id={i} ph={ph} val={str(v)[:60] if v else ''}")
                except: pass
            
            selects = await page.locator('select:visible').all()
            print(f"Selects: {len(selects)}")
            
            buttons = await page.locator('button:visible').all()
            print("Buttons:")
            for b in buttons:
                try: print(f"  {await b.inner_text()}")
                except: pass
                
    except Exception as e:
        print(f"Alert modal error: {e}")
        await page.screenshot(path="C:/temp/chartink/alert_modal_fail.png")

async def create_alert_for_scan(page, scan_url, strat_name, webhook_id, idx):
    """Open a scan, click Create Alert, fill webhook URL"""
    webhook_url = BASE + webhook_id
    print(f"\n[{idx+1}/10] Alert for: {strat_name}")
    
    await page.goto(scan_url, timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    # If scan hasn't run, click Run Scan first
    try:
        run_btn = page.locator('button:has-text("Run Scan")').first
        if await run_btn.is_visible(timeout=2000):
            await run_btn.click()
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
    except: pass
    
    # Click Create Alert
    try:
        await page.click('button:has-text("Create Alert")', timeout=5000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"C:/temp/chartink/alert_{idx+1:02d}_modal.png")
        
        # Fill webhook URL
        webhook_filled = False
        for sel in ['input[placeholder*="http" i]', 'input[type="url"]', 
                    'input[placeholder*="webhook" i]', 'input[name*="webhook" i]',
                    '#webhook_url', 'input[placeholder*="URL" i]']:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=1500):
                    await el.fill(webhook_url)
                    webhook_filled = True
                    print(f"  Webhook via {sel}")
                    break
            except: pass
        
        # Save
        for sel in ['button:has-text("Save Alert")', 'button:has-text("Set Alert")',
                    'button:has-text("Create Alert")', 'button:has-text("Save")',
                    'button[type="submit"]']:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=2000):
                    await el.click()
                    await page.wait_for_timeout(2000)
                    print(f"  Submitted via {sel}")
                    break
            except: pass
        
        await page.screenshot(path=f"C:/temp/chartink/alert_{idx+1:02d}_done.png")
        return webhook_filled
        
    except Exception as e:
        print(f"  Error: {e}")
        return False

async def create_new_scan_with_alert(page, strat, idx):
    """Create a new scan from scratch using the copy of an existing scan as template"""
    webhook_url = BASE + strat["id"]
    print(f"\n[{idx+1}/10] Creating new: {strat['name']}")
    
    # Use /screener with a copy of darvas as starting point and modify name
    await page.goto("https://chartink.com/screener/copy-darvas-box-breakout-r-111", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    # Change the scan name (atlas-input fields at top)
    atlas = await page.locator('input.atlas-input').all()
    print(f"  Atlas inputs: {len(atlas)}")
    if atlas:
        try:
            await atlas[0].triple_click()
            await atlas[0].type(strat["name"], delay=50)
            print(f"  Name set: {strat['name']}")
        except Exception as e:
            print(f"  Name err: {e}")
    
    # Save as new scan via More -> Save Copy
    try:
        await page.click('button:has-text("More")', timeout=5000)
        await page.wait_for_timeout(1000)
        await page.screenshot(path=f"C:/temp/chartink/new_{idx+1:02d}_more.png")
        
        for save_text in ["Save Copy", "Save as copy", "Save Scan", "Save"]:
            try:
                el = page.locator(f'button:has-text("{save_text}"), a:has-text("{save_text}")').first
                if await el.is_visible(timeout=1500):
                    await el.click()
                    await page.wait_for_timeout(2000)
                    print(f"  Saved via: {save_text} -> {page.url}")
                    break
            except: pass
    except Exception as e:
        print(f"  More/Save err: {e}")
    
    # Now create alert
    await page.wait_for_timeout(1000)
    try:
        await page.click('button:has-text("Create Alert")', timeout=5000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"C:/temp/chartink/new_{idx+1:02d}_alert.png")
        
        # Fill webhook
        for sel in ['input[placeholder*="http" i]', 'input[type="url"]',
                    'input[placeholder*="webhook" i]', 'input[placeholder*="URL" i]',
                    '#webhook_url']:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=1500):
                    await el.fill(webhook_url)
                    print(f"  Webhook set: {webhook_url[:60]}...")
                    break
            except: pass
        
        # Submit
        for sel in ['button:has-text("Save")', 'button[type="submit"]', 'button:has-text("Create")']:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=2000):
                    await el.click()
                    await page.wait_for_timeout(2000)
                    print(f"  Alert saved")
                    break
            except: pass
            
        await page.screenshot(path=f"C:/temp/chartink/new_{idx+1:02d}_done.png")
        return True
    except Exception as e:
        print(f"  Alert err: {e}")
        return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width":1440,"height":900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0")
        page = await ctx.new_page()
        
        ok = await login(page)
        print(f"Login: {'OK' if ok else 'FAILED'}")
        if not ok:
            await browser.close()
            return
        
        # First inspect the alert modal
        await inspect_alert_modal(page)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
