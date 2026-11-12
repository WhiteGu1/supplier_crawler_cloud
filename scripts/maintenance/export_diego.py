# -*- coding: utf-8 -*-
"""导出Diego全量商品用于AI重分类"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT id, name, image_local, category FROM products
    WHERE supplier_id=2 AND category IS NOT NULL AND category != ''
    AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
""")
rows = cur.fetchall()

items = []
for pid, name, img, cat in rows:
    if img.startswith('./'):
        full = 'D:/projects/supplier_crawler/' + img[2:]
    elif img.startswith('images/'):
        full = 'D:/projects/supplier_crawler/' + img
    else:
        full = img
    items.append({"id": pid, "name": name, "img": full, "old_cat": cat})

with open('diego_reclassify.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"Diego: {len(items)} 条")
print(f"ID范围: {items[0]['id']} ~ {items[-1]['id']}")

# 分类分布
from collections import Counter
cats = Counter(it['old_cat'] for it in items)
print(f"\n现有分类分布:")
for cat, cnt in cats.most_common():
    print(f"  {cat}: {cnt}")

# 分批
batches = [items[i:i+10] for i in range(0, len(items), 10)]
print(f"\n共 {len(batches)} 批")

# 保存批次信息
batch_info = []
for i, batch in enumerate(batches):
    batch_info.append({
        "batch": i,
        "ids": [it['id'] for it in batch],
        "names": [it['name'] for it in batch],
        "imgs": [it['img'] for it in batch],
        "old_cats": [it['old_cat'] for it in batch],
    })

with open('diego_batches.json', 'w', encoding='utf-8') as f:
    json.dump(batch_info, f, ensure_ascii=False, indent=2)

print(f"批次信息已保存到 diego_batches.json")
print(f"\n前3批预览:")
for i in range(min(3, len(batches))):
    print(f"\nBatch {i}:")
    for it in batches[i]:
        print(f"  {it['id']}\t{it['name'][:30]}\t{it['old_cat']}")

conn.close()
