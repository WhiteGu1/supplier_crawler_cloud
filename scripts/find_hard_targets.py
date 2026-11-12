import pymysql

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

queries = {
    "tei18364 (Barcode 6971968516763, Price 1500)": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (price = 1500 AND (name LIKE '%Labial%' OR name LIKE '%TEI%' OR name LIKE '%Barra%'))",
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%16763%' OR sku LIKE '%16763%' OR product_url LIKE '%16763%')",
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%18364%' OR sku LIKE '%18364%')"
    ],
    "dh80058 (Barcode 6902721681152, Price 1100, MASCARA MINI TANGO)": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%Tango%' OR name LIKE '%Sensational%' OR price = 1100 AND name LIKE '%Mascara%')",
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%681152%' OR name LIKE '%81152%' OR sku LIKE '%81152%' OR product_url LIKE '%81152%')",
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%DH80058%' OR name LIKE '%80058%')"
    ],
    "dh75114 (Price 1150, DELINEADOR LIQUIDO)": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%Delineador%' AND price BETWEEN 1100 AND 1200)",
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%75114%' OR sku LIKE '%75114%' OR product_url LIKE '%75114%')"
    ],
    "dh-bqy42576 (Barcode 6942349742576, Price 600, MASCARILLA FACIAL)": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%Mascarilla%' AND price = 600 AND name LIKE '%Bioaqua%')",
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%42576%' OR sku LIKE '%42576%' OR product_url LIKE '%42576%')"
    ],
    "dh-bqy40602 (Barcode 6942349740602, Price 600, MASCARILLA FACIAL)": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%40602%' OR sku LIKE '%40602%' OR product_url LIKE '%40602%')",
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%Mascarilla%' AND price = 600)"
    ]
}

with conn.cursor() as cur:
    for cat, sqls in queries.items():
        print(f"\n==================== {cat} ====================")
        seen = set()
        for q in sqls:
            cur.execute(q)
            for r in cur.fetchall():
                if r['id'] not in seen:
                    seen.add(r['id'])
                    cur.execute("SELECT id, quantity FROM cart_items WHERE product_id = %s", (r['id'],))
                    cart = cur.fetchone()
                    cart_str = f"IN CART (CartID: {cart['id']}, Qty: {cart['quantity']})" if cart else "NOT IN CART"
                    clean_name = r['name'].encode('ascii', 'replace').decode('ascii')
                    print(f"  PID: {r['id']} | Web SKU: {r['sku']} | Price: ${r['price']} | {cart_str}")
                    print(f"    Name: {clean_name}")
                    print(f"    URL:  {r['product_url']}")
