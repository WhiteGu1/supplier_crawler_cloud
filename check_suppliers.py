# -*- coding: utf-8 -*-
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT s.id, s.name, COUNT(*) as total,
           SUM(CASE WHEN p.category IS NULL OR p.category='' THEN 1 ELSE 0 END) as uncategorized,
           SUM(CASE WHEN (p.category IS NULL OR p.category='') AND p.image_local IS NOT NULL AND p.image_local != '' THEN 1 ELSE 0 END) as img_uncat
    FROM products p
    JOIN suppliers s ON p.supplier_id = s.id
    GROUP BY s.id, s.name
    ORDER BY s.id
""")
rows = cur.fetchall()
print(f"{'SID':<5} {'Supplier':<15} {'Total':<7} {'Uncat':<7} {'ImgUncat':<8}")
print("-" * 45)
for r in rows:
    print(f"{r[0]:<5} {r[1]:<15} {r[2]:<7} {r[3]:<7} {r[4]:<8}")

conn.close()
