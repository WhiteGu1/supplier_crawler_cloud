import sys
sys.stdout.reconfigure(encoding='utf-8')
import pymysql

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# 1. 总体统计
cur.execute("SELECT COUNT(*) as total FROM products")
print(f"商品总数: {cur.fetchone()['total']}")

cur.execute("SELECT COUNT(*) as cnt FROM products WHERE is_new = 1")
print(f"is_new=1 新商品数: {cur.fetchone()['cnt']}")

cur.execute("SELECT COUNT(*) as cnt FROM products WHERE category IS NULL OR category = ''")
print(f"无分类商品数: {cur.fetchone()['cnt']}")

# 2. is_new=1 各种分类情况
cur.execute("""
    SELECT 
        SUM(CASE WHEN category IS NULL OR category = '' THEN 1 ELSE 0 END) as no_cat,
        SUM(CASE WHEN category IS NOT NULL AND category != '' THEN 1 ELSE 0 END) as has_cat,
        COUNT(*) as total
    FROM products WHERE is_new = 1
""")
row = cur.fetchone()
print(f"\nis_new=1 详情: total={row['total']} 有分类={row['has_cat']} 无分类={row['no_cat']}")

# 3. 按供应商分组看is_new=1
cur.execute("""
    SELECT supplier_id, COUNT(*) as cnt 
    FROM products 
    WHERE is_new = 1
    GROUP BY supplier_id
    ORDER BY cnt DESC
""")
print("\nis_new=1 按供应商分布:")
for r in cur.fetchall():
    print(f"  supplier_id={r['supplier_id']}: {r['cnt']}条")

# 4. 看看最近添加的商品
cur.execute("""
    SELECT id, supplier_id, name, sku, category, is_new, created_at
    FROM products 
    WHERE is_new = 1
    ORDER BY id DESC
    LIMIT 20
""")
print("\n最近20条is_new=1商品:")
for r in cur.fetchall():
    cat = r['category'] or '(空)'
    print(f"  id={r['id']} sup={r['supplier_id']} new={r['is_new']} cat={cat} name={r['name'][:50]}")

# 5. 看看无分类商品
cur.execute("""
    SELECT id, supplier_id, name, sku, is_new
    FROM products 
    WHERE category IS NULL OR category = ''
    ORDER BY id
""")
print(f"\n无分类商品:")
for r in cur.fetchall():
    print(f"  id={r['id']} sup={r['supplier_id']} new={r['is_new']} name={r['name'][:60]} sku={r['sku']}")

conn.close()
