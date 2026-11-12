import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT category, COUNT(*) FROM products WHERE is_available=1 GROUP BY category ORDER BY COUNT(*) DESC LIMIT 60")
for r in cur.fetchall():
    print(f'{r[1]:5d}  {r[0]}')
print()
# 检查是否有 > 分隔的分类
cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE '%>%'")
print(f"含 > 分隔的分类商品数: {cur.fetchone()[0]}")
conn.close()
