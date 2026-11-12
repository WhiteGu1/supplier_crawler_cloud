import json
import pymysql
import re

# Load DB items
conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute('''
        SELECT c.id as cart_id, c.product_id, c.quantity, p.name, p.sku, p.price, p.product_url, p.package_qty, p.sub_pack_qty
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18
        ORDER BY c.id ASC
    ''')
    db_items = cur.fetchall()

from match_full_details import invoice_items

# We will create a precise audit report
# For each DB item, search if it appears in invoice_items
# Multiple invoice rows might correspond to the same product (e.g. split across tickets)

report = []

for db in db_items:
    db_name = db['name']
    db_url = db['product_url']
    db_price = float(db['price'])
    db_qty = db['quantity']
    
    # find all matching invoice rows
    matched_inv_rows = []
    
    # Extract codes from db_name and db_url
    codes = set()
    for m in re.findall(r'[A-Za-z0-9\-]+', db_name + ' ' + db_url):
        if len(m) >= 4 and not m.isdigit():
            codes.add(m.upper())
        elif len(m) >= 5 and m.isdigit():
            codes.add(m)
            
    for inv in invoice_items:
        inv_code = inv['sku'].upper()
        inv_bc = inv['barcode'].upper()
        inv_name = inv['name'].upper()
        
        hit = False
        # Check code overlap
        for c in codes:
            if c in {'PACK', 'PARA', 'CON', 'MINI', 'COLOR', 'CITY', 'GIRL', 'NAEZ', 'TEI', 'MELY', 'PINK', 'SKALA', 'CHARM', 'LIMIT', 'UNIDAD', 'CAJA'}:
                continue
            if c in inv_code or c in inv_bc or (len(c) >= 5 and c in inv_name):
                hit = True
                break
                
        # Also check price similarity if hit
        if hit:
            matched_inv_rows.append(inv)
            
    total_inv_qty = sum(r['qty'] for r in matched_inv_rows)
    report.append({
        'cart_id': db['cart_id'],
        'name': db_name,
        'sku': db['sku'],
        'db_price': db_price,
        'db_qty': db_qty,
        'matched_inv_rows': matched_inv_rows,
        'total_inv_qty': total_inv_qty,
        'status': 'FULL_MATCH' if total_inv_qty == db_qty else ('PARTIAL' if total_inv_qty > 0 else 'NOT_ON_INVOICE')
    })

full_match = [r for r in report if r['status'] == 'FULL_MATCH']
partial = [r for r in report if r['status'] == 'PARTIAL']
not_found = [r for r in report if r['status'] == 'NOT_ON_INVOICE']

print(f"Total DB Items: {len(db_items)}")
print(f"Full Match (Qty exact): {len(full_match)}")
print(f"Partial Match (Qty diff): {len(partial)}")
print(f"Not on invoice (Out of stock / not packed): {len(not_found)}")
