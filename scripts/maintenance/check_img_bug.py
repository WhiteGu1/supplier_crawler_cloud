# -*- coding: utf-8 -*-
"""检查benabi和trapoman的无图商品"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# benabi 无图未分类
cur.execute("""
    SELECT id, name, image_local, image_url FROM products
    WHERE supplier_id=4 AND (category IS NULL OR category='')
    AND (image_local IS NULL OR image_local = '')
    ORDER BY id LIMIT 20
""")
rows = cur.fetchall()
print(f"=== benabi 无图未分类 (前20条) ===")
for r in rows:
    print(f"  id={r[0]}  name={r[1][:40]}  image_local={r[2]!r}  image_url={r[3][:80] if r[3] else 'None'}")

# 检查benabi无图商品是否有image_url
cur.execute("""
    SELECT COUNT(*) FROM products
    WHERE supplier_id=4 AND (category IS NULL OR category='')
    AND (image_local IS NULL OR image_local = '')
    AND image_url IS NOT NULL AND image_url != ''
""")
has_url = cur.fetchone()[0]
print(f"\nbenabi 无图但有image_url: {has_url}")

# Trapoman 无图未分类
cur.execute("""
    SELECT id, name, image_local, image_url FROM products
    WHERE supplier_id=3 AND (category IS NULL OR category='')
    AND (image_local IS NULL OR image_local = '')
    ORDER BY id LIMIT 20
""")
rows = cur.fetchall()
print(f"\n=== Trapoman 无图未分类 (前20条) ===")
for r in rows:
    print(f"  id={r[0]}  name={r[1][:40]}  image_local={r[2]!r}  image_url={r[3][:80] if r[3] else 'None'}")

# 检查trapoman无图商品是否有image_url
cur.execute("""
    SELECT COUNT(*) FROM products
    WHERE supplier_id=3 AND (category IS NULL OR category='')
    AND (image_local IS NULL OR image_local = '')
    AND image_url IS NOT NULL AND image_url != ''
""")
has_url2 = cur.fetchone()[0]
print(f"\nTrapoman 无图但有image_url: {has_url2}")

# 看看前端怎么取图片的 - 检查API返回
cur.execute("""
    SELECT id, name, image_local, image_url FROM products
    WHERE supplier_id=3 AND (category IS NULL OR category='')
    AND (image_local IS NULL OR image_local = '')
    AND image_url IS NOT NULL AND image_url != ''
    ORDER BY id LIMIT 5
""")
rows = cur.fetchall()
print(f"\n=== Trapoman 有url无local的样本 ===")
for r in rows:
    print(f"  id={r[0]}  name={r[1][:40]}")
    print(f"    image_local={r[2]!r}")
    print(f"    image_url={r[3][:120]}")

conn.close()
