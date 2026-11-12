# -*- coding: utf-8 -*-
import asyncio, sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        page.on('console', lambda msg: print('BROWSER CONSOLE:', msg.text))
        page.on('request', lambda r: print('[REQ]', r.method, r.url, r.post_data[:100] if r.post_data else ''))
        page.on('response', lambda r: print('[RESP]', r.status, r.url))
        await page.goto('https://www.sfpanda.com.ar/productos', wait_until='domcontentloaded')
        print("Page loaded. Executing Jumpseller.addProductToCart...")
        res = await page.evaluate('''() => {
            return new Promise((resolve) => {
                Jumpseller.addProductToCart('37700711', 2, {}, {
                    callback: function(cart) {
                        resolve(cart);
                    }
                });
            });
        }''')
        print('RESULT:', res)
        # Check cart URL
        await page.goto('https://www.sfpanda.com.ar/cart')
        print('Cart page loaded! URL:', page.url)
        content = await page.content()
        print('Is 37700711 in cart?', '37700711' in content)
        await b.close()

asyncio.run(main())
