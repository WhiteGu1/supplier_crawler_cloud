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

# 先修一下 DA-373 的名称
cur.execute("UPDATE products SET name='JABONERA SPORT' WHERE supplier_id=16 AND sku='DA-373'")
conn.commit()

# 获取 Gaston 的税率 / 调价比例
cur.execute("SELECT name, price_adjustment FROM suppliers WHERE id=16")
sup = cur.fetchone()
tax_rate = float(sup['price_adjustment'] or 0.0) # 10.5%

details = []
total_base = 0.0
total_adjusted = 0.0
consultar_items = []

for sku, qty in order_items:
    cur.execute("""
        SELECT p.id, p.sku, p.name, p.price, p.category, p.description
        FROM products p
        WHERE p.supplier_id=16 AND (p.sku=%s OR p.sku LIKE %s)
        LIMIT 1
    """, (sku, f"{sku}%"))
    prod = cur.fetchone()
    
    if not prod:
        print(f"Error: {sku} not found!")
        continue
        
    base_price = float(prod['price'])
    # 调价后单价
    adj_price = round(base_price * (1 + tax_rate / 100), 2)
    
    base_subtotal = round(base_price * qty, 2)
    adj_subtotal = round(adj_price * qty, 2)
    
    total_base += base_subtotal
    total_adjusted += adj_subtotal
    
    if base_price == 0.0:
        consultar_items.append((sku, prod['name'], qty))
        
    details.append({
        "sku": prod['sku'],
        "name": prod['name'],
        "qty": qty,
        "base_price": base_price,
        "base_subtotal": base_subtotal,
        "adj_price": adj_price,
        "adj_subtotal": adj_subtotal,
    })

conn.close()

print(f"Supplier: {sup['name']} (Price Adjustment / Tax: +{tax_rate}%)")
print(f"Total Unique Items: {len(details)}")
print(f"Total Quantity: {sum(d['qty'] for d in details)} 件\n")

print(f"{'No.':<3} | {'SKU':<10} | {'Qty':<4} | {'Base Price':<11} | {'Base Subtotal':<13} | {'Adj Price (+10.5%)':<18} | {'Adj Subtotal':<14} | {'Name'}")
print("-" * 120)

for idx, d in enumerate(details, 1):
    print(f"{idx:<3} | {d['sku']:<10} | {d['qty']:<4} | ${d['base_price']:>9.2f} | ${d['base_subtotal']:>11.2f} | ${d['adj_price']:>16.2f} | ${d['adj_subtotal']:>12.2f} | {d['name'][:30]}")

print("-" * 120)
print(f"原价总计 (不含税):      ${total_base:>12.2f}")
print(f"税费总计 (+10.5%):      ${total_base * tax_rate / 100:>12.2f}")
print(f"调整后实付总计 (含税):  ${total_adjusted:>12.2f}")

if consultar_items:
    print(f"\n注意：以下 {len(consultar_items)} 款商品原厂目录标为 CONSULTAR (待询价)，未计入金额:")
    for c_sku, c_name, c_qty in consultar_items:
        print(f"  - [{c_sku}] {c_name} (数量: {c_qty})")
