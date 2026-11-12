# -*- coding: utf-8 -*-
import sys
import fitz
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

# 1. 检查数据库中现有 supplier_id = 16 的 DA 相关商品
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT COUNT(*) as cnt FROM products WHERE supplier_id = 16")
print("Gaston 总商品数:", cur.fetchone()['cnt'])

cur.execute("SELECT COUNT(*) as cnt FROM products WHERE supplier_id = 16 AND sku LIKE 'DA%'")
print("Gaston SKU以DA开头的商品数:", cur.fetchone()['cnt'])

cur.execute("SELECT id, sku, name, price, category, image_url FROM products WHERE supplier_id = 16 AND sku LIKE 'DA%' LIMIT 10")
for r in cur.fetchall():
    print("  ", r)

conn.close()
