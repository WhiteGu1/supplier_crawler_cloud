# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute('SELECT id, sku, name, price, image_url, created_at FROM products WHERE sku LIKE %s', ('%SBK%',))
for r in cur.fetchall():
    print(f"[{r['id']}] SKU:{r['sku']:15s} | ${float(r['price']):8.2f} | Image: {r['image_url']} | Name: {r['name']}")
conn.close()
