import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# KK分类列表
cur.execute("SELECT DISTINCT category FROM products WHERE supplier_id=10 AND category!='' AND is_available=1 ORDER BY category")
rows = cur.fetchall()
print(f"KK分类数: {len(rows)}")
for r in rows:
    print(f"  '{r[0]}'")

# 检查是否有 > 分隔的二级分类
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=10 AND category LIKE '%>%'")
has_sub = cur.fetchone()[0]
print(f"\n含'>'分隔的: {has_sub}")

# 检查前端API返回的分类
cur.execute("SELECT DISTINCT category FROM products WHERE category!='' AND is_available=1 ORDER BY category LIMIT 50")
all_cats = cur.fetchall()
print(f"\n全部分类(前50):")
for r in all_cats:
    print(f"  '{r[0]}'")

# 检查是否有 is_available 字段
cur.execute("SHOW COLUMNS FROM products LIKE 'is_available'")
col = cur.fetchone()
print(f"\nis_available列: {col}")

conn.close()
