# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("""
    UPDATE products 
    SET image_url = CONCAT('/images/gaston_16/', sku, '.jpg')
    WHERE supplier_id = 16 AND sku LIKE 'SBK-%'
""")
affected = cur.rowcount
conn.commit()
print(f"Updated {affected} rows.")

cur.execute("SELECT id, sku, name, price, image_url FROM products WHERE supplier_id = 16 AND sku LIKE 'SBK-%'")
for r in cur.fetchall():
    print(f"[{r['id']}] SKU:{r['sku']:15s} | Image: {r['image_url']} | Name: {r['name']}")

conn.close()
