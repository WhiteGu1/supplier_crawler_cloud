# -*- coding: utf-8 -*-
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

result = {}
for sid, name in [(6, 'osa'), (7, 'sfpanda')]:
    cur.execute("""SELECT id, image_local FROM products
        WHERE supplier_id=%s AND (category IS NULL OR category='')
        AND image_local IS NOT NULL AND image_local != ''
        ORDER BY id""", (sid,))
    rows = cur.fetchall()
    items = []
    for pid, img in rows:
        if img.startswith('./'):
            full = 'D:/projects/supplier_crawler/' + img[2:]
        elif img.startswith('images/'):
            full = 'D:/projects/supplier_crawler/' + img
        else:
            full = img
        items.append({"id": pid, "img": full})
    result[name] = items
    print(f"{name}: {len(items)} 条有图未分类")

# Save to JSON
with open('osa_sfpanda_remaining.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n总计: {len(result['osa']) + len(result['sfpanda'])} 条")
print("已保存到 osa_sfpanda_remaining.json")

# Print osa items (only 38)
print("\n=== osa 商品列表 ===")
for item in result['osa']:
    print(f"  {item['id']}\t{item['img']}")

conn.close()
