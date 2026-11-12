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

show_query("PERCHAS", "SELECT id, sku, name, price FROM products WHERE supplier_id = 16 AND name LIKE '%percha%'")
show_query("CEPILLOS & ESCOBAS", "SELECT id, sku, name, price FROM products WHERE supplier_id = 16 AND (name LIKE '%cepillo%' OR name LIKE '%escob%')")
show_query("JABONERAS", "SELECT id, sku, name, price FROM products WHERE supplier_id = 16 AND name LIKE '%jabon%'")
show_query("PAÑOS & REPASADORES & TOALLAS", "SELECT id, sku, name, price FROM products WHERE supplier_id = 16 AND (name LIKE '%paño%' OR name LIKE '%repasador%' OR name LIKE '%toalla%' OR name LIKE '%microfibra%')")
show_query("ORGANIZADORES", "SELECT id, sku, name, price FROM products WHERE supplier_id = 16 AND name LIKE '%organizador%'")
show_query("GANCHOS", "SELECT id, sku, name, price FROM products WHERE supplier_id = 16 AND name LIKE '%gancho%'")

conn.close()
