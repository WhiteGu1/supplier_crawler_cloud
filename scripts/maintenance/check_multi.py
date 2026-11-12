import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT product_id, GROUP_CONCAT(category SEPARATOR ' | ') FROM product_categories GROUP BY product_id HAVING COUNT(*) > 1 LIMIT 10")
for r in cur.fetchall():
    print(f"  商品{r[0]}: {r[1]}")
conn.close()
