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

# Function to extract potential model numbers or significant tokens
def extract_tokens(text):
    if not text:
        return set()
    # Find patterns like DH12345, AR1234, TE1234, CML-123, 12345 (5+ digits), etc.
    tokens = set()
    for tok in re.findall(r'[a-zA-Z0-9\-_/]+', text):
        clean = tok.strip('-_/').upper()
        if len(clean) >= 3:
            tokens.add(clean)
            # also stripped of non-alphanumeric
            clean_alnum = re.sub(r'[^A-Z0-9]', '', clean)
            if len(clean_alnum) >= 3:
                tokens.add(clean_alnum)
    return tokens

# Prepare DB item tokens
for db in db_items:
    db['tokens'] = extract_tokens(db['name']) | extract_tokens(db['product_url']) | extract_tokens(db['sku'])
    db['price_f'] = float(db['price'])

# Match invoice items
matches = []
unmatched = []

used_cart_ids = set()

for inv in invoice_items:
    inv_tokens = extract_tokens(inv['sku']) | extract_tokens(inv['barcode']) | extract_tokens(inv['name'])
    
    best_candidate = None
    best_score = 0
    
    for db in db_items:
        score = 0
        common_tokens = inv_tokens & db['tokens']
        # filter out generic tokens
        common_meaningful = [t for t in common_tokens if t not in {'PACK', 'KIT', 'CITY', 'GIRL', 'CON', 'PARA', 'SET', 'COLOR', 'MINI', '24U', '12U', '6U', 'ROJO', 'ACEITE', 'NAEZ', 'TEI', 'MELY', 'PINK', 'SKALA'}]
        
        if common_meaningful:
            # Score based on token lengths
            score += sum(len(t) * 10 for t in common_meaningful)
            
        # Price match bonus
        if abs(db['price_f'] - inv['price']) < 0.01:
            score += 25
            
        # Qty match bonus
        if db['quantity'] == inv['qty']:
            score += 20
            
        if score > best_score:
            best_score = score
            best_candidate = db
            
    if best_candidate and best_score >= 35:
        matches.append({
            'inv': inv,
            'db': best_candidate,
            'score': best_score,
            'qty_match': best_candidate['quantity'] == inv['qty'],
            'price_match': abs(best_candidate['price_f'] - inv['price']) < 0.01
        })
        used_cart_ids.add(best_candidate['cart_id'])
    else:
        unmatched.append(inv)

print(f"Total Invoice Items: {len(invoice_items)}")
print(f"Matched to DB: {len(matches)}")
print(f"Unmatched Invoice Items: {len(unmatched)}")
print(f"DB Items used: {len(used_cart_ids)} / {len(db_items)}")

# Let's inspect any unmatched invoice items
if unmatched:
    print("\n--- Unmatched Invoice Items ---")
    for u in unmatched:
        print(f"  P{u['p']} | SKU:{u['sku']} | Barcode:{u['barcode']} | Name:{u['name']} | Price:{u['price']} | Qty:{u['qty']}")

# Let's check quantity mismatches or price mismatches in matched
print("\n--- Price or Qty Differences in Matched ---")
diff_count = 0
for m in matches:
    inv = m['inv']
    db = m['db']
    clean_db_name = db['name'].encode('ascii', 'replace').decode('ascii')[:35]
    if not m['qty_match'] or not m['price_match']:
        diff_count += 1
        print(f"Diff #{diff_count}: P{inv['p']} | Inv: {inv['name'][:20]} (P:{inv['price']}, Q:{inv['qty']}) vs DB: {clean_db_name} (P:{db['price_f']}, Q:{db['quantity']})")

print(f"Total with diffs: {diff_count}")
