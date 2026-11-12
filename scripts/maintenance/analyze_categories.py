import sys
sys.stdout.reconfigure(encoding='utf-8')
import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

# 1. 所有分类路径及其商品数
cur.execute("""
SELECT category, COUNT(*) as cnt 
FROM product_categories 
GROUP BY category 
ORDER BY category
""")
rows = cur.fetchall()
print(f'=== 全部分类路径 ({len(rows)}条) ===')
for r in rows:
    print(f'{r["cnt"]:4d}  {r["category"]}')

# 2. products.category 分布
cur.execute("""
SELECT category, COUNT(*) as cnt 
FROM products 
WHERE category IS NOT NULL AND category != ''
GROUP BY category 
ORDER BY cnt DESC
""")
rows2 = cur.fetchall()
print(f'\n=== products.category 分布 ({len(rows2)}条) ===')
for r in rows2:
    print(f'{r["cnt"]:4d}  {r["category"]}')

# 3. 一级分类列表
cur.execute("""
SELECT DISTINCT SUBSTRING_INDEX(category, ' > ', 1) as l1 
FROM product_categories 
ORDER BY l1
""")
l1s = [r['l1'] for r in cur.fetchall()]
print(f'\n=== 一级分类 ({len(l1s)}个) ===')
for l1 in l1s:
    print(f'  {l1}')

conn.close()