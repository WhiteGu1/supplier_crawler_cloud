import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# KK总体情况
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=10")
total = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=10 AND category IS NOT NULL AND category != ''")
classified = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=10 AND image_local IS NOT NULL AND image_local != ''")
has_img = cur.fetchone()[0]

print(f"KK (supplier_id=10):")
print(f"  总数: {total}")
print(f"  已分类: {classified}")
print(f"  有图: {has_img}")
print(f"  无图: {total - has_img}")

# 分类分布
cur.execute("SELECT category, COUNT(*) as cnt FROM products WHERE supplier_id=10 GROUP BY category ORDER BY cnt DESC")
rows = cur.fetchall()
print(f"\n分类分布 ({len(rows)} 个分类):")
for r in rows:
    print(f"  {r[0] or '(空)':<20} {r[1]:>5}")

# ID范围
cur.execute("SELECT MIN(id), MAX(id) FROM products WHERE supplier_id=10")
id_range = cur.fetchone()
print(f"\nID范围: {id_range[0]} - {id_range[1]}")

# 有图商品抽样
cur.execute("SELECT id, name, category, image_local FROM products WHERE supplier_id=10 AND image_local IS NOT NULL AND image_local != '' ORDER BY id LIMIT 10")
rows = cur.fetchall()
print(f"\n前10条有图商品:")
for r in rows:
    print(f"  ID:{r[0]} [{r[2] or '无'}] {r[1][:50] if r[1] else 'N/A'}")

conn.close()
