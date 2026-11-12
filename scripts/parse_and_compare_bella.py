import json
import re
import pymysql

def load_db_items():
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
    return db_items

db_items = load_db_items()
print(f"Loaded {len(db_items)} items from database.")
for it in db_items[:5]:
    clean_name = it['name'].encode('ascii', 'replace').decode('ascii')
    print(f"  ID:{it['cart_id']} | SKU:{it['sku']} | Price:{it['price']} | Qty:{it['quantity']} | Name:{clean_name[:40]}")
