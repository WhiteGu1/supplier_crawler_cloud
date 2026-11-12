# -*- coding: utf-8 -*-
import sys
import re
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

# 1. 抓取 Trapoman 收藏商品
cur.execute("""
    SELECT p.id, p.name, p.price, p.category, p.description
    FROM favorites f
    JOIN products p ON f.product_id = p.id
    WHERE p.supplier_id = 3
    ORDER BY f.id
""")
favs = cur.fetchall()

# 玩具类排除规则
toy_keywords = ['juego mesa', 'burbujero', 'pelota', 'damas', 'ajedrez', 'ludo', 'pool table', 'bijouterie', 'muñeca', 'juguete', 'pistola agua', 'inflable']

toy_favs = []
candidate_favs = []

for f in favs:
    name_l = f['name'].lower()
    cat_l = (f['category'] or '').lower()
    is_toy = ('玩具' in cat_l or any(k in name_l for k in toy_keywords))
    if is_toy:
        toy_favs.append(f)
    else:
        candidate_favs.append(f)

print(f"Trapoman 收藏总数: {len(favs)}")
print(f"玩具类排除: {len(toy_favs)} 个")
for t in toy_favs:
    print(f"  - [排除玩具] [{t['id']}] {t['name']} | ${t['price']} | {t['category']}")

print(f"\n需要去 Gaston 匹配的非玩具商品: {len(candidate_favs)} 个")

# 2. 抓取 Gaston 全部在售商品
cur.execute("""
    SELECT id, sku, name, price, category, image_url
    FROM products
    WHERE supplier_id = 16 AND is_available = 1
""")
gaston_prods = cur.fetchall()
print(f"Gaston 在售商品数: {len(gaston_prods)}")

conn.close()
