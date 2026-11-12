"""验证多SKU商品详情页解析：对比提取结果与页面实际数据"""
import asyncio, sys, json, re
sys.path.insert(0, 'crawler')
sys.path.insert(0, 'database')

import mysql.connector
from mysql.connector import pooling

# 连数据库找几个多SKU的offer
conn = mysql.connector.connect(
    host="localhost", port=3306, user="root", password="admin123",
    database="supplier_crawler", charset="utf8mb4", use_pure=True,
)
cur = conn.cursor(dictionary=True)
cur.execute("""
    SELECT product_url, name, sku, price, image_url
    FROM products WHERE supplier_id=8 AND sku LIKE '%_%' AND sku != ''
    AND product_url LIKE '%?sku=%'
    LIMIT 5
""")
samples = cur.fetchall()
print("=== 数据库中的多SKU商品样本 ===")
for s in samples:
    print(f"  URL: {s['product_url'][:70]}")
    print(f"  name: {s['name'][:60]}")
    print(f"  sku: {s['sku']}")
    print(f"  price: {s['price']}")
    print(f"  image: {s['image_url'][:80]}")
    print()

# 提取offer_id
offer_ids = set()
for s in samples:
    m = re.search(r'/offer/(\d+)', s['product_url'])
    if m:
        offer_ids.add(m.group(1))

print(f"=== 需要验证的offer_ids: {offer_ids} ===\n")

cur.close()
conn.close()

# 用playwright连接CDP打开详情页，获取HTML
async def check():
    from playwright.async_api import async_playwright
    import os
    sys.stdout.reconfigure(encoding='utf-8')
    
    p = await async_playwright().start()
    cdp_url = "http://localhost:9223"
    try:
        browser = await p.chromium.connect_over_cdp(cdp_url)
        print(f"CDP连接成功: {cdp_url}")
    except Exception as e:
        print(f"CDP连接失败: {e}")
        await p.stop()
        return

    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    
    from alibaba1688_spider import _extract_detail, _RE_SUBJECT, _RE_MIN_PRICE, _RE_SKU_PROPS, _RE_SKU_MAP, _RE_IMAGE_LIST
    
    for offer_id in offer_ids:
        url = f"https://detail.1688.com/offer/{offer_id}.html"
        print(f"\n{'='*60}")
        print(f"打开详情页: {url}")
        
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            
            # 检查关键数据
            m_subj = _RE_SUBJECT.search(html)
            m_price = _RE_MIN_PRICE.search(html)
            m_props = _RE_SKU_PROPS.search(html)
            m_map = _RE_SKU_MAP.search(html)
            m_imgs = _RE_IMAGE_LIST.search(html)
            
            print(f"  subject: {m_subj.group(1)[:50] if m_subj else 'NOT FOUND'}")
            print(f"  offerMinPrice: {m_price.group(1) if m_price else 'NOT FOUND'}")
            print(f"  skuProps found: {'YES' if m_props else 'NO'}")
            print(f"  skuMap found: {'YES' if m_map else 'NO'}")
            print(f"  imageList found: {'YES' if m_imgs else 'NO'}")
            
            if m_props:
                try:
                    props = json.loads(m_props.group(1))
                    print(f"\n  skuProps内容:")
                    for p_idx, prop in enumerate(props):
                        print(f"    prop[{p_idx}]: name={prop.get('name','')}")
                        for v in prop.get('value', []):
                            img = v.get('imageUrl', '')
                            print(f"      value: name={v.get('name','')}, imageUrl={img[:60] if img else 'EMPTY'}")
                except Exception as e:
                    print(f"  skuProps解析失败: {e}")
                    print(f"  raw: {m_props.group(1)[:200]}")
            
            if m_map:
                try:
                    sku_map = json.loads(m_map.group(1))
                    print(f"\n  skuMap内容 ({len(sku_map)}条):")
                    for entry in sku_map[:5]:
                        print(f"    specAttrs={entry.get('specAttrs','')[:40]}, price={entry.get('price','?')}, discountPrice={entry.get('discountPrice','?')}")
                    if len(sku_map) > 5:
                        print(f"    ... 还有{len(sku_map)-5}条")
                except Exception as e:
                    print(f"  skuMap解析失败: {e}")
                    print(f"  raw: {m_map.group(1)[:200]}")
            
            if m_imgs:
                try:
                    imgs = json.loads(m_imgs.group(1))
                    print(f"\n  imageList ({len(imgs)}张):")
                    for img in imgs[:3]:
                        url1 = img.get('fullPathImageURI','')
                        url2 = img.get('size310x310ImageURI','')
                        print(f"    full={url1[:60]}, 310={url2[:60]}")
                except Exception as e:
                    print(f"  imageList解析失败: {e}")
                    print(f"  raw: {m_imgs.group(1)[:200]}")
            
            # 调用_extract_detail看结果
            items = _extract_detail(html, offer_id, 8)
            print(f"\n  _extract_detail结果 ({len(items)}条):")
            for item in items:
                print(f"    name={item['name'][:40]}, sku={item['sku']}, price={item['price']}, img={item['image_url'][:60] if item['image_url'] else 'EMPTY'}")
            
        except Exception as e:
            print(f"  错误: {e}")
        finally:
            await page.close()
    
    await p.stop()

asyncio.run(check())
