import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

URL = "https://eprocure.gov.in/eprocure/app?page=FrontEndTendersByOrganisation&service=page"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await Stealth().apply_stealth_async(page)
        print("Opening org list...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(6)

        # Click the first organisation's tender-count link
        first = await page.query_selector("table.list_table a")
        href = await first.get_attribute("href")
        full_url = "https://eprocure.gov.in" + href
        print(f"Following: {full_url[:90]}...")
        await page.goto(full_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(6)

        content = await page.content()
        print(f"CAPTCHA on drill-down page: {'captcha' in content.lower()}")

        rows = await page.query_selector_all("table.list_table tr")
        print(f"Drill-down list_table rows: {len(rows)}")
        for i, row in enumerate(rows[:12]):
            text = (await row.inner_text()).strip().replace("\n", " | ")
            print(f"  [{i}] {text[:180]}")

        await asyncio.sleep(15)
        await browser.close()

asyncio.run(main())
