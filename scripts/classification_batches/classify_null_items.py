import pymysql, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

# Get all NULL/empty category items
cur.execute("SELECT id, supplier_id, sku, name, image_local FROM products WHERE category IS NULL OR category = '' ORDER BY supplier_id, id")
items = cur.fetchall()
print(f'Total NULL/empty items: {len(items)}')

# Classification rules based on name keywords (Spanish + Chinese)
rules = [
    # 厨房餐具
    ('molde|cuchillo|cuchara|tenedor|taza|vaso|copa|plato|olla|cacerola|sarten|tartera|batidor|tijera|cortador|jarra|botella|termica|dispenser|salero|sacacorcho|tabla', '厨房餐具'),
    ('bowl|vidrio|melamina|silicona|blister', '厨房餐具'),
    # 家居生活
    ('canasto|cesto|taper|fresh box|tacho|alfombra|espejo|organizador|carpeta|tender|set x3', '家居生活'),
    ('jarro|mug|botella termica', '家居生活'),
    # 箱包配件
    ('mochila|cartuchera|riñonera|bolso|maleta', '箱包配件'),
    # 文具
    ('sticker|llavero', '文具'),
    # 玩具
    ('juguete|globo|carpa', '玩具游戏'),
    # 美妆个护
    ('pestañas|alhajero|cepillo|guantes|bufanda', '美妆个护'),
    # 其他
    ('adaptador|canilla|bolsa|agua caliente', '家居生活'),
]

classified = 0
unmatched = []
for item in items:
    name_lower = item['name'].lower()
    matched = False
    for pattern, cat in rules:
        if any(p in name_lower for p in pattern.split('|')):
            # Use one-level category (no sub-category for now)
            full_cat = cat
            cur.execute('UPDATE products SET category=%s WHERE id=%s', (full_cat, item['id']))
            classified += 1
            matched = True
            break
    if not matched:
        unmatched.append(item)
        print(f"  UNMATCHED: sid={item['supplier_id']} id={item['id']} name={item['name']}")

print(f'\nClassified by rules: {classified}')
print(f'Unmatched: {len(unmatched)}')

conn.commit()

# Show unmatched for further processing
for item in unmatched:
    print(f"  NEED_REVIEW: id={item['id']} name={item['name']}")

conn.close()
