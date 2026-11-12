# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

from find_and_add_gaston_favs import MATCH_LIST

TAX = 1.105
remaining = [m for m in MATCH_LIST if m[0] not in (38034, 37817)]

print(f"=== 保留并通过严格税后检验的 {len(remaining)} 款商品 ===")
for gid, tid, note in remaining:
    cur.execute("SELECT sku, name, price FROM products WHERE id=%s", (gid,))
    g = cur.fetchone()
    cur.execute("SELECT sku, name, price FROM products WHERE id=%s", (tid,))
    t = cur.fetchone()
    
    g_raw = float(g['price'])
    g_adj = g_raw * TAX
    t_price = float(t['price'])
    diff = ((g_adj - t_price) / t_price) * 100
    print(f"{g['sku']:10s} | 原价:${g_raw:7.2f} -> 税后(+10.5%):${g_adj:7.2f} | Trapoman ${t_price:7.2f} | 相比T价: {diff:+6.1f}% | {note}")

conn.close()
