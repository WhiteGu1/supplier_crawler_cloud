import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute("""
    SELECT id, name, image_local
    FROM products
    WHERE supplier_id=3 AND (category IS NULL OR category='')
      AND is_available=1
    ORDER BY id
""")
rows = cur.fetchall()
print(f"Trapoman unclassified total: {len(rows)}")
with_img = sum(1 for r in rows if r[2])
no_img = len(rows) - with_img
print(f"with_img: {with_img}, no_img: {no_img}")
print()
for i, (pid, name, img) in enumerate(rows):
    has_img = "Y" if img else "N"
    print(f"{i+1}\t{pid}\t{has_img}\t{name}")

conn.close()
