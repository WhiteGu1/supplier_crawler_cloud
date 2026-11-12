import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT s.id, s.name, 
           COUNT(p.id) as total,
           SUM(CASE WHEN p.category IS NOT NULL AND p.category != '' THEN 1 ELSE 0 END) as classified,
           SUM(CASE WHEN p.category IS NULL OR p.category = '' THEN 1 ELSE 0 END) as unclassified,
           SUM(CASE WHEN p.image_local IS NOT NULL AND p.image_local != '' AND (p.category IS NULL OR p.category = '') THEN 1 ELSE 0 END) as has_img_unclassified
    FROM suppliers s
    LEFT JOIN products p ON s.id = p.supplier_id
    GROUP BY s.id, s.name
    ORDER BY s.id
""")
rows = cur.fetchall()
print(f"各供应商分类进度:")
print(f"{'ID':>3} {'名称':<20} {'总数':>6} {'已分类':>6} {'未分类':>6} {'有图未分类':>8}")
print("-" * 60)
total_unclassified = 0
total_has_img = 0
for r in rows:
    print(f"{r[0]:>3} {r[1]:<20} {r[2]:>6} {r[3]:>6} {r[4]:>6} {r[5]:>8}")
    total_unclassified += r[4] or 0
    total_has_img += r[5] or 0

print(f"\n总计未分类: {total_unclassified}")
print(f"其中有图未分类: {total_has_img}")

conn.close()
