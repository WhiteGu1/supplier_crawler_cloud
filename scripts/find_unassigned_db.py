import pymysql
import re

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute('''
        SELECT c.id as cart_id, c.quantity, p.name, p.sku, p.price, p.product_url
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18
        ORDER BY c.id ASC
    ''')
    db_items = cur.fetchall()

from show_unassigned import invoice_items
from build_full_comparison_table import assigned_inv

unassigned_indices = [i for i in range(len(invoice_items)) if i not in assigned_inv]

print(f"Finding exact matches for {len(unassigned_indices)} items:")

for idx in unassigned_indices:
    inv = invoice_items[idx]
    # search candidates in db
    code_digits = re.findall(r'\d+', inv['sku'] + ' ' + inv['barcode'])
    code_letters = re.findall(r'[A-Za-z]+', inv['sku'])
    
    candidates = []
    for db in db_items:
        db_str = (db['name'] + ' ' + db['product_url'] + ' ' + str(db['sku'])).upper()
        
        # Check if digits in db_str
        matched_digits = [d for d in code_digits if len(d) >= 4 and d in db_str]
        matched_letters = [l for l in code_letters if len(l) >= 2 and l.upper() in db_str]
        
        if matched_digits:
            candidates.append((db, matched_digits))
            
    clean_name = inv['name'].encode('ascii', 'replace').decode('ascii')
    print(f"\nInvoice [{idx}] P{inv['p']} {inv['sku']} / {inv['barcode']} (P:{inv['price']}, Q:{inv['qty']}): {clean_name}")
    if candidates:
        for c, digs in candidates[:3]:
            c_name = c['name'].encode('ascii', 'replace').decode('ascii')
            print(f"   -> DB ID {c['cart_id']} (P:{c['price']}, Q:{c['quantity']}): {c_name[:50]} (matched: {digs})")
    else:
        print("   -> NO DIGIT MATCH IN DB")
