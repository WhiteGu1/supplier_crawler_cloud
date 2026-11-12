import json
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='admin123', database='supplier_crawler', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

with conn.cursor() as cur:
    cur.execute('''
        SELECT c.id as cart_id, c.product_id, c.quantity as cur_cart_qty, p.name, p.sku, p.price, p.product_url, p.package_qty, p.sub_pack_qty
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18
    ''')
    cur_cart = {r['product_id']: r for r in cur.fetchall()}

from parse_order_and_sync import order_sync_data

print("Comparing current cart with order:")
diffs = []
for item in order_sync_data:
    pid = item['product_id']
    cur_it = cur_cart.get(pid)
    order_packs = item['order_qty']
    line_total = item['line_total']
    unit_price = item['db_price']
    
    # Calculate exact total units based on line_total / unit_price
    calc_units = round(line_total / unit_price) if unit_price > 0 else order_packs
    
    cur_qty = cur_it['cur_cart_qty'] if cur_it else 0
    if cur_qty != calc_units:
        diffs.append({
            'pid': pid,
            'name': item['name'][:30],
            'cur_qty': cur_qty,
            'new_qty': calc_units,
            'order_multiplier': order_packs,
            'line_total': line_total,
            'unit_price': unit_price
        })

print(f"Total order items: {len(order_sync_data)}")
print(f"Items with quantity difference: {len(diffs)}")
for d in diffs[:10]:
    clean_name = d['name'].encode('ascii', 'replace').decode('ascii')
    print(" ", clean_name, "cur:", d['cur_qty'], "-> new:", d['new_qty'], f"(${d['line_total']:,.0f})")
