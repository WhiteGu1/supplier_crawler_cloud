import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM product_categories")
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(DISTINCT product_id) FROM product_categories")
products = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM (SELECT product_id FROM product_categories GROUP BY product_id HAVING COUNT(*) > 1) x")
multi = cur.fetchone()[0]

print("=" * 50)
print("多分类全量分类完成 - 最终统计")
print("=" * 50)
print(f"多分类表总数: {total}")
print(f"覆盖商品数: {products}")
print(f"多分类商品数: {multi} ({multi*100//products}%)")
print(f"单分类商品数: {products - multi} ({(products-multi)*100//products}%)")
print(f"平均分类路径/商品: {total/products:.2f}")

print("\n一级分类分布:")
cur.execute("""
    SELECT SUBSTRING_INDEX(category, ' > ', 1) as cat1, COUNT(*) 
    FROM product_categories 
    GROUP BY cat1 
    ORDER BY COUNT(*) DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

print("\n多分类Top10:")
cur.execute("""
    SELECT product_id, GROUP_CONCAT(category SEPARATOR ' | ') 
    FROM product_categories 
    GROUP BY product_id 
    HAVING COUNT(*) > 1 
    ORDER BY COUNT(*) DESC 
    LIMIT 10
""")
for r in cur.fetchall():
    print(f"  商品{r[0]}: {r[1]}")

conn.close()
