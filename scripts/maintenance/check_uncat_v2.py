import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT id, supplier_id, name, category FROM products WHERE category IS NULL OR category=''")
rows = cur.fetchall()
print('Remaining uncategorized:', len(rows))
for r in rows[:20]:
    print(r)
conn.close()