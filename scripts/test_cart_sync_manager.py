# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from crawler.cart_sync import calc_valid_quantity, CartSyncManager
from database.db_manager import DatabaseManager

sys.stdout.reconfigure(encoding='utf-8')

# Test calc_valid_quantity
print("--- Test calc_valid_quantity ---")
assert calc_valid_quantity(1, min_qty=1, package_qty=1) == 1
assert calc_valid_quantity(5, min_qty=12, package_qty=1) == 12
assert calc_valid_quantity(15, min_qty=12, package_qty=12) == 24
assert calc_valid_quantity(24, min_qty=12, package_qty=12) == 24
assert calc_valid_quantity(25, min_qty=12, package_qty=12) == 36
assert calc_valid_quantity(10, min_qty=24, package_qty=240) == 240
print("calc_valid_quantity tests passed successfully!")

# Test CartSyncManager with DatabaseManager
db = DatabaseManager('localhost', 3306, 'root', 'admin123', 'supplier_crawler')
sync_mgr = CartSyncManager(db)

# Test syncing a SmartyCart item (Trapoman, supplier_id=3)
trapoman_items = [
    {
        "product_id": 39372,
        "sku": "360356",
        "name": "PELOTA FUTBOL N2 ARGENTINA (SB 57195)",
        "quantity": 25,
        "min_qty": 5,
        "package_qty": 5,
        "price": 3300.0,
    }
]

print("\n--- Testing Sync Trapoman (ID 3) ---")
res = sync_mgr.sync_to_supplier(3, trapoman_items, auto_adjust=True)
print("Result success:", res.get("success"))
print("Result message:", res.get("message"))
print("Synced count:", res.get("synced_count"))
print("Cart URL:", res.get("cart_url"))
if res.get("failed_items"):
    print("Failed items:", res.get("failed_items"))
if res.get("adjusted_items"):
    print("Adjusted items:", res.get("adjusted_items"))
