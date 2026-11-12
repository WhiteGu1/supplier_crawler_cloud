# -*- coding: utf-8 -*-
import sys
import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.db_manager import DatabaseManager

db = DatabaseManager('localhost', 3306, 'root', 'admin123', 'supplier_crawler')
items = db.get_cart_items()
bella_items = [it for it in items if 'bella' in (it.get('supplier_name') or '').lower() or it.get('supplier_id') == 18]

print(f"Total items in cart: {len(items)}")
print(f"Bella Central items in cart: {len(bella_items)}")
for it in bella_items:
    print(f"ID={it['product_id']} | Qty={it['quantity']} | min_qty={it['min_qty']} | pkg_qty={it['package_qty']} | SKU={it['sku']} | Name={it['name']} | URL={it['product_url']}")
