import pymysql

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    for q in ['75114', '18364', '80058', '42576', '40602']:
        cur.execute("SELECT id, supplier_id, sku, name, price, product_url FROM products WHERE sku LIKE %s OR name LIKE %s", (f"%{q}%", f"%{q}%"))
        rows = cur.fetchall()
        print(f"Query '{q}': {len(rows)} matches")
        for r in rows:
            clean_name = r['name'].encode('ascii', 'replace').decode('ascii')
            print(f"  Supplier {r['supplier_id']} | PID: {r['id']} | SKU: {r['sku']} | Price: {r['price']} | {clean_name}")
