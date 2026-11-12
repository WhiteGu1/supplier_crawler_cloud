import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute("""
    SELECT s.name,
           COUNT(*) AS total,
           SUM(CASE WHEN p.category IS NOT NULL AND p.category != '' THEN 1 ELSE 0 END) AS classified,
           SUM(CASE WHEN (p.category IS NULL OR p.category = '') AND p.image_local IS NOT NULL AND p.image_local != '' THEN 1 ELSE 0 END) AS rem_img,
           SUM(CASE WHEN (p.category IS NULL OR p.category = '') AND (p.image_local IS NULL OR p.image_local = '') THEN 1 ELSE 0 END) AS rem_noimg
    FROM products p JOIN suppliers s ON p.supplier_id=s.id
    WHERE p.is_available=1
    GROUP BY s.id, s.name ORDER BY s.name
""")
print(f"{'Supplier':<12} {'Total':>6} {'Done':>6} {'ImgRem':>6} {'NoImg':>6}")
print("-"*40)
for name,total,done,ri,rn in cur.fetchall():
    print(f"{name:<12} {total:>6} {done:>6} {ri:>6} {rn:>6}")
conn.close()
