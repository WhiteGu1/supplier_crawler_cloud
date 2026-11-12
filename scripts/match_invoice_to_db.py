import json
import re
import pymysql

# Load database cart items for Bella Central (supplier_id = 18)
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

print(f"Total Bella items in DB cart: {len(db_items)}")

# Load OCR data
with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

# Let's inspect the pages and order of pages
# We want to understand the exact page sequence and line items
for p in pages:
    print(f"Page {p['page_index']}: {p['filename']} ({len(p['boxes'])} boxes)")
