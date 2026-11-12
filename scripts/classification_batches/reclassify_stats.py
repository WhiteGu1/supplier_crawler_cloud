# -*- coding: utf-8 -*-
"""统计全量重分类的规模"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 按供应商统计有图商品
cur.execute("""
    SELECT s.id, s.name, COUNT(*) as total,
           SUM(CASE WHEN p.image_local IS NOT NULL AND p.image_local != '' THEN 1 ELSE 0 END) as has_img
    FROM products p
    JOIN suppliers s ON p.supplier_id = s.id
    WHERE p.category IS NOT NULL AND p.category != ''
    GROUP BY s.id, s.name
    ORDER BY s.id
""")
rows = cur.fetchall()
print(f"{'SID':<5} {'Supplier':<15} {'Total':<7} {'HasImg':<7} {'Batches':<8}")
print("-" * 45)
grand_total = 0
grand_img = 0
for r in rows:
    batches = (r[3] + 9) // 10
    print(f"{r[0]:<5} {r[1]:<15} {r[2]:<7} {r[3]:<7} {batches:<8}")
    grand_total += r[2]
    grand_img += r[3]

total_batches = (grand_img + 9) // 10
waves = (total_batches + 4) // 5
print(f"\n总计: {grand_total} 条, 有图: {grand_img} 条")
print(f"需要 {total_batches} 批（每批10张），{waves} 波（每波5批并行）")

# Dsaza无图的5条
cur.execute("""
    SELECT id, name FROM products
    WHERE supplier_id=6 AND (category IS NULL OR category='')
""")
for r in cur.fetchall():
    print(f"无图未分类: id={r[0]} name={r[1]}")

conn.close()
