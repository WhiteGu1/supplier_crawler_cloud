import pymysql
import re
from parse_all_5_xls import all_tickets

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute('''
        SELECT c.id as cart_id, c.product_id, c.quantity as cart_qty, p.name, p.sku, p.price, p.product_url
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18
        ORDER BY c.id ASC
    ''')
    cart_items = cur.fetchall()
    
    cur.execute('''
        SELECT id as product_id, name, sku, price, product_url
        FROM products
        WHERE supplier_id = 18
    ''')
    all_prods = cur.fetchall()

print(f"Cart items: {len(cart_items)}, All Bella products: {len(all_prods)}")

def find_db_match(inv_sku, inv_bc, inv_name, inv_price, inv_qty):
    # Clean tokens from inv_sku and inv_bc
    raw_codes = []
    for part in re.split(r'[/\s]+', inv_sku + ' ' + inv_bc):
        part = part.strip()
        if len(part) >= 4 and part not in {'ACEITE', 'CEPILLO', 'NEGRO', 'LACTEA', 'REMOVEDOR120ML', 'KAKAZIYAN'}:
            raw_codes.append(part)
            # If barcode is 13 digits (e.g. 6983434367052), the last 5 or 6 digits are often in Bella's product name!
            if part.isdigit() and len(part) >= 12:
                raw_codes.append(part[-5:])
                raw_codes.append(part[-6:])
        # Also extract prefix codes like DH-JZD-EYE-6705 -> 6705, BC1820 -> 1820
        m = re.match(r'^([A-Z]+-?[A-Z0-9-]+?)([A-Z]{3,})?$', part)
        
    # First search in cart_items
    best_cart = None
    best_score = 0
    for c in cart_items:
        hay = (c['name'] + ' ' + str(c['sku']) + ' ' + c['product_url']).upper()
        hay_no_dash = hay.replace('-', '').replace(' ', '')
        score = 0
        for code in raw_codes:
            cu = code.upper()
            cu_no_dash = cu.replace('-', '')
            if len(cu) >= 4 and (cu in hay or cu_no_dash in hay_no_dash):
                score += len(cu) * 10
        if abs(float(c['price']) - inv_price) < 0.01:
            score += 25
        if c['cart_qty'] == inv_qty:
            score += 15
        if score > best_score:
            best_score = score
            best_cart = c
            
    if best_cart and best_score >= 50:
        return best_cart, "购物车订单商品"
        
    # Search in all_prods
    best_prod = None
    best_pscore = 0
    for p in all_prods:
        hay = (p['name'] + ' ' + str(p['sku']) + ' ' + p['product_url']).upper()
        hay_no_dash = hay.replace('-', '').replace(' ', '')
        score = 0
        for code in raw_codes:
            cu = code.upper()
            cu_no_dash = cu.replace('-', '')
            if len(cu) >= 4 and (cu in hay or cu_no_dash in hay_no_dash):
                score += len(cu) * 10
        if abs(float(p['price']) - inv_price) < 0.01:
            score += 25
        if score > best_pscore:
            best_pscore = score
            best_prod = p
            
    if best_prod and best_pscore >= 50:
        return best_prod, "商品库匹配"
    return None, "未直接匹配"

# Test on 55555.xls
print("\n--- Matching 55555.xls items ---")
matched_5 = 0
for idx, it in enumerate(all_tickets[4]['items'], 1):
    m, mtype = find_db_match(it['sku'], it['barcode_or_line2'], it['name_line1'], it['price'], it['qty'])
    if m:
        matched_5 += 1
        cname = m['name'].encode('ascii', 'replace').decode('ascii')[:45]
        print(f"  {idx:02d}. {it['sku']} -> [{mtype}] WebSKU:{m['sku']} | {cname}")
    else:
        print(f"  {idx:02d}. {it['sku']} ({it['barcode_or_line2']}) P:{it['price']} Q:{it['qty']} -> UNMATCHED")
print(f"Matched {matched_5} / {len(all_tickets[4]['items'])} in 55555.xls")
