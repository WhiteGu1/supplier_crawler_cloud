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

# Let's write a script that does 1-to-1 best assignment
# Candidates scored by:
# 1. Exact model code in db name or url (e.g. DD2913 in url or name -> huge score)
# 2. Exact barcode match
# 3. Price match
# 4. Quantity match

assigned_inv = {} # inv_idx -> db_cart_id
assigned_db = {} # db_cart_id -> list of inv_idx

for i, inv in enumerate(invoice_items):
    best_db = None
    best_score = -1
    
    inv_code = inv['sku'].upper().replace(' ', '').replace('-', '')
    inv_bc = inv['barcode'].upper().replace(' ', '').replace('-', '')
    
    for db in db_items:
        db_text = (db['name'] + ' ' + db['product_url'] + ' ' + str(db['sku'])).upper().replace(' ', '').replace('-', '')
        score = 0
        
        # Check model code
        if len(inv_code) >= 3 and inv_code in db_text:
            score += 100
        # Check barcode
        if len(inv_bc) >= 6 and inv_bc in db_text:
            score += 120
            
        # Price match
        if abs(float(db['price']) - inv['price']) < 0.01:
            score += 30
            
        # Quantity match
        if db['quantity'] == inv['qty']:
            score += 15
            
        if score > best_score:
            best_score = score
            best_db = db
            
    if best_db and best_score >= 40:
        assigned_inv[i] = (best_db, best_score)
        cid = best_db['cart_id']
        if cid not in assigned_db:
            assigned_db[cid] = []
        assigned_db[cid].append(i)

print(f"Total invoice items: {len(invoice_items)}")
print(f"Assigned invoice items: {len(assigned_inv)} / {len(invoice_items)}")
print(f"Unique DB items covered: {len(assigned_db)} / {len(db_items)}")

# Let's inspect the matches and discrepancies
records = []
for db in db_items:
    cid = db['cart_id']
    inv_idxs = assigned_db.get(cid, [])
    inv_matches = [invoice_items[idx] for idx in inv_idxs]
    
    total_inv_qty = sum(m['qty'] for m in inv_matches)
    
    # Check unit prices
    price_diffs = []
    for m in inv_matches:
        if abs(m['price'] - float(db['price'])) > 0.01:
            price_diffs.append((m['price'], float(db['price'])))
            
    status = ""
    if not inv_matches:
        status = "未在发票中出现 (可能缺货/未发)"
    elif total_inv_qty == db['quantity']:
        if not price_diffs:
            status = "完全匹配 (数量&单价完全一致)"
        else:
            status = "数量一致，单价有差异"
    else:
        status = f"数量差异 (系统:{db['quantity']}, 发票:{total_inv_qty})"
        
    records.append({
        'cart_id': cid,
        'sku': db['sku'],
        'name': db['name'],
        'db_qty': db['quantity'],
        'inv_qty': total_inv_qty,
        'db_price': float(db['price']),
        'status': status,
        'inv_matches': inv_matches
    })

# Summary counts
status_counts = {}
for r in records:
    cat = r['status'].split(' (')[0]
    status_counts[cat] = status_counts.get(cat, 0) + 1

print("\n--- Summary of DB Cart Items (Total: 110) ---")
for k, v in status_counts.items():
    print(f"  {k}: {v}")

# Save detailed report to json
with open('scripts/comparison_report.json', 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

