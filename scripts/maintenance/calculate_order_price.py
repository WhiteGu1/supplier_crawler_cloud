# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

raw_text = """
C02109OR     4
C04539LI     12
C04538LI     12
G01770LI     12
SHO0029U   6
SH4211MI    6
SH4295OR   6
SH4272OR   6
SH4696OR   6
SH4730OR   6
DA-390      12
DA-389      12
DA-383      12
DA-67        12
DA-01        12
DA-07        12
DA-297      12
DA-279      12
DA-280      12
DA-278      12
SH2796MI    6
SH4767UC    6
IGI-001     12
IGI-056    12
IGB-302    24
SH4780PE    12
IGH-055A     12
DA-373      24
SH4736MI    12
"""

lines = [l.strip() for l in raw_text.strip().split('\n') if l.strip()]
order_items = []
for line in lines:
    parts = line.split()
    sku = parts[0].strip()
    qty = int(parts[1].strip())
    order_items.append((sku, qty))

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

results = []

for sku, qty in order_items:
    # 优先精确查找
    cur.execute("""
        SELECT p.id, p.supplier_id, s.name as supplier_name, s.price_adjustment, p.sku, p.name, p.price, p.is_available
        FROM products p
        JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.sku = %s
    """, (sku,))
    rows = cur.fetchall()

    if not rows:
        # 尝试忽略横杠或空格
        clean_sku = sku.replace('-', '').replace(' ', '')
        cur.execute("""
            SELECT p.id, p.supplier_id, s.name as supplier_name, s.price_adjustment, p.sku, p.name, p.price, p.is_available
            FROM products p
            JOIN suppliers s ON p.supplier_id = s.id
            WHERE REPLACE(REPLACE(p.sku, '-', ''), ' ', '') = %s
        """, (clean_sku,))
        rows = cur.fetchall()

    if not rows:
        # 尝试模糊查询
        cur.execute("""
            SELECT p.id, p.supplier_id, s.name as supplier_name, s.price_adjustment, p.sku, p.name, p.price, p.is_available
            FROM products p
            JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.sku LIKE %s
        """, (f"{sku}%",))
        rows = cur.fetchall()

    results.append({
        "query_sku": sku,
        "qty": qty,
        "matches": rows
    })

conn.close()

print(f"Total queries: {len(results)}")
not_found = []
multiple = []
for r in results:
    q_sku = r['query_sku']
    qty = r['qty']
    m = r['matches']
    if len(m) == 0:
        not_found.append(q_sku)
        print(f"[NOT FOUND] {q_sku} x {qty}")
    elif len(m) == 1:
        prod = m[0]
        base_p = float(prod['price'])
        adj = float(prod['price_adjustment'] or 0.0)
        adj_p = round(base_p * (1 + adj / 100), 2)
        print(f"[OK] {q_sku:10s} x {qty:2d} -> [{prod['supplier_name']}] {prod['sku']:10s} | Base:${base_p:.2f} | Adj({adj:+.1f}%):${adj_p:.2f} | {prod['name'][:35]}")
    else:
        multiple.append(q_sku)
        print(f"[MULTI ({len(m)})] {q_sku} x {qty}:")
        for prod in m:
            base_p = float(prod['price'])
            adj = float(prod['price_adjustment'] or 0.0)
            adj_p = round(base_p * (1 + adj / 100), 2)
            print(f"   - [{prod['supplier_name']} (id:{prod['supplier_id']})] {prod['sku']:10s} Base:${base_p:.2f} Adj:${adj_p:.2f} | {prod['name'][:35]}")

print(f"\nSummary:")
print(f"  Exact 1 match: {len(results) - len(not_found) - len(multiple)}")
print(f"  Not found: {len(not_found)} -> {not_found}")
print(f"  Multiple matches: {len(multiple)} -> {multiple}")
