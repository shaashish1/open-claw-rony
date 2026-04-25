import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page(viewport={"width":1400,"height":900})
        await page.goto("https://dashboard.itgyani.com/ops", wait_until="domcontentloaded")
        await asyncio.sleep(5)
        # Click sprint nav tab precisely
        await page.locator(".nav-tab", has_text="Sprint").click()
        await asyncio.sleep(4)
        await page.screenshot(path="C:/temp/dashboard_qa/v6_sprint.png")
        # Systems
        await page.locator(".nav-tab", has_text="Systems").click()
        await asyncio.sleep(2)
        await page.screenshot(path="C:/temp/dashboard_qa/v6_systems.png")
        # Tasks
        await page.locator(".nav-tab", has_text="Tasks").click()
        await asyncio.sleep(1)
        await page.screenshot(path="C:/temp/dashboard_qa/v6_tasks.png")
        print("Done")
        await b.close()

asyncio.run(main())
