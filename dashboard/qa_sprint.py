"""Quick screenshot of the sprint section"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto("https://dashboard.itgyani.com/ops", wait_until="networkidle", timeout=20000)
        await asyncio.sleep(4)  # let Jira API load
        # scroll to sprint section
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
        await asyncio.sleep(1)
        await page.screenshot(path="C:/temp/dashboard_qa/sprint_section.png")
        # also full page
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path="C:/temp/dashboard_qa/ops_full.png", full_page=True)
        print("Done")
        await browser.close()

asyncio.run(main())
