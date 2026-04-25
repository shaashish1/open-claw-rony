import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page(viewport={"width":1400,"height":900})
        await page.goto("https://dashboard.itgyani.com/ops", wait_until="domcontentloaded")
        # Wait longer for all API calls to complete
        await asyncio.sleep(15)
        await page.screenshot(path="C:/temp/dashboard_qa/final_agents.png")
        
        await page.locator(".nav-tab", has_text="Sprint").click()
        await asyncio.sleep(10)  # Jira API takes ~5-8s
        await page.screenshot(path="C:/temp/dashboard_qa/final_sprint.png")
        
        await page.locator(".nav-tab", has_text="Systems").click()
        await asyncio.sleep(3)
        await page.screenshot(path="C:/temp/dashboard_qa/final_systems.png")
        
        # Check sprint content
        try:
            todo = await page.locator("#col-todo").inner_text()
            prog = await page.locator("#col-prog").inner_text()
            done = await page.locator("#col-done").inner_text()
            print(f"TODO: {len(todo.split('IT-'))-1} items")
            print(f"IN PROG: {len(prog.split('IT-'))-1} items")  
            print(f"DONE: {len(done.split('IT-'))-1} items")
        except Exception as e:
            print(f"Sprint check error: {e}")
        
        print("Done - screenshots saved")
        await b.close()

asyncio.run(main())
