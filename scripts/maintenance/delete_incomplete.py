# -*- coding: utf-8 -*-
"""删除无图残缺数据 - name仅为供应商名，无图片URL"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 先统计各供应商要删除的数量
cur.execute("""
    SELECT s.name, COUNT(*) 
    FROM products p 
    JOIN suppliers s ON p.supplier_id = s.id 
    WHERE (p.category IS NULL OR p.category = '')
    AND (p.image_local IS NULL OR p.image_local = '')
    AND (p.image_url IS NULL OR p.image_url = '')
    GROUP BY s.id, s.name
    ORDER BY s.id
""")
rows = cur.fetchall()
print("将删除以下残缺数据：")
total = 0
for name, cnt in rows:
    print(f"  {name}: {cnt} 条")
    total += cnt
print(f"  总计: {total} 条")

# 删除（先删price_history外键，再删products）
cur.execute("""
    DELETE ph FROM price_history ph
    INNER JOIN products p ON ph.product_id = p.id
    WHERE (p.category IS NULL OR p.category = '')
    AND (p.image_local IS NULL OR p.image_local = '')
    AND (p.image_url IS NULL OR p.image_url = '')
""")
ph_deleted = cur.rowcount
print(f"\n删除 price_history: {ph_deleted} 条")

cur.execute("""
    DELETE FROM products
    WHERE (category IS NULL OR category = '')
    AND (image_local IS NULL OR image_local = '')
    AND (image_url IS NULL OR image_url = '')
""")
prod_deleted = cur.rowcount
print(f"删除 products: {prod_deleted} 条")

conn.commit()

# 验证最终状态
cur.execute("""
    SELECT s.id, s.name, COUNT(*) as total,
           SUM(CASE WHEN p.category IS NULL OR p.category='' THEN 1 ELSE 0 END) as uncat
    FROM products p
    JOIN suppliers s ON p.supplier_id = s.id
    GROUP BY s.id, s.name
    ORDER BY s.id
""")
rows = cur.fetchall()
print(f"\n{'SID':<5} {'Supplier':<15} {'Total':<7} {'Uncat':<7}")
print("-" * 35)
for r in rows:
    print(f"{r[0]:<5} {r[1]:<15} {r[2]:<7} {r[3]:<7}")

cur.execute("SELECT COUNT(*) FROM products")
grand_total = cur.fetchone()[0]
print(f"\n商品总数: {grand_total}")

conn.close()
