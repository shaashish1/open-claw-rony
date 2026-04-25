import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page(viewport={"width":1400,"height":900})
        page.set_default_timeout(30000)
        
        # Load with domcontentloaded (faster)
        await page.goto("https://dashboard.itgyani.com/ops", wait_until="domcontentloaded")
        await asyncio.sleep(6)  # wait for JS + API calls
        
        # Header check
        title = await page.title()
        print(f"Title: {title}")
        
        # Check key elements exist
        for sel, label in [
            ("#tab-agents .grid", "Agents grid"),
            ("#k-strat", "Strategy KPI"),
            ("#k-ci", "ChartInk KPI"),
            (".nav-tab", "Nav tabs"),
        ]:
            el = page.locator(sel).first
            count = await page.locator(sel).count()
            print(f"  {label}: {'OK' if count > 0 else 'MISSING'} ({count})")
        
        # Screenshot top
        await page.screenshot(path="C:/temp/dashboard_qa/v6_top.png")
        
        # Scroll agents
        await page.evaluate("window.scrollTo(0,300)")
        await asyncio.sleep(1)
        await page.screenshot(path="C:/temp/dashboard_qa/v6_agents.png")
        
        # Sprint tab
        await page.locator("text=Sprint").click()
        await asyncio.sleep(4)
        await page.screenshot(path="C:/temp/dashboard_qa/v6_sprint.png")
        
        # Systems tab
        await page.locator("text=Systems").click()
        await asyncio.sleep(2)
        await page.screenshot(path="C:/temp/dashboard_qa/v6_systems.png")
        
        # Check sprint content
        sprint_text = await page.locator("#col-todo").inner_text()
        print(f"Sprint TO DO items: {len(sprint_text.split('IT-')) - 1} issues")
        
        print("All screenshots saved to C:/temp/dashboard_qa/")
        await b.close()

asyncio.run(main())
