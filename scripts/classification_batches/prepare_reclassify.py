# -*- coding: utf-8 -*-
"""统计各供应商分类情况，为全量重分类做准备"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT s.id, s.name, COUNT(*) as total,
           SUM(CASE WHEN p.category IS NULL OR p.category='' THEN 1 ELSE 0 END) as uncat,
           SUM(CASE WHEN p.image_local IS NOT NULL AND p.image_local != '' THEN 1 ELSE 0 END) as has_img
    FROM products p
    JOIN suppliers s ON p.supplier_id = s.id
    GROUP BY s.id, s.name
    ORDER BY s.id
""")
rows = cur.fetchall()
print(f"{'SID':<5} {'Supplier':<15} {'Total':<7} {'Uncat':<7} {'HasImg':<7} {'Batches':<8}")
print("-" * 52)
grand_total = 0
grand_batches = 0
for r in rows:
    batches = (r[2] + 9) // 10
    print(f"{r[0]:<5} {r[1]:<15} {r[2]:<7} {r[3]:<7} {r[4]:<7} {batches:<8}")
    grand_total += r[2]
    grand_batches += batches

print(f"\n总计: {grand_total} 条, {grand_batches} 批")
print(f"每波5批并行, 需要 {grand_batches // 5} 波")

# 查看现有分类分布
cur.execute("""
    SELECT category, COUNT(*) FROM products
    WHERE category IS NOT NULL AND category != ''
    GROUP BY category ORDER BY COUNT(*) DESC
""")
cats = cur.fetchall()
print(f"\n现有分类分布:")
for cat, cnt in cats:
    print(f"  {cat}: {cnt}")

conn.close()
