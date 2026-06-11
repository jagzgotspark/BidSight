import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

URL = "https://eprocure.gov.in/eprocure/app?page=FrontEndTendersByOrganisation&service=page"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await Stealth().apply_stealth_async(page)

        print("Opening CPPP latest active tenders...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(8)

        print(f"Title: {await page.title()}")
        content = await page.content()
        print(f"HTML length: {len(content)}")

        content = await page.content()
        has_captcha = "captcha" in content.lower()
        print(f"CAPTCHA present: {has_captcha}")

        rows = await page.query_selector_all("table.list_table tr")
        print(f"list_table rows: {len(rows)}")
        for i, row in enumerate(rows[:15]):
            text = (await row.inner_text()).strip().replace("\n", " | ")
            print(f"  [{i}] {text[:180]}")
            print("\n--- Organisation links ---")
        org_links = await page.query_selector_all("table.list_table a")
        print(f"Total links: {len(org_links)}")
        for link in org_links[:15]:
            href = await link.get_attribute("href")
            text = (await link.inner_text()).strip()
            if text and len(text) > 2:
                print(f"  {text[:50]} -> {href}")

        await asyncio.sleep(15)  # keep browser open to inspect
        await browser.close()

asyncio.run(main())