import pymysql

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

# Load all 110 cart items
with conn.cursor() as cur:
    cur.execute('''
        SELECT c.id as cart_id, c.quantity, p.id as product_id, p.name, p.sku, p.price, p.product_url
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18
        ORDER BY c.id ASC
    ''')
    cart_items = cur.fetchall()

print(f"Total Bella cart items: {len(cart_items)}")

targets = [
    ("sku 969955", ["969955", "PINK 21", "CS6636", "CS3403", "CS5945", "6952938501767"]),
    ("sku tei18364", ["18364", "TE18364", "6971968516763", "TEI"]),
    ("sku dh80058", ["80058", "DH80058", "6902721681152", "TANGO", "SENSATIONAL"]),
    ("sku tei18383", ["18383", "TE18383", "6971968516978", "SOMBRA"]),
    ("sku dh-lso5", ["LSO5", "LS05", "8972423632101", "SELLO", "FIBRA"]),
    ("dh75114", ["75114", "DELINEADOR"]),
    ("art/405", ["405", "ALMENDRAS", "FIDELITE"]),
    ("art/403", ["403", "KERATINA", "FIDELITE"]),
    ("dh-bqy42576", ["42576", "6942349742576", "BQY", "FLOR DE LOTO"]),
    ("dh-bqy40602", ["40602", "6942349740602", "CARBON"]),
    ("dh509-222", ["222", "DH509", "KTMM", "PERSONAJES"]),
    ("k3086/k3082", ["3086", "3082", "K3086", "K3082", "6978882330161", "TEI", "SURTIDO"]),
    ("14625", ["14625", "SKALA", "MAYONESA"])
]

for label, keys in targets:
    print(f"\n==================== TARGET: {label} ====================")
    matches = []
    for it in cart_items:
        text = (it['name'] + ' ' + str(it['sku']) + ' ' + it['product_url']).upper()
        matched_keys = [k for k in keys if k.upper() in text]
        if matched_keys:
            matches.append((it, matched_keys))
            
    if not matches:
        print("  >>> No match in DB cart items <<<")
    else:
        for it, mkeys in matches:
            clean_name = it['name'].encode('ascii', 'replace').decode('ascii')
            print(f"  CartID: {it['cart_id']} | PID: {it['product_id']} | SKU: {it['sku']} | Price: ${it['price']} | Qty: {it['quantity']}")
            print(f"    Name: {clean_name}")
            print(f"    Matched keys: {mkeys}")
            print(f"    URL: {it['product_url']}")
