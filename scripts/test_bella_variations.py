import pymysql
import json
import urllib.request

conn = pymysql.connect(host='localhost', user='root', password='admin123', database='supplier_crawler', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute('''
        SELECT c.id, c.product_id, c.quantity, p.name, p.sku, p.price, p.product_url, p.package_qty, p.sub_pack_qty
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18
        ORDER BY c.id ASC
        LIMIT 10
    ''')
    rows = cur.fetchall()

for r in rows:
    wc_id = r['sku']
    try:
        req = urllib.request.Request(f'https://bellacentral.com.ar/wp-json/wc/store/v1/products/{wc_id}', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            p = json.loads(resp.read().decode('utf-8'))
            print(f"ID {wc_id} ({r['quantity']} pcs, pkg={r['package_qty']}, sub={r['sub_pack_qty']}): type={p.get('type')}, in_stock={p.get('is_in_stock')}")
            for v in p.get('variations', []):
                attrs = [a.get('value') for a in v.get('attributes', [])]
                print(f"   var {v['id']}: {attrs}")
    except Exception as e:
        print(f"ID {wc_id} err:", e)
