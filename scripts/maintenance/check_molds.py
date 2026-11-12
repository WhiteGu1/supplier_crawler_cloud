# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

def show_query(title, sql):
    print(f"\n=== {title} ===")
    cur.execute(sql)
    rows = cur.fetchall()
    for r in rows:
        print(f"[{r['id']}] {r['sku']}: {r['name']} (${float(r['price']):.2f})")
    print(f"Count: {len(rows)}")

show_query("MOLDE / HIELERA / HELADO", "SELECT id, sku, name, price FROM products WHERE supplier_id = 16 AND (name LIKE '%molde%' OR name LIKE '%hiel%' OR name LIKE '%helad%')")
show_query("COCINA / BAZAR UNDER $2000", "SELECT id, sku, name, price, category FROM products WHERE supplier_id = 16 AND price > 0 AND price <= 2000 AND (category LIKE '%Cocina%' OR category LIKE '%Bazar%')")

conn.close()
