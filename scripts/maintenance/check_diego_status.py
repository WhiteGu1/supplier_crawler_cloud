import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=2 AND is_available=1")
print(f"Diego total: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=2 AND is_available=1 AND (category IS NULL OR category='' OR category='未分类')")
print(f"Diego uncategorized: {cur.fetchone()[0]}")

cur.execute("SELECT category, COUNT(*) FROM products WHERE supplier_id=2 AND is_available=1 GROUP BY category ORDER BY COUNT(*) DESC")
for r in cur.fetchall():
    print(f"  {r[1]}\t{r[0]}")

conn.close()
