import pymysql, json, os, sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("""
    SELECT id, name, image_local 
    FROM products 
    WHERE supplier_id=3 AND (category IS NULL OR category='' OR category='未分类') AND is_available=1
    LIMIT 20
""")
rows = cur.fetchall()

results = []
for r in rows:
    item = {'id': r['id'], 'name': r['name'], 'image_local': r['image_local']}
    if r['image_local']:
        for c in [os.path.join('images','Trapoman',r['image_local']), os.path.join('images',r['image_local']), r['image_local']]:
            if os.path.exists(c):
                item['full_path'] = os.path.abspath(c).replace('\\','/')
                break
    results.append(item)

# 输出 JSON 数组
print(json.dumps(results, ensure_ascii=False, indent=2))
print(f"\n共 {len(results)} 条", file=sys.stderr)
conn.close()
