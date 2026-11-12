import pymysql

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

queries = {
    "969955": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%969955%' OR sku LIKE '%969955%' OR name LIKE '%01767%' OR product_url LIKE '%01767%' OR (name LIKE '%PINK 21%' AND price = 1900))"
    ],
    "tei18364": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%18364%' OR sku LIKE '%18364%' OR product_url LIKE '%18364%' OR name LIKE '%16763%' OR product_url LIKE '%16763%' OR (name LIKE '%Labial%' AND name LIKE '%TEI%' AND price = 1500))"
    ],
    "dh80058": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%80058%' OR sku LIKE '%80058%' OR product_url LIKE '%80058%' OR name LIKE '%81152%' OR product_url LIKE '%81152%' OR name LIKE '%Sensational%')"
    ],
    "tei18383": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%18383%' OR sku LIKE '%18383%' OR product_url LIKE '%18383%' OR name LIKE '%16978%' OR product_url LIKE '%16978%')"
    ],
    "dh-lso5": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%LS05%' OR name LIKE '%LSO5%' OR product_url LIKE '%ls05%' OR product_url LIKE '%lso5%' OR name LIKE '%32101%' OR product_url LIKE '%32101%')"
    ],
    "dh75114": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%75114%' OR sku LIKE '%75114%' OR product_url LIKE '%75114%' OR (name LIKE '%Delineador%' AND price = 1150))"
    ],
    "art/405": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%405%' OR name LIKE '%61213%' OR product_url LIKE '%61213%' OR product_url LIKE '%405%' OR (name LIKE '%Almendras%' AND name LIKE '%Fidelite%'))"
    ],
    "art/403": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%403%' OR name LIKE '%61190%' OR product_url LIKE '%61190%' OR product_url LIKE '%403%' OR (name LIKE '%Keratina%' AND name LIKE '%Fidelite%'))"
    ],
    "dh-bqy42576": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%42576%' OR sku LIKE '%42576%' OR product_url LIKE '%42576%' OR (name LIKE '%Mascarilla%' AND name LIKE '%Bioaqua%' AND price = 600))"
    ],
    "dh-bqy40602": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%40602%' OR sku LIKE '%40602%' OR product_url LIKE '%40602%' OR (name LIKE '%Carbon%' AND name LIKE '%Bioaqua%'))"
    ],
    "dh509-222": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%DH509-222%' OR name LIKE '%509-222%' OR product_url LIKE '%509-222%')"
    ],
    "k3086/k3082": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%K3086%' OR name LIKE '%K3082%' OR name LIKE '%330161%' OR product_url LIKE '%k3086%' OR product_url LIKE '%k3082%' OR (name LIKE '%Mascarilla%' AND name LIKE '%TEI%' AND price = 550))"
    ],
    "14625": [
        "SELECT * FROM products WHERE supplier_id = 18 AND (name LIKE '%14625%' OR sku LIKE '%14625%' OR product_url LIKE '%14625%' OR (name LIKE '%Skala%' AND price = 4600))"
    ]
}

with conn.cursor() as cur:
    for target, sqls in queries.items():
        print(f"\n==================== {target.upper()} ====================")
        for sql in sqls:
            cur.execute(sql)
            rows = cur.fetchall()
            for r in rows:
                # check if in cart
                cur.execute("SELECT id, quantity FROM cart_items WHERE product_id = %s", (r['id'],))
                cart = cur.fetchone()
                cart_info = f"IN CART (CartID: {cart['id']}, Qty: {cart['quantity']})" if cart else "NOT IN CART"
                clean_name = r['name'].encode('ascii', 'replace').decode('ascii')
                print(f"  PID: {r['id']} | Web SKU: {r['sku']} | Price: ${r['price']} | {cart_info}")
                print(f"    Name: {clean_name}")
                print(f"    URL:  {r['product_url']}")
