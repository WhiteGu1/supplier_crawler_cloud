# -*- coding: utf-8 -*-
import sys, pymysql

sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT COUNT(*) as cnt FROM products WHERE supplier_id = 16 AND sku LIKE 'DA-%'")
print('Total DA products in Gaston:', cur.fetchone()['cnt'])

cur.execute("SELECT category, COUNT(*) as cnt FROM products WHERE supplier_id = 16 AND sku LIKE 'DA-%' GROUP BY category ORDER BY cnt DESC")
print('\nCategory Distribution:')
for r in cur.fetchall():
    print(f"  {r['category']:35s}: {r['cnt']}")

cur.execute("SELECT id, sku, name, price, category, description, image_url FROM products WHERE supplier_id = 16 AND sku IN ('DA-01', 'DA-100', 'DA-200', 'DA-300', 'DA-401') ORDER BY id")
print('\nSample Products:')
for r in cur.fetchall():
    print(f"  [{r['id']}] {r['sku']:8s} | ${float(r['price']):8.2f} | Cat: {r['category']:25s} | Img: {r['image_url']:32s} | Name: {r['name']}")

conn.close()
