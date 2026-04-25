"""
ChartInk Automation v3 — Use actual UI buttons
The screener is a visual builder. Strategy:
1. Load /screener/create (which has a pre-existing scan from last session)
2. Click "Create Alert" -> set webhook -> save
For unique scans, use the "More" copy flow per scan

Observation: The page already has a scan loaded with some filters.
We need to understand the full flow for setting a webhook alert.
"""
import asyncio, os, json
from playwright.async_api import async_playwright

os.makedirs("C:/temp/chartink", exist_ok=True)

LOGIN = "ashish.sharma14@gmail.com"
PASSWORD = "BlockTrade5$"
BASE_WEBHOOK = "https://openalgo.cryptogyani.com/chartink/webhook/"

# The scan dashboard shows existing saved scans
# We'll use the "Alerts" button flow from the existing scan dashboard

async def login(page):
    print("Logging in...")
    await page.goto("https://chartink.com/login", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.fill('#login-email', LOGIN)
    await page.fill('#login-password', PASSWORD)
    await page.click('button.primary-button')
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    logged = "login" not in page.url.lower()
    print(f"Login: {'OK' if logged else 'FAILED'} -> {page.url}")
    return logged

async def explore_alert_flow(page):
    """Find how to create a webhook alert"""
    print("\n--- Exploring Alert Flow ---")
    
    # Go to screener create page and click "Create Alert"
    await page.goto("https://chartink.com/screener/create", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    # Click "Create Alert" button
    try:
        await page.click('button:has-text("Create Alert")', timeout=5000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path="C:/temp/chartink/alert_flow_01.png")
        print("Clicked Create Alert")
    except Exception as e:
        print(f"Create Alert not found: {e}")
        await page.screenshot(path="C:/temp/chartink/alert_flow_01_fail.png")
    
    # What appeared?
    url = page.url
    print(f"URL after Create Alert: {url}")
    
    # Get all inputs/selects in modal or new page
    modals = await page.locator('.modal, [role="dialog"], .popup, .alert-form').all()
    print(f"Modals found: {len(modals)}")
    
    inputs = await page.locator('input:visible').all()
    print(f"Visible inputs: {len(inputs)}")
    for inp in inputs:
        try:
            t = await inp.get_attribute("type")
            n = await inp.get_attribute("name") 
            i = await inp.get_attribute("id")
            ph = await inp.get_attribute("placeholder")
            v = await inp.get_attribute("value")
            print(f"  INPUT t={t} n={n} id={i} ph={ph} val={v[:30] if v else ''}")
        except: pass
    
    await page.screenshot(path="C:/temp/chartink/alert_flow_02.png")
    
    # Also check the "Alerts" top nav button
    await page.wait_for_timeout(1000)
    try:
        await page.click('button:has-text("Alerts")', timeout=3000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path="C:/temp/chartink/alert_flow_03_alerts_nav.png")
        print(f"Clicked Alerts nav -> {page.url}")
    except Exception as e:
        print(f"Alerts nav: {e}")
    
    # Check scan dashboard for alerts
    await page.goto("https://chartink.com/scan_dashboard", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    await page.screenshot(path="C:/temp/chartink/dashboard_view.png")
    print(f"Dashboard URL: {page.url}")
    
    # Check what's on dashboard
    buttons = await page.locator('button:visible').all()
    links = await page.locator('a:visible').all()
    print("Dashboard buttons:")
    for b in buttons[:15]:
        try: print(f"  {await b.inner_text()}")
        except: pass
    print("Dashboard links (scan related):")
    for l in links[:20]:
        try:
            txt = await l.inner_text()
            href = await l.get_attribute("href")
            if any(k in str(txt+href).lower() for k in ['scan', 'alert', 'screener', 'create']):
                print(f"  {txt[:40]} -> {href}")
        except: pass

async def get_existing_scans(page):
    """Get list of saved scans from dashboard"""
    await page.goto("https://chartink.com/scan_dashboard", timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    html = await page.content()
    await page.screenshot(path="C:/temp/chartink/dashboard_full.png")
    
    # Try to get scan list via API
    # ChartInk likely has an endpoint like /screener/list or similar
    response = await page.evaluate("""
        async () => {
            try {
                const r = await fetch('/screener/list', {headers: {'X-Requested-With': 'XMLHttpRequest'}});
                return {status: r.status, text: await r.text()};
            } catch(e) { return {error: e.toString()}; }
        }
    """)
    print(f"Screener list API: {str(response)[:500]}")
    
    # Try saved scans endpoint
    response2 = await page.evaluate("""
        async () => {
            try {
                const r = await fetch('/api/user/saved-scans', {headers: {'X-Requested-With': 'XMLHttpRequest'}});
                return {status: r.status, text: await r.text()};
            } catch(e) { return {error: e.toString()}; }
        }
    """)
    print(f"Saved scans API: {str(response2)[:500]}")

    return []

async def create_alert_for_screener(page, screener_url, webhook_url, alert_name):
    """Navigate to a saved screener and set up a webhook alert"""
    print(f"\nSetting alert for: {alert_name}")
    await page.goto(screener_url, timeout=30000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    await page.screenshot(path=f"C:/temp/chartink/alert_{alert_name[:20]}_1.png")
    
    # Click Create Alert
    try:
        await page.click('button:has-text("Create Alert"), a:has-text("Create Alert")', timeout=5000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"C:/temp/chartink/alert_{alert_name[:20]}_2.png")
        print("  Create Alert clicked")
    except Exception as e:
        print(f"  Create Alert not found: {e}")
        return False
    
    # Fill webhook URL if field exists
    webhook_inputs = await page.locator('input[placeholder*="webhook" i], input[name*="webhook" i], input[type="url"]').all()
    for wi in webhook_inputs:
        try:
            if await wi.is_visible(timeout=1000):
                await wi.fill(webhook_url)
                print(f"  Webhook URL filled")
                break
        except: pass
    
    # Submit
    for sel in ['button:has-text("Save")', 'button:has-text("Create")', 'button[type="submit"]']:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1500):
                await el.click()
                print(f"  Saved via {sel}")
                return True
        except: pass
    
    return False

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
            await browser.close()
            return
        
        await explore_alert_flow(page)
        await get_existing_scans(page)
        
        await browser.close()
    print("\nDone! Check C:/temp/chartink/ for screenshots")

if __name__ == "__main__":
    asyncio.run(main())
