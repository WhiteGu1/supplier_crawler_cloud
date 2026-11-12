import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=5")
total = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=5 AND category IS NOT NULL AND category != ''")
classified = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=5 AND (category IS NULL OR category = '')")
unclassified = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=5 AND (image_local IS NULL OR image_local = '')")
no_image = cur.fetchone()[0]

print(f"Diego (supplier_id=5) 进度:")
print(f"  总数: {total}")
print(f"  已分类: {classified}")
print(f"  未分类: {unclassified}")
print(f"  无图: {no_image}")
print(f"  有图未分类: {unclassified - no_image}")

cur.execute("SELECT MIN(id), MAX(id) FROM products WHERE supplier_id=5 AND (category IS NULL OR category = '')")
row = cur.fetchone()
if row[0]:
    print(f"  未分类ID范围: {row[0]} - {row[1]}")
    cur.execute("SELECT id, name, image_local FROM products WHERE supplier_id=5 AND (category IS NULL OR category = '') AND image_local IS NOT NULL AND image_local != '' ORDER BY id LIMIT 25")
    rows = cur.fetchall()
    print(f"\n  前25个有图未分类:")
    for r in rows:
        print(f"    ID:{r[0]} {r[1][:60] if r[1] else 'N/A'} | {r[2][:60] if r[2] else 'N/A'}")
else:
    print("  全部已分类！")

conn.close()
