"""
scripts/restore_cart_and_add_invoice.py
1. Restore all non-Diego cart items deleted at 10:27 from binlog:
   - Bella Central: 93 items
   - Trapoman: 31 items
   - benabi: 12 items
   - Dsaza: 14 items
   - najal: 1 item
2. Ensure the 51 Diego invoice items (total 1735 units) are in the cart.
"""
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import DatabaseManager
from scripts.check_and_add_diego_items import INVOICE_ITEMS

def main():
    db = DatabaseManager('localhost', 3306, 'root', 'admin123', 'supplier_crawler')

    # Read recovered_deletes.txt
    with open('recovered_deletes.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    events = text.split('=== EVENT ===')
    deleted_rows = []
    for ev in events:
        if '261017 10:27:' in ev:
            matches = re.findall(r'###\s+@1=(\d+)\s+###\s+@2=(\d+)\s+###\s+@3=(\d+)', ev)
            for cid, pid, qty in matches:
                deleted_rows.append((int(cid), int(pid), int(qty)))

    # Fetch product supplier info
    with db.connection() as conn:
        cur = conn.cursor(dictionary=True)
        pids = [r[1] for r in deleted_rows]
        format_strings = ','.join(['%s'] * len(pids))
        cur.execute(f"SELECT p.id, p.name, p.sku, p.supplier_id, s.name as supplier_name FROM products p LEFT JOIN suppliers s ON p.supplier_id=s.id WHERE p.id IN ({format_strings})", pids)
        prods = {p['id']: p for p in cur.fetchall()}

    # Separate non-Diego items to restore
    non_diego_to_restore = []
    for cid, pid, qty in deleted_rows:
        p = prods.get(pid)
        if p and p.get("supplier_id") != 2:
            non_diego_to_restore.append((pid, qty, p["name"], p["supplier_name"]))

    print(f"Non-Diego items to restore: {len(non_diego_to_restore)}")
    sup_counts = Counter(item[3] for item in non_diego_to_restore)
    for sup, cnt in sup_counts.items():
        print(f"  {sup}: {cnt} items")

    # 1. Restore non-Diego items into cart
    restored_cnt = 0
    with db.connection() as conn:
        cursor = conn.cursor()
        for pid, qty, name, sname in non_diego_to_restore:
            # Check if already in cart
            cursor.execute("SELECT id FROM cart_items WHERE product_id = %s", (pid,))
            existing = cursor.fetchone()
            if not existing:
                cursor.execute(
                    "INSERT INTO cart_items (product_id, quantity, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())",
                    (pid, qty)
                )
                restored_cnt += 1
            else:
                # keep existing quantity
                pass
        conn.commit()

    print(f"Restored {restored_cnt} non-Diego items to cart_items.")

    # 2. Ensure all 51 Diego invoice items are properly set in cart
    with db.connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, sku, name, price, image_url FROM products WHERE supplier_id = 2")
        diego_all = cur.fetchall()

    by_sku = {}
    by_img_code = {}
    for p in diego_all:
        sku = (p.get("sku") or "").strip()
        if sku:
            by_sku[sku] = p
        img_url = p.get("image_url") or ""
        m = re.search(r'/catalogo/(\d+)\.', img_url)
        if m:
            by_img_code[m.group(1)] = p

    diego_added = 0
    diego_units = 0
    with db.connection() as conn:
        cursor = conn.cursor()
        # First remove any other Diego items not in the invoice
        invoice_cods = {str(item["cod"]) for item in INVOICE_ITEMS}
        
        for item in INVOICE_ITEMS:
            cod = str(item["cod"])
            qty = item["qty"]
            p = by_sku.get(cod) or by_img_code.get(cod)
            if not p:
                print(f"Warning: Diego Cod {cod} not found in DB!")
                continue
            
            pid = p["id"]
            if not p.get("sku"):
                cursor.execute("UPDATE products SET sku = %s WHERE id = %s", (cod, pid))

            # Set exact quantity in cart
            cursor.execute("SELECT id FROM cart_items WHERE product_id = %s", (pid,))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE cart_items SET quantity = %s, updated_at = NOW() WHERE id = %s", (qty, row[0]))
            else:
                cursor.execute("INSERT INTO cart_items (product_id, quantity, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())", (pid, qty))

            diego_added += 1
            diego_units += qty

        # Clean up any Diego items in cart that were NOT in the invoice
        invoice_pids = []
        for item in INVOICE_ITEMS:
            cod = str(item["cod"])
            p = by_sku.get(cod) or by_img_code.get(cod)
            if p:
                invoice_pids.append(p["id"])

        if invoice_pids:
            fmt_pids = ','.join(['%s'] * len(invoice_pids))
            cursor.execute(
                f"DELETE c FROM cart_items c JOIN products p ON c.product_id = p.id WHERE p.supplier_id = 2 AND c.product_id NOT IN ({fmt_pids})",
                invoice_pids
            )
            deleted_old_diego = cursor.rowcount
            if deleted_old_diego > 0:
                print(f"Removed {deleted_old_diego} old Diego items not in the invoice.")

        conn.commit()

    print(f"Diego invoice items in cart: {diego_added} items, {diego_units} units.")

    # 3. Final Cart Summary
    final_items = db.get_cart_items()
    print(f"\n=== FINAL CART STATE ===")
    print(f"Total products in cart: {len(final_items)}")
    final_sup_counts = Counter(it["supplier_name"] for it in final_items)
    for sup, cnt in final_sup_counts.items():
        sub_items = [it for it in final_items if it["supplier_name"] == sup]
        total_u = sum(it["quantity"] for it in sub_items)
        print(f"  {sup}: {cnt} items ({total_u} units)")

if __name__ == "__main__":
    main()
