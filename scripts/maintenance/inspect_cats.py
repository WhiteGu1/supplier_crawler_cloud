import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 现有分类全量
cur.execute("SELECT DISTINCT category FROM products WHERE is_available=1 AND category IS NOT NULL AND category!='' ORDER BY category")
cats = [r[0] for r in cur.fetchall()]
print("=== 现有分类列表 ===")
for c in cats:
    print(c)

print(f"\n总计: {len(cats)} 个分类")

# 统计各分类商品数
cur.execute("""
    SELECT category, COUNT(*) as cnt 
    FROM products 
    WHERE is_available=1 AND category IS NOT NULL AND category!=''
    GROUP BY category 
    ORDER BY cnt DESC
""")
print("\n=== 分类商品数(前20) ===")
for cat, cnt in cur.fetchall():
    print(f"  {cat}: {cnt}")

# 看看商品数据结构
cur.execute("SELECT id, name, sku, category, brand, supplier_name, price FROM products WHERE is_available=1 LIMIT 5")
print("\n=== 商品数据结构示例 ===")
for r in cur.fetchall():
    print(f"  id={r[0]}, name={r[1]}, sku={r[2]}, category={r[3]}, brand={r[4]}, supplier={r[5]}, price={r[6]}")

# 总数
cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1")
total = cur.fetchone()[0]
print(f"\n商品总数: {total}")

# 未分类数量
cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1 AND (category IS NULL OR category='')")
uncat = cur.fetchone()[0]
print(f"未分类: {uncat}")

conn.close()
