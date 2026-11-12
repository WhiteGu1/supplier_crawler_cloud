# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("""
    SELECT p.id, p.name, p.price, p.category
    FROM favorites f
    JOIN products p ON f.product_id = p.id
    WHERE p.supplier_id = 3
    ORDER BY f.id
""")
favs = cur.fetchall()

toy_keywords = ['juego mesa', 'burbujero', 'pelota', 'damas', 'ajedrez', 'ludo', 'pool table', 'bijouterie', 'muñeca', 'juguete', 'pistola agua', 'inflable']

candidate_favs = [f for f in favs if not ('玩具' in (f['category'] or '') or any(k in f['name'].lower() for k in toy_keywords))]

print(f"Total candidate non-toy favorites: {len(candidate_favs)}")
for i, f in enumerate(candidate_favs):
    print(f"[{i+1:2d}] ID:{f['id']:5d} | ${float(f['price']):9.2f} | {f['name']}")

conn.close()
