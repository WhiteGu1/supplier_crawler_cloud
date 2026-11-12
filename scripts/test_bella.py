import pymysql
import json
import urllib.request

conn = pymysql.connect(host='localhost', user='root', password='admin123', database='supplier_crawler', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute('''
        SELECT c.id, c.product_id, c.quantity, p.name, p.sku, p.price, p.product_url, p.is_missing, p.package_qty, p.sub_pack_qty
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18
        ORDER BY c.id ASC
    ''')
    rows = cur.fetchall()

print(f"Total Bella items in cart: {len(rows)}")
for r in rows:
    if r['sku'] == '188728':
        print("188728 in cart:", {k: v for k, v in r.items() if k != 'name'})
        break
