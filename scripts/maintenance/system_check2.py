import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 1. 16条无分类商品详情
cur.execute("SELECT id, name, supplier_id FROM products WHERE category IS NULL OR category = '' LIMIT 20")
print("=== 16条无分类商品 ===")
for r in cur.fetchall():
    print(f"  id={r[0]} name={r[1]} supplier={r[2]}")

# 2. products.category 与 product_categories 不一致的样本
cur.execute("""
    SELECT p.id, p.name, p.category as old_cat, pc.category as new_cat
    FROM products p 
    JOIN product_categories pc ON p.id = pc.product_id 
    WHERE p.category != pc.category
    LIMIT 10
""")
print("\n=== products.category vs product_categories 不一致样本 ===")
for r in cur.fetchall():
    print(f"  id={r[0]} {r[1][:30]}")
    print(f"    old: {r[2]}")
    print(f"    new: {r[3]}")

# 3. 多分类过多(>3条)的商品
cur.execute("SELECT product_id, COUNT(*) as cnt FROM product_categories GROUP BY product_id HAVING cnt > 3 ORDER BY cnt DESC LIMIT 10")
print("\n=== 分类路径>3条的商品 ===")
for r in cur.fetchall():
    cur.execute("SELECT name FROM products WHERE id=%s", (r[0],))
    name = cur.fetchone()[0]
    print(f"  id={r[0]} {name[:30]} -> {r[1]}条分类")

# 4. 缺失商品(is_missing)按供应商
cur.execute("SELECT s.name, COUNT(*) FROM products p JOIN suppliers s ON p.supplier_id=s.id WHERE p.is_missing=1 GROUP BY s.id ORDER BY COUNT(*) DESC")
print("\n=== 缺失商品按供应商 ===")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

# 5. 无图商品按供应商
cur.execute("SELECT s.name, COUNT(*) FROM products p JOIN suppliers s ON p.supplier_id=s.id WHERE p.image_url IS NULL OR p.image_url='' GROUP BY s.id ORDER BY COUNT(*) DESC")
print("\n=== 无图商品按供应商 ===")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

# 6. 数据库表大小
cur.execute("SELECT table_name, table_rows, ROUND(data_length/1024/1024,1) as data_mb, ROUND(index_length/1024/1024,1) as idx_mb FROM information_schema.tables WHERE table_schema='supplier_crawler' ORDER BY data_length DESC")
print("\n=== 数据库表大小 ===")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}行, 数据{r[2]}MB, 索引{r[3]}MB")

# 7. 检查索引
cur.execute("SHOW INDEX FROM product_categories")
print("\n=== product_categories 索引 ===")
for r in cur.fetchall():
    print(f"  {r[2]}: {r[4]} (unique={r[1]})")

conn.close()
