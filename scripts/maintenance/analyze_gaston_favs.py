# -*- coding: utf-8 -*-
import sys
import re
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

# 1. 抓取 Trapoman 收藏中的商品
cur.execute("""
    SELECT p.id, p.name, p.price, p.category
    FROM favorites f
    JOIN products p ON f.product_id = p.id
    WHERE p.supplier_id = 3
    ORDER BY f.id
""")
favs = cur.fetchall()
toy_keywords = ['juego mesa', 'burbujero', 'pelota', 'damas', 'ajedrez', 'ludo', 'pool table', 'bijouterie', 'muñeca', 'juguete', 'pistola agua', 'inflable']
candidates = [f for f in favs if not ('玩具' in (f['category'] or '') or any(k in f['name'].lower() for k in toy_keywords))]

print(f"Total favorites: {len(favs)}, Non-toy candidates: {len(candidates)}")

# 2. 抓取 Gaston 全部商品
cur.execute("""
    SELECT id, sku, name, price, category
    FROM products
    WHERE supplier_id = 16
""")
gaston_prods = cur.fetchall()
print(f"Gaston products: {len(gaston_prods)}")

# 打印所有 53 个候选商品
for i, c in enumerate(candidates, 1):
    print(f"{i:2d}. [{c['id']}] ${float(c['price']):.2f} : {c['name']}")

conn.close()
