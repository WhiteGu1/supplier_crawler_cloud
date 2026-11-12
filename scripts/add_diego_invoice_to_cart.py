"""
scripts/add_diego_invoice_to_cart.py
Add the 51 Diego invoice items to the shopping cart.
"""
import os
import re
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import DatabaseManager
from scripts.check_and_add_diego_items import INVOICE_ITEMS

def main():
    db = DatabaseManager('localhost', 3306, 'root', 'admin123', 'supplier_crawler')
    
    with db.connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, sku, name, price, image_url, min_qty, package_qty FROM products WHERE supplier_id = 2")
        diego_prods = cur.fetchall()

    by_sku = {}
    by_img_code = {}
    for p in diego_prods:
        sku = (p.get("sku") or "").strip()
        if sku:
            by_sku[sku] = p
        img_url = p.get("image_url") or ""
        m = re.search(r'/catalogo/(\d+)\.', img_url)
        if m:
            by_img_code[m.group(1)] = p

    added_count = 0
    total_qty = 0

    with db.connection() as conn:
        cursor = conn.cursor()
        for item in INVOICE_ITEMS:
            cod = str(item["cod"])
            qty = item["qty"]
            p = by_sku.get(cod) or by_img_code.get(cod)
            if not p:
                print(f"Error: Cod {cod} not found in DB!")
                continue

            pid = p["id"]
            # Ensure SKU is set to Cod
            if not p.get("sku"):
                cursor.execute("UPDATE products SET sku = %s WHERE id = %s", (cod, pid))
            
            # Add or set quantity in cart_items
            db.add_to_cart(product_id=pid, quantity=qty, mode="set")
            added_count += 1
            total_qty += qty

        conn.commit()

    print(f"Successfully added/updated {added_count} Diego products in cart.")
    print(f"Total units added: {total_qty}")

    # Verify cart items
    cart_items = [it for it in db.get_cart_items() if it.get("supplier_id") == 2]
    print(f"Verified Diego items in cart: {len(cart_items)} items, {sum(it['quantity'] for it in cart_items)} units.")

if __name__ == "__main__":
    main()
