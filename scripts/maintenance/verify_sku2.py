# -*- coding: utf-8 -*-
"""验证多SKU详情页：检查图片和价格是否正确"""
import asyncio, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'crawler')

from alibaba1688_spider import _extract_detail, _RE_SUBJECT, _RE_MIN_PRICE, _RE_SKU_PROPS, _RE_SKU_MAP, _RE_IMAGE_LIST

async def check():
    from playwright.async_api import async_playwright
    
    # 选一个多SKU的offer来验证
    offer_id = "728815950887"  # 防烫垫，有9个SKU
    url = f"https://detail.1688.com/offer/{offer_id}.html"
    print(f"验证offer: {offer_id}")
    print(f"URL: {url}")
    
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp("http://localhost:9223")
    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await context.new_page()
    
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(3000)
    html = await page.content()
    
    # 1. 检查skuProps里的imageUrl
    m_props = _RE_SKU_PROPS.search(html)
    if m_props:
        props = json.loads(m_props.group(1))
        print(f"\n=== skuProps ===")
        for prop in props:
            print(f"  prop name: {prop.get('name','')}")
            for v in prop.get('value', []):
                img = v.get('imageUrl', '')
                print(f"    SKU: {v.get('name','')} -> image: {img[:80] if img else 'EMPTY'}")
    
    # 2. 检查skuMap里的price
    m_map = _RE_SKU_MAP.search(html)
    if m_map:
        sku_map = json.loads(m_map.group(1))
        print(f"\n=== skuMap ({len(sku_map)}条) ===")
        for entry in sku_map:
            print(f"  specAttrs={entry.get('specAttrs','')} -> price={entry.get('price','?')}, discountPrice={entry.get('discountPrice','?')}")
    else:
        print("\n=== skuMap NOT FOUND ===")
    
    # 3. 检查页面上的实际价格（通过JS提取）
    print(f"\n=== 页面JS实时价格 ===")
    try:
        # 尝试获取页面上SKU选择器的实际价格
        sku_prices = await page.evaluate("""() => {
            const result = [];
            // 方法1: 查找sku价格元素
            const skuItems = document.querySelectorAll('.sku-item, .obj-leveltwo-color, [class*="sku"]');
            skuItems.forEach(item => {
                const name = item.getAttribute('data-sku-config') || item.getAttribute('title') || item.textContent.trim().substring(0, 30);
                const priceEl = item.querySelector('.price, [class*="price"]') || item.closest('tr,li,div').querySelector('.price, [class*="price"]');
                const price = priceEl ? priceEl.textContent.trim() : '';
                const imgEl = item.querySelector('img');
                const img = imgEl ? imgEl.src : '';
                if (name) result.push({name, price, img: img.substring(0, 80)});
            });
            return result;
        }""")
        for sp in sku_prices[:10]:
            print(f"  {sp['name'][:30]} -> price={sp['price']}, img={sp['img']}")
    except Exception as e:
        print(f"  JS提取失败: {e}")
    
    # 4. 尝试从window.context.result提取（1688详情页的完整数据）
    print(f"\n=== window.context.result ===")
    try:
        ctx_data = await page.evaluate("""() => {
            if (window.context && window.context.result) {
                const r = window.context.result;
                return {
                    subject: r.subject,
                    offerMinPrice: r.offerMinPrice,
                    skuProps: r.skuProps ? 'exists' : 'missing',
                    skuMap: r.skuMap ? 'exists' : 'missing',
                    imageList: r.imageList ? r.imageList.length + ' images' : 'missing',
                    // 检查skuProps的第一个prop的value
                    firstSkuProp: r.skuProps && r.skuProps[0] ? {
                        name: r.skuProps[0].name,
                        values: r.skuProps[0].value ? r.skuProps[0].value.map(v => ({
                            name: v.name,
                            imageUrl: v.imageUrl ? v.imageUrl.substring(0, 80) : 'EMPTY'
                        })) : []
                    } : null,
                    // 检查skuMap前3条
                    firstSkuMap: r.skuMap ? r.skuMap.slice(0, 3).map(e => ({
                        specAttrs: e.specAttrs,
                        price: e.price,
                        discountPrice: e.discountPrice
                    })) : null
                };
            }
            return 'window.context.result not found';
        }""")
        print(json.dumps(ctx_data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"  提取失败: {e}")
    
    # 5. 对比_extract_detail的结果
    items = _extract_detail(html, offer_id, 8)
    print(f"\n=== _extract_detail结果 ({len(items)}条) ===")
    for item in items:
        print(f"  name={item['name'][:50]}")
        print(f"    sku={item['sku']}, price={item['price']}, img={item['image_url'][:70] if item['image_url'] else 'EMPTY'}")
    
    # 6. 截图对比
    await page.screenshot(path=f"D:/projects/supplier_crawler/verify_{offer_id}.png", full_page=False)
    print(f"\n截图已保存: verify_{offer_id}.png")
    
    await page.close()
    await p.stop()

asyncio.run(check())
