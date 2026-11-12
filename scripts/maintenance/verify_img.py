# -*- coding: utf-8 -*-
"""验证图片相同的问题offer"""
import asyncio, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'crawler')

from alibaba1688_spider import _extract_detail, _RE_SKU_PROPS, _RE_IMAGE_LIST

async def check():
    from playwright.async_api import async_playwright
    
    # 验证图片相同的offer
    test_offers = [
        ("1016651947224", "收纳盒-3个SKU图片相同"),
        ("1036501204912", "蚊香盒-5个SKU图片相同"),
    ]
    
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp("http://localhost:9223")
    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    
    for oid, desc in test_offers:
        url = f"https://detail.1688.com/offer/{oid}.html"
        print(f"\n{'='*60}")
        print(f"验证: {desc}")
        print(f"URL: {url}")
        
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            html = await page.content()
            
            # 检查skuProps
            m_props = _RE_SKU_PROPS.search(html)
            if m_props:
                props = json.loads(m_props.group(1))
                print(f"\n  skuProps:")
                for prop in props:
                    print(f"    prop: {prop.get('name','')}")
                    for v in prop.get('value', []):
                        img = v.get('imageUrl', '')
                        print(f"      {v.get('name','')}: imageUrl={img[:80] if img else 'EMPTY'}")
            else:
                print("  skuProps: NOT FOUND")
            
            # 检查imageList（主图列表）
            m_imgs = _RE_IMAGE_LIST.search(html)
            if m_imgs:
                imgs = json.loads(m_imgs.group(1))
                print(f"\n  imageList ({len(imgs)}张):")
                for img in imgs[:5]:
                    print(f"    {img.get('fullPathImageURI','')[:70]}")
            
            # extract结果
            items = _extract_detail(html, oid, 8)
            print(f"\n  _extract_detail ({len(items)}条):")
            for item in items:
                print(f"    {item['name'][:35]} | price={item['price']} | img={item['image_url'][:65] if item['image_url'] else 'EMPTY'}")
            
            # 截图
            await page.screenshot(path=f"C:/Users/Administrator/.qclaw/workspace-agent-b550e3e8/verify_{oid}.png", full_page=False)
            print(f"\n  截图已保存")
            
        except Exception as e:
            print(f"  错误: {e}")
        finally:
            await page.close()
    
    await p.stop()

asyncio.run(check())
