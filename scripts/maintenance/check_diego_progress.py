import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# Diego = supplier_id=5
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=5")
total = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=5 AND category IS NOT NULL AND category != ''")
classified = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=5 AND (category IS NULL OR category = '')")
unclassified = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=5 AND (image_path IS NULL OR image_path = '')")
no_image = cur.fetchone()[0]

print(f"Diego (supplier_id=5) 进度:")
print(f"  总数: {total}")
print(f"  已分类: {classified}")
print(f"  未分类: {unclassified}")
print(f"  无图: {no_image}")
print(f"  有图未分类: {unclassified - no_image}")

# 查看未分类商品的ID范围
cur.execute("SELECT MIN(id), MAX(id) FROM products WHERE supplier_id=5 AND (category IS NULL OR category = '')")
row = cur.fetchone()
if row[0]:
    print(f"  未分类ID范围: {row[0]} - {row[1]}")

    # 查看前20个未分类ID
    cur.execute("SELECT id, name, image_path FROM products WHERE supplier_id=5 AND (category IS NULL OR category = '') ORDER BY id LIMIT 20")
    rows = cur.fetchall()
    print(f"\n  前20个未分类:")
    for r in rows:
        has_img = "有图" if r[2] else "无图"
        print(f"    ID:{r[0]} [{has_img}] {r[1][:50] if r[1] else 'N/A'}")
else:
    print("  全部已分类！")

conn.close()
