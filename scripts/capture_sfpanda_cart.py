# -*- coding: utf-8 -*-
import asyncio, sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        async def on_request(request):
            if "cart" in request.url:
                print(f"[REQ] {request.method} {request.url}")
                print(f"      Headers: {request.headers}")
                print(f"      PostData: {request.post_data}")
        
        async def on_response(response):
            if "cart" in response.url:
                print(f"[RESP] {response.status} {response.url}")
                try:
                    text = await response.text()
                    print(f"       Body: {text[:200]}")
                except:
                    pass

        page.on("request", on_request)
        page.on("response", on_response)

        print("Navigating to https://sfpanda.com.ar/productos...")
        await page.goto("https://sfpanda.com.ar/productos", wait_until="networkidle")
        
        # Find first add button
        btn = await page.query_selector("article.product-block button.product-block__button, form[action*='cart'] button, input[type='submit']")
        if btn:
            print("Found button, clicking...")
            await btn.click()
            await page.wait_for_timeout(3000)
        else:
            print("No button found. Checking form...")
            card = await page.query_selector("article.product-block")
            if card:
                print(await card.inner_html())
        await browser.close()

asyncio.run(main())
