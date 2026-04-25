"""
ChartInk WORKING Automation — div-based buttons
Run Scan / Save Scan / Create Alert are DIVs not BUTTONs
"""
import asyncio, os, json
from playwright.async_api import async_playwright

os.makedirs("C:/temp/chartink", exist_ok=True)

LOGIN = "ashish.sharma14@gmail.com"
PASSWORD = "BlockTrade5$"
BASE = "https://openalgo.cryptogyani.com/chartink/webhook/"

STRATEGIES = [
    {"name": "CI EMA Golden Cross",    "wid": "3b91b063-b985-4014-a3cb-f5ea39c9b5a8"},
    {"name": "CI RSI Oversold Bounce", "wid": "8c5becfe-cd44-429e-9bff-191625015a7a"},
    {"name": "CI 52W Breakout",        "wid": "9d8e3da7-1c6a-4261-a0c9-45887721f20e"},
    {"name": "CI MACD Cross",          "wid": "09b9b950-bb35-4332-8e6d-14fb3ad4a649"},
    {"name": "CI Supertrend Buy",      "wid": "c4fb5731-9e53-498d-9283-0122b1d87b07"},
    {"name": "CI Volume Breakout",     "wid": "78ef3583-7a9e-4d09-81a1-c27c83204511"},
    {"name": "CI BB Breakout",         "wid": "0eac56c8-8ea8-4c26-b700-665bd6e2fe92"},
    {"name": "CI CG Momentum",         "wid": "c519cd72-2671-4d4d-96bc-b6c4136fc6a3"},
    {"name": "CI OBV Trend",           "wid": "89a7980f-0492-4dba-828d-bfb2cbf9d492"},
    {"name": "CI ADX Trend",           "wid": "0fce8e4d-4cec-4e27-81f9-344712c80ec4"},
]

# Base scan: copy of Darvas Box (2 simple conditions)
BASE_SCAN_URL = "https://chartink.com/screener/copy-darvas-box-breakout-r-111"

async def login(page):
    await page.goto("https://chartink.com/login", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.fill('#login-email', LOGIN)
    await page.fill('#login-password', PASSWORD)
    await page.click('button.primary-button')
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    return "login" not in page.url.lower()

async def click_action_div(page, text, wait_ms=2000):
    """Click a div-based action button by text content"""
    result = await page.evaluate(f'''
        () => {{
            const divs = Array.from(document.querySelectorAll('div[class*="cursor-pointer"]'));
            const target = divs.find(d => d.textContent.trim() === "{text}" || d.textContent.includes("{text}"));
            if (target) {{
                target.click();
                return "clicked: " + target.textContent.trim().substring(0,50);
            }}
            // Try spans too
            const spans = Array.from(document.querySelectorAll('span'));
            const spanTarget = spans.find(s => s.textContent.trim() === "{text}");
            if (spanTarget) {{
                spanTarget.parentElement.click();
                return "clicked via span: " + spanTarget.textContent.trim();
            }}
            return "not found";
        }}
    ''')
    await page.wait_for_timeout(wait_ms)
    return result

async def get_scan_name_input(page):
    """Get the scan name atlas-input field"""
    inputs = await page.locator('input.atlas-input').all()
    for inp in inputs:
        try:
            vis = await inp.is_visible()
            if vis:
                return inp
        except: pass
    return None

async def process_one_strategy(page, strat, idx, save_screenshot=True):
    """Full flow: load template, rename, save, set alert webhook"""
    webhook_url = BASE + strat["wid"]
    print(f"\n[{idx+1}/10] {strat['name']}")

    # Load the base scan
    await page.goto(BASE_SCAN_URL, timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(6000)  # Wait for Vue to fully render

    # 1. Rename the scan
    name_inp = await get_scan_name_input(page)
    if name_inp:
        await name_inp.triple_click()
        await name_inp.fill(strat["name"])
        print(f"  Name set: {strat['name']}")
    else:
        print("  Name input not found")

    # 2. Click "Save Scan" via JS div click
    save_result = await click_action_div(page, "Save Scan", 3000)
    print(f"  Save Scan: {save_result}")
    
    if save_screenshot:
        await page.screenshot(path=f"C:/temp/chartink/s{idx+1:02d}_saved.png")

    new_url = page.url
    print(f"  URL after save: {new_url}")

    # 3. Click "Create Alert" 
    alert_result = await click_action_div(page, "Create Alert", 2000)
    print(f"  Create Alert: {alert_result}")
    
    if save_screenshot:
        await page.screenshot(path=f"C:/temp/chartink/s{idx+1:02d}_alert.png")

    # 4. Fill webhook in alert modal
    webhook_filled = False
    # Look for URL input in modal
    await page.wait_for_timeout(1000)
    
    # Try to find webhook input by evaluating all inputs
    inputs_info = await page.evaluate('''
        () => Array.from(document.querySelectorAll('input')).map(i => ({
            type: i.type, name: i.name, id: i.id, placeholder: i.placeholder,
            visible: i.offsetParent !== null, value: i.value.substring(0,50)
        }))
    ''')
    print(f"  Inputs after alert click: {len(inputs_info)}")
    for inp in inputs_info:
        if inp.get('visible'):
            print(f"    {inp}")

    # Try filling webhook URL
    for sel in ['input[type="url"]', 'input[placeholder*="http" i]', 
                'input[placeholder*="webhook" i]', 'input[placeholder*="URL" i]',
                'input[name*="webhook" i]', '#webhook', 'input[name="url"]']:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1000):
                await el.fill(webhook_url)
                webhook_filled = True
                print(f"  Webhook filled via {sel}")
                break
        except: pass

    # Submit the alert form
    if webhook_filled:
        save_res = await click_action_div(page, "Save Alert", 2000)
        print(f"  Save Alert: {save_res}")
        # Also try button
        for sel in ['button:has-text("Save")', 'button:has-text("Create")', 'button[type="submit"]']:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=1000):
                    await el.click()
                    print(f"  Submitted via {sel}")
                    break
            except: pass

    if save_screenshot:
        await page.screenshot(path=f"C:/temp/chartink/s{idx+1:02d}_done.png")

    return {
        "name": strat["name"],
        "url": new_url,
        "webhook": webhook_url,
        "saved": "not found" not in save_result,
        "alert_clicked": "not found" not in alert_result,
        "webhook_filled": webhook_filled
    }

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
        
        # Process all 10 strategies
        for i, strat in enumerate(STRATEGIES):
            try:
                result = await process_one_strategy(page, strat, i)
                results.append(result)
            except Exception as e:
                print(f"  ERROR: {e}")
                results.append({"name": strat["name"], "error": str(e)})
            await page.wait_for_timeout(1000)
        
        with open("C:/temp/chartink/final_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        await browser.close()
    
    print("\n=== FINAL RESULTS ===")
    ok_count = 0
    for r in results:
        status = "OK" if r.get("webhook_filled") else ("PARTIAL" if r.get("alert_clicked") else "FAIL")
        if status == "OK": ok_count += 1
        print(f"  [{status}] {r['name']}")
    print(f"\n{ok_count}/10 webhooks configured")

if __name__ == "__main__":
    asyncio.run(main())
