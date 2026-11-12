# -*- coding: utf-8 -*-
import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

for sid, name in [(21, "Randy"), (22, "nativo home")]:
    cur.execute("""
        SELECT category, count(*) as cnt
        FROM products
        WHERE supplier_id = %s AND is_available = 1 AND is_missing = 0
        GROUP BY category
        ORDER BY cnt DESC
    """, (sid,))
    rows = cur.fetchall()
    print(f"=== Supplier {sid} ({name}): {len(rows)} distinct categories ===")
    for r in rows:
        print(f"  {r['cnt']:4d} | {r['category']}")

conn.close()
