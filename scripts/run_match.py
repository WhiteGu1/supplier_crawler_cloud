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

# Import invoice_items from previous script
from match_full_details import invoice_items

# We will match invoice items to db_items
# Matching rules:
# 1. Match by SKU substring in DB SKU or DB Name or DB URL
# 2. Match by Barcode substring in DB SKU or DB Name or DB URL
# 3. Match by name keyword matching

matched = []
unmatched_inv = []
db_matched_ids = set()

def normalize(s):
    if not s:
        return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

for inv in invoice_items:
    inv_sku_norm = normalize(inv['sku'])
    inv_bc_norm = normalize(inv['barcode'])
    inv_name_norm = normalize(inv['name'])
    
    best_db = None
    best_score = 0
    
    for db in db_items:
        db_sku_norm = normalize(db['sku'])
        db_name_norm = normalize(db['name'])
        db_url_norm = normalize(db['product_url'])
        
        score = 0
        # Exact SKU match
        if inv_sku_norm and len(inv_sku_norm) >= 4 and (inv_sku_norm in db_sku_norm or inv_sku_norm in db_name_norm or inv_sku_norm in db_url_norm):
            score += 100
        # Barcode match
        if inv_bc_norm and len(inv_bc_norm) >= 6 and (inv_bc_norm in db_sku_norm or inv_bc_norm in db_name_norm or inv_bc_norm in db_url_norm):
            score += 80
        # Price match (exact unit price match)
        if abs(float(db['price']) - inv['price']) < 0.01:
            score += 30
        
        if score > best_score:
            best_score = score
            best_db = db
            
    if best_db and best_score >= 50:
        matched.append({
            'inv': inv,
            'db': best_db,
            'score': best_score
        })
        db_matched_ids.add(best_db['cart_id'])
    else:
        unmatched_inv.append(inv)

print(f"Matched: {len(matched)} / {len(invoice_items)}")
print(f"Unmatched invoice items: {len(unmatched_inv)}")
for u in unmatched_inv:
    print(f"  Unmatched: P{u['p']} | SKU:{u['sku']} | Name:{u['name']} | Price:{u['price']} | Qty:{u['qty']}")

unmatched_db = [db for db in db_items if db['cart_id'] not in db_matched_ids]
print(f"\nUnmatched DB items: {len(unmatched_db)} / {len(db_items)}")

