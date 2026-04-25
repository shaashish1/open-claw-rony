import asyncio
from playwright.async_api import async_playwright
import os

os.makedirs("C:/temp", exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        await page.goto("https://chartink.com/login", timeout=30000)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)
        
        await page.screenshot(path="C:/temp/ci_login.png")
        
        # Dump HTML structure around forms
        html = await page.content()
        # Find form section
        start = html.find('<form')
        if start == -1:
            start = html.find('login')
        print("Form HTML snippet:")
        print(html[max(0,start):start+3000])
        
        # Check inputs
        inputs = await page.locator('input').all()
        print(f"\nInputs found: {len(inputs)}")
        for inp in inputs:
            try:
                t = await inp.get_attribute("type")
                n = await inp.get_attribute("name")
                pid = await inp.get_attribute("id")
                ph = await inp.get_attribute("placeholder")
                print(f"  type={t} name={n} id={pid} placeholder={ph}")
            except: pass
        
        buttons = await page.locator('button, input[type="submit"]').all()
        print(f"\nButtons found: {len(buttons)}")
        for b in buttons:
            try:
                txt = await b.inner_text()
                t = await b.get_attribute("type")
                print(f"  type={t} text={txt[:50]}")
            except: pass
        
        await browser.close()

asyncio.run(main())
