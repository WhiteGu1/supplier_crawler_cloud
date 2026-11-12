# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

from find_and_add_gaston_favs import MATCH_LIST

TAX = 1.105 # 10.5% 额外税

print(f"Checking {len(MATCH_LIST)} matches with Gaston 10.5% tax...")
passed = []
failed = []

for gid, tid, note in MATCH_LIST:
    cur.execute("SELECT id, sku, name, price FROM products WHERE id = %s", (gid,))
    g = cur.fetchone()
    cur.execute("SELECT id, sku, name, price FROM products WHERE id = %s", (tid,))
    t = cur.fetchone()
    
    g_raw = float(g['price'])
    g_adj = g_raw * TAX
    t_price = float(t['price'])
    max_allowed = t_price * 1.10
    diff_pct = ((g_adj - t_price) / t_price) * 100
    
    item_info = {
        'gid': gid, 'gsku': g['sku'], 'gname': g['name'],
        'g_raw': g_raw, 'g_adj': g_adj,
        'tid': tid, 'tname': t['name'], 't_price': t_price,
        'max_allowed': max_allowed, 'diff_pct': diff_pct,
        'note': note
    }
    
    if g_adj <= max_allowed:
        passed.append(item_info)
    else:
        failed.append(item_info)

print(f"\n=== PASSED ({len(passed)} items) ===")
for p in passed:
    print(f"[PASS] {p['gsku']:10s} | Raw:${p['g_raw']:7.2f} -> Adj(+10.5%):${p['g_adj']:7.2f} | Trapoman ${p['t_price']:7.2f} (上限${p['max_allowed']:7.2f}) | {p['diff_pct']:+6.1f}% | {p['gname']}")

print(f"\n=== FAILED / EXCEEDED (+10.5% tax exceeds 10% limit) ({len(failed)} items) ===")
for f in failed:
    print(f"[FAIL] {f['gsku']:10s} | Raw:${f['g_raw']:7.2f} -> Adj(+10.5%):${f['g_adj']:7.2f} | Trapoman ${f['t_price']:7.2f} (上限${f['max_allowed']:7.2f}) | {f['diff_pct']:+6.1f}% | {f['gname']}")

conn.close()
