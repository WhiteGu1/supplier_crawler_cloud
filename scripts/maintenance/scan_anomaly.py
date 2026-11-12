# -*- coding: utf-8 -*-
"""扫描DB中可能图片/价格异常的SKU"""
import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')
import mysql.connector
from collections import defaultdict

conn = mysql.connector.connect(
    host="localhost", port=3306, user="root", password="admin123",
    database="supplier_crawler", charset="utf8mb4", use_pure=True,
)
cur = conn.cursor(dictionary=True)

# 1. 同一offer下所有SKU图片相同（应该是不同的）
cur.execute("""
    SELECT product_url, name, sku, price, image_url
    FROM products WHERE supplier_id=8 AND product_url LIKE '%?sku=%'
    ORDER BY product_url
""")
rows = cur.fetchall()

by_offer = defaultdict(list)
for r in rows:
    m = re.search(r'/offer/(\d+)', r['product_url'])
    if m:
        by_offer[m.group(1)].append(r)

print("=== 多SKU但图片全部相同的offer（可能图片错误）===")
suspect_img = []
for oid, items in by_offer.items():
    if len(items) < 2:
        continue
    imgs = [i['image_url'] for i in items]
    if len(set(imgs)) == 1 and imgs[0]:  # 所有图片相同
        suspect_img.append((oid, items))

for oid, items in suspect_img[:10]:
    print(f"\n  offer={oid} ({len(items)}个SKU) 所有图片相同:")
    print(f"    img={items[0]['image_url'][:80]}")
    for i in items[:3]:
        print(f"    {i['name'][:40]} | price={i['price']}")

# 2. 多SKU但价格全部相同且为0
print(f"\n=== 多SKU但价格全为0的offer ===")
for oid, items in by_offer.items():
    if len(items) < 2:
        continue
    if all(float(i['price']) == 0 for i in items):
        print(f"  offer={oid} ({len(items)}个SKU) price全部=0")
        for i in items[:2]:
            print(f"    {i['name'][:40]} | img={i['image_url'][:60] if i['image_url'] else 'EMPTY'}")

# 3. 图片为空
print(f"\n=== 图片为空的SKU ===")
cur.execute("SELECT COUNT(*) as c FROM products WHERE supplier_id=8 AND (image_url IS NULL OR image_url='')")
empty_img = cur.fetchone()
print(f"  共 {empty_img['c']} 条")

# 4. 图片URL不含alicdn.com的
cur.execute("SELECT product_url, name, sku, image_url FROM products WHERE supplier_id=8 AND image_url!='' AND image_url NOT LIKE '%alicdn%' LIMIT 10")
bad_img = cur.fetchall()
if bad_img:
    print(f"\n=== 图片URL非alicdn的 ===")
    for r in bad_img:
        print(f"  {r['name'][:30]} | img={r['image_url'][:70]}")

# 5. 同一offer下不同SKU价格全相同，但skuMap里实际有不同价格的情况
# 需要抽样检查
print(f"\n=== 统计 ===")
print(f"  总多SKU offer数: {len(by_offer)}")
print(f"  图片全相同: {len(suspect_img)}")
same_price = sum(1 for items in by_offer.values() if len(set(float(i['price']) for i in items)) == 1)
diff_price = sum(1 for items in by_offer.values() if len(set(float(i['price']) for i in items)) > 1)
print(f"  价格全相同: {same_price}")
print(f"  价格有不同: {diff_price}")

cur.close()
conn.close()
