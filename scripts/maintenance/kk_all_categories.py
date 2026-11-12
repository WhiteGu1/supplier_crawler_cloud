import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT category, COUNT(*) as cnt 
    FROM products WHERE supplier_id=10 
    GROUP BY category ORDER BY cnt DESC
""")
rows = cur.fetchall()
print(f"KK全部分类 ({len(rows)} 个):")
for r in rows:
    print(f"  '{r[0]}' -> {r[1]}")

conn.close()
