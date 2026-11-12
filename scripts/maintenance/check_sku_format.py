# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("SELECT COUNT(*) as cnt FROM products WHERE sku LIKE '% %'")
print('SKUs with space in whole DB:', cur.fetchone()['cnt'])
cur.execute("SELECT sku FROM products WHERE sku LIKE '% %' LIMIT 10")
print('Sample SKUs with space:', [r['sku'] for r in cur.fetchall()])

cur.execute("SELECT sku, name FROM products WHERE supplier_id = 16 LIMIT 10")
print('Sample Gaston SKUs:', [r['sku'] for r in cur.fetchall()])

conn.close()
