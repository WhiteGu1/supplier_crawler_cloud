import pymysql, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("""
    SELECT id, name, category, image_local 
    FROM products 
    WHERE supplier_id=2 AND is_available=1
    ORDER BY id
""")
rows = cur.fetchall()

results = []
missing_img = 0
for r in rows:
    item = {'id': r['id'], 'name': r['name'], 'cat': r['category']}
    if r['image_local']:
        candidates = [
            os.path.join('images', 'Diego', r['image_local']),
            os.path.join('images', r['image_local']),
            r['image_local']
        ]
        for c in candidates:
            if os.path.exists(c):
                item['img'] = os.path.abspath(c).replace('\\', '/')
                break
        else:
            item['img'] = None
            missing_img += 1
    else:
        item['img'] = None
        missing_img += 1
    results.append(item)

# 写到文件
with open('diego_all_data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Total: {len(results)}, With image: {len(results)-missing_img}, Missing: {missing_img}")
print(f"Data written to diego_all_data.json")
conn.close()
