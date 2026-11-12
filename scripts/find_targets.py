import pymysql
import re

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

targets = [
    ('969955', ['969955', '6952938501767', 'BASE DE MAQUILLAJE PINK']),
    ('tei18364', ['18364', '6971968516763', 'TE18364']),
    ('dh80058', ['80058', '6902721681152', 'SENSATIONALFSJ36']),
    ('tei18383', ['18383', '6971968516978', 'TE18383']),
    ('dh-lso5', ['LSO5', 'LS05', '8972423632101']),
    ('dh75114', ['75114']),
    ('art/405', ['405', '7798135961213', 'ALMENDRAS']),
    ('art/403', ['403', '7798135961190', 'KERATINA']),
    ('dh-bqy42576', ['42576', '6942349742576', 'BQY42576']),
    ('dh-bqy40602', ['40602', '6942349740602', 'BQY40602']),
    ('dh509-222', ['509-222', 'DH509', '222', 'KTMM']),
    ('k3086/k3082', ['K3086', 'K3082', '6978882330161', '3086', '3082']),
    ('14625', ['14625', '897042012329', 'SKALA', 'MAYONESA'])
]

with conn.cursor() as cur:
    for label, patterns in targets:
        print(f"\n==================== SEARCH FOR: {label} ====================")
        found = []
        for p in patterns:
            cur.execute('''
                SELECT p.id, p.sku, p.name, p.price, p.product_url, c.quantity as in_cart_qty, c.id as cart_id
                FROM products p
                LEFT JOIN cart_items c ON c.product_id = p.id
                WHERE p.supplier_id = 18 AND (
                    p.sku LIKE %s OR p.name LIKE %s OR p.product_url LIKE %s
                )
            ''', (f'%{p}%', f'%{p}%', f'%{p}%'))
            rows = cur.fetchall()
            for r in rows:
                if r['id'] not in [x['id'] for x in found]:
                    found.append(r)
                    
        if not found:
            print("  >>> NOT FOUND in database <<<")
        else:
            for r in found:
                clean_name = r['name'].encode('ascii', 'replace').decode('ascii')
                in_cart_str = f"In Cart: Qty={r['in_cart_qty']} (Cart ID {r['cart_id']})" if r['in_cart_qty'] else "NOT in cart"
                print(f"  PID: {r['id']} | DB SKU: {r['sku']} | Price: ${r['price']} | {in_cart_str}")
                print(f"    Name: {clean_name}")
                print(f"    URL:  {r['product_url']}")
