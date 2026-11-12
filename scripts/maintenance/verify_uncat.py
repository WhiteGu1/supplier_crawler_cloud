import sys
sys.stdout.reconfigure(encoding='utf-8')
import pymysql

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category = ''")
print(f"无分类商品数: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM product_categories")
print(f"多分类记录数: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(DISTINCT product_id) FROM product_categories")
print(f"有分类记录的商品数: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM products")
print(f"商品总数: {cur.fetchone()[0]}")

# 检查本次处理的291条中还有多少无分类
cur.execute("""
    SELECT supplier_id, COUNT(*) as cnt 
    FROM products 
    WHERE category IS NULL OR category = ''
    GROUP BY supplier_id
    ORDER BY cnt DESC
""")
rows = cur.fetchall()
if rows:
    print(f"\n仍有无分类商品的供应商:")
    for r in rows:
        print(f"  supplier_id={r[0]}: {r[1]}条")
else:
    print("\n✅ 所有商品均已分类！")

conn.close()
