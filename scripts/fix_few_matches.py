import pymysql

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

queries = [
    ("LH-KP028", "SELECT id, sku, name, price FROM products WHERE supplier_id=18 AND (name LIKE '%KP028%' OR name LIKE '%63819%' OR (name LIKE '%Cepillo%' AND name LIKE '%Ducha%'))"),
    ("IG3303", "SELECT id, sku, name, price FROM products WHERE supplier_id=18 AND (name LIKE '%3303%' OR name LIKE '%03034%')"),
    ("BC1116", "SELECT id, sku, name, price FROM products WHERE supplier_id=18 AND (name LIKE '%1116%' OR name LIKE '%Vincha%' AND price=3200)"),
    ("BC1127", "SELECT id, sku, name, price FROM products WHERE supplier_id=18 AND (name LIKE '%1127%' OR name LIKE '%Vincha%' AND price=1800)"),
    ("BA03A / 3009", "SELECT id, sku, name, price FROM products WHERE supplier_id=18 AND (name LIKE '%3009%' OR name LIKE '%BA03%' OR (name LIKE '%Esponja%' AND name LIKE '%Masajeador%'))"),
    ("46758", "SELECT id, sku, name, price FROM products WHERE supplier_id=18 AND (name LIKE '%46758%' OR name LIKE '%46734%')")
]

with conn.cursor() as cur:
    for label, sql in queries:
        cur.execute(sql)
        rows = cur.fetchall()
        print(f"=== {label} ===")
        for r in rows:
            print(f"  PID:{r['id']} | SKU:{r['sku']} | P:{r['price']} | {r['name'].encode('ascii','replace').decode('ascii')}")
