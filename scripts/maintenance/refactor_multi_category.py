"""重构多分类表：去掉is_primary，所有分类路径并列"""
import pymysql

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 1. 去掉 is_primary 列（如果存在）
cur.execute("SHOW COLUMNS FROM product_categories LIKE 'is_primary'")
if cur.fetchone():
    cur.execute("ALTER TABLE product_categories DROP COLUMN is_primary")
    print("已删除 is_primary 列")
else:
    print("is_primary 列不存在，跳过")

# 2. 确认表结构
cur.execute("DESC product_categories")
for r in cur.fetchall():
    print(r)

# 3. 统计当前数据
cur.execute("SELECT COUNT(*) FROM product_categories")
print(f"\n关联表总数: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(DISTINCT product_id) FROM product_categories")
print(f"有分类的商品数: {cur.fetchone()[0]}")

# 4. 检查是否有重复（同一商品同一分类路径多次记录）
cur.execute("SELECT product_id, category, COUNT(*) as cnt FROM product_categories GROUP BY product_id, category HAVING cnt > 1 LIMIT 5")
dups = cur.fetchall()
print(f"重复记录: {len(dups)} 条" if dups else "无重复记录")

conn.commit()
conn.close()
