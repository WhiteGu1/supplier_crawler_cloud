# -*- coding: utf-8 -*-
"""找价格不同的多SKU商品验证"""
import asyncio, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'crawler')

import mysql.connector

# 找同一个offer下不同价格的SKU
conn = mysql.connector.connect(
    host="localhost", port=3306, user="root", password="admin123",
    database="supplier_crawler", charset="utf8mb4", use_pure=True,
)
cur = conn.cursor(dictionary=True)
cur.execute("""
    SELECT product_url, name, sku, price, image_url
    FROM products WHERE supplier_id=8
    AND product_url LIKE '%?sku=%'
    ORDER BY product_url
""")
all_rows = cur.fetchall()

# 按offer_id分组，找价格不同的
from collections import defaultdict
groups = defaultdict(list)
for r in all_rows:
    m = re.search(r'/offer/(\d+)', r['product_url'])
    if m:
        groups[m.group(1)].append(r)

target_offers = []
for oid, items in groups.items():
    prices = set(float(i['price']) for i in items)
    if len(prices) > 1 and len(items) >= 3:
        target_offers.append((oid, items))

print(f"找到 {len(target_offers)} 个价格不同的多SKU offer")
# 取前2个验证
for oid, items in target_offers[:2]:
    print(f"\n{'='*60}")
    print(f"offer_id: {oid}, SKU数: {len(items)}, 价格列表: {[i['price'] for i in items]}")
    for i in items:
        print(f"  DB: {i['name'][:40]} | sku={i['sku']} | price={i['price']} | img={i['image_url'][:70] if i['image_url'] else 'EMPTY'}")

cur.close()
conn.close()

# 验证这些offer
async def check():
    from playwright.async_api import async_playwright
    from alibaba1688_spider import _extract_detail, _RE_SKU_PROPS, _RE_SKU_MAP, _RE_IMAGE_LIST
    
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp("http://localhost:9223")
    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    
    for oid, db_items in target_offers[:2]:
        url = f"https://detail.1688.com/offer/{oid}.html"
        print(f"\n{'='*60}")
        print(f"打开: {url}")
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            html = await page.content()
            
            # skuProps
            m_props = _RE_SKU_PROPS.search(html)
            if m_props:
                props = json.loads(m_props.group(1))
                print(f"\n--- skuProps ---")
                for prop in props:
                    for v in prop.get('value', []):
                        img = v.get('imageUrl', '')
                        print(f"  {v.get('name','')}: img={img[:70] if img else 'EMPTY'}")
            
            # skuMap
            m_map = _RE_SKU_MAP.search(html)
            if m_map:
                sku_map = json.loads(m_map.group(1))
                print(f"\n--- skuMap ({len(sku_map)}条) ---")
                for e in sku_map:
                    print(f"  {e.get('specAttrs','')}: price={e.get('price','?')}, discount={e.get('discountPrice','?')}")
            
            # 页面实时价格
            print(f"\n--- 页面显示的SKU价格 ---")
            real_prices = await page.evaluate("""() => {
                const items = document.querySelectorAll('[class*="sku-item"], [class*="obj-level"], .sku-item, li[data-sku-config]');
                const result = [];
                document.querySelectorAll('li, div').forEach(el => {
                    const txt = el.textContent;
                    if (txt && txt.includes('¥') && txt.length < 100) {
                        const name = el.getAttribute('title') || el.getAttribute('data-sku-config') || '';
                        if (name) result.push({name: name.substring(0,30), text: txt.trim().substring(0,60)});
                    }
                });
                return result.slice(0, 15);
            }""")
            for rp in real_prices:
                print(f"  {rp['name']}: {rp['text']}")
            
            # _extract_detail结果
            items = _extract_detail(html, oid, 8)
            print(f"\n--- _extract_detail ({len(items)}条) ---")
            for item in items:
                print(f"  {item['name'][:35]} | price={item['price']} | img={item['image_url'][:65] if item['image_url'] else 'EMPTY'}")
            
            # 对比DB
            print(f"\n--- DB中存的数据 ---")
            for di in db_items:
                print(f"  {di['name'][:35]} | price={di['price']} | img={di['image_url'][:65] if di['image_url'] else 'EMPTY'}")
            
            await page.screenshot(path=f"D:/projects/supplier_crawler/verify_{oid}.png", full_page=False)
            
        except Exception as e:
            print(f"错误: {e}")
        finally:
            await page.close()
    
    await p.stop()

asyncio.run(check())
