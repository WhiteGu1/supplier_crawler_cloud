import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM products")
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1 AND is_missing=0")
available = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM products WHERE is_missing=1")
missing = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM products WHERE image_url IS NULL OR image_url = ''")
no_img = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category = ''")
no_cat = cur.fetchone()[0]
print("=== 商品总览 ===")
print(f"总商品: {total}, 可用: {available}, 缺失: {missing}, 无图: {no_img}, 无分类(products.category): {no_cat}")

cur.execute("SELECT COUNT(*) FROM product_categories")
pc_total = cur.fetchone()[0]
cur.execute("SELECT COUNT(DISTINCT product_id) FROM product_categories")
pc_products = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM (SELECT product_id FROM product_categories GROUP BY product_id HAVING COUNT(*) > 1) x")
pc_multi = cur.fetchone()[0]
cur.execute("SELECT COUNT(DISTINCT category) FROM product_categories")
pc_paths = cur.fetchone()[0]
print(f"\n=== 多分类表 ===")
print(f"总路径: {pc_total}, 覆盖商品: {pc_products}, 多分类商品: {pc_multi}({pc_multi*100//pc_products}%), 去重分类: {pc_paths}")

cur.execute("SELECT s.name, COUNT(p.id) FROM products p JOIN suppliers s ON p.supplier_id=s.id GROUP BY s.id ORDER BY COUNT(p.id) DESC")
print(f"\n=== 供应商分布 ===")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

cur.execute("SELECT COUNT(*) FROM product_categories WHERE category NOT LIKE '%%>%%'")
bad = cur.fetchone()[0]
print(f"\n异常分类(无>): {bad}")

cur.execute("SELECT COUNT(*) FROM (SELECT product_id, category FROM product_categories GROUP BY product_id, category HAVING COUNT(*) > 1) x")
dup = cur.fetchone()[0]
print(f"重复分类(同商品同分类多条): {dup}")

cur.execute("SELECT COUNT(*) FROM products p WHERE p.category IS NOT NULL AND p.category != '' AND NOT EXISTS (SELECT 1 FROM product_categories pc WHERE pc.product_id = p.id)")
orphan = cur.fetchone()[0]
print(f"有category但不在product_categories表: {orphan}")

# products.category 是否与 product_categories 第一条一致
cur.execute("""
    SELECT COUNT(*) FROM products p 
    JOIN product_categories pc ON p.id = pc.product_id 
    WHERE p.category != pc.category AND pc.category IS NOT NULL
""")
mismatch = cur.fetchone()[0]
print(f"products.category与product_categories不一致: {mismatch}")

# 一级分类分布
print("\n=== 一级分类分布(多分类表) ===")
cur.execute("""
    SELECT SUBSTRING_INDEX(category, ' > ', 1) as cat1, COUNT(*) 
    FROM product_categories 
    GROUP BY cat1 ORDER BY COUNT(*) DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

# 检查后端API状态
import requests
try:
    r = requests.get("http://127.0.0.1:8100/api/products?page=1&page_size=1", timeout=5)
    print(f"\n=== 后端API ===")
    print(f"端口8100: {r.status_code}")
except:
    print(f"\n=== 后端API ===")
    print("端口8100: 未响应")

# 检查缓存目录大小
import os
cache_dir = r"D:\projects\supplier_crawler\classify_cache"
if os.path.exists(cache_dir):
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(cache_dir):
        for f in files:
            fp = os.path.join(root, f)
            total_size += os.path.getsize(fp)
            file_count += 1
    print(f"\n=== 缓存目录 ===")
    print(f"文件数: {file_count}, 总大小: {total_size // 1024 // 1024}MB")

conn.close()
