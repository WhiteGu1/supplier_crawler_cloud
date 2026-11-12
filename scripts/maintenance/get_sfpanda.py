# -*- coding: utf-8 -*-
"""获取sfpanda未分类有图商品列表"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT id, image_local, name FROM products
    WHERE supplier_id=1 AND (category IS NULL OR category='')
    AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
""")
rows = cur.fetchall()

items = []
for pid, img, name in rows:
    if img.startswith('./'):
        full = 'D:/projects/supplier_crawler/' + img[2:]
    elif img.startswith('images/'):
        full = 'D:/projects/supplier_crawler/' + img
    else:
        full = img
    items.append({"id": pid, "img": full, "name": name})

with open('sfpanda_remaining.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"sfpanda: {len(items)} 条有图未分类")
print(f"ID范围: {items[0]['id']} ~ {items[-1]['id']}")

# Show first and last 5
print("\n前5条:")
for it in items[:5]:
    print(f"  {it['id']}\t{it['name'][:40]}\t{it['img']}")
print("\n后5条:")
for it in items[-5:]:
    print(f"  {it['id']}\t{it['name'][:40]}\t{it['img']}")

# Count batches needed
batches = (len(items) + 9) // 10
print(f"\n需要 {batches} 批（每批10张），{batches//5} 波（每波5批并行）")

conn.close()
