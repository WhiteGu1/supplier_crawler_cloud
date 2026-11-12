# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT id, sku, name, price, category FROM products WHERE supplier_id = 16 AND price > 0 ORDER BY price ASC")
rows = cur.fetchall()
print(f"Total Gaston products with price > 0: {len(rows)}")

with open("d:/projects/supplier_crawler/scripts/maintenance/gaston_priced_items.txt", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(f"[{r['id']}] SKU:{r['sku']} | ${float(r['price']):8.2f} | {r['category']} | {r['name']}\n")

print("Saved to gaston_priced_items.txt")
conn.close()
