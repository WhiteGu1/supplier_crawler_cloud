# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

queries = [
    ("Jabonera (皂盒)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND (name LIKE '%jabonera%' OR name LIKE '%jabón%')"),
    ("Mamadera (奶瓶)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND (name LIKE '%mamadera%' OR name LIKE '%bebe%' OR name LIKE '%biberon%')"),
    ("Pimentero / Salero (椒盐/调味)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND (name LIKE '%pimentero%' OR name LIKE '%salero%' OR name LIKE '%molinillo%')"),
    ("Embudo (漏斗)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND name LIKE '%embudo%'"),
    ("Molde (模具/冰棒/蛋糕)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND name LIKE '%molde%'"),
    ("Colador (过滤器/滤网)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND name LIKE '%colador%'"),
    ("Rociador / Pulverizador (喷雾器)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND (name LIKE '%rociador%' OR name LIKE '%pulverizador%')"),
    ("Ganchos / Perchero (挂钩/挂架)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND (name LIKE '%gancho%' OR name LIKE '%perchero%')"),
    ("Esponja (海绵/钢丝球)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND name LIKE '%esponja%'"),
    ("Porta cepillo (牙刷架)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND (name LIKE '%cepillo%' OR name LIKE '%dentrifico%')"),
    ("Bandeja (托盘)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND name LIKE '%bandeja%'"),
    ("Balanza (电子秤)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND name LIKE '%balanza%'"),
    ("Cacerola / Sarten (锅具)", "SELECT id, sku, name, price FROM products WHERE supplier_id=16 AND (name LIKE '%cacerola%' OR name LIKE '%sarten%')"),
]

for title, q in queries:
    cur.execute(q)
    rows = cur.fetchall()
    print(f"\n=== {title} (共 {len(rows)} 件) ===")
    for r in rows[:6]:
        print(f"  [{r['id']}] SKU:{r['sku']} ${float(r['price']):.2f} | {r['name']}")

conn.close()
