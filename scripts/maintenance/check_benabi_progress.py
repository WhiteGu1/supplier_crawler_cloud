import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# benabi 已分类数量
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND category IS NOT NULL AND category != ''")
done = cur.fetchone()[0]

# benabi 剩余有图未分类
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining_img = cur.fetchone()[0]

# benabi 总剩余未分类
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='')")
remaining_total = cur.fetchone()[0]

print(f"benabi 已分类: {done}")
print(f"benabi 剩余有图未分类: {remaining_img}")
print(f"benabi 总剩余未分类(含无图): {remaining_total}")

# 各供应商未分类统计
cur.execute("""
    SELECT s.name, COUNT(*) as cnt 
    FROM products p 
    JOIN suppliers s ON p.supplier_id = s.id 
    WHERE (p.category IS NULL OR p.category = '') 
    GROUP BY p.supplier_id, s.name 
    ORDER BY cnt DESC
""")
print("\n各供应商未分类:")
for name, cnt in cur.fetchall():
    print(f"  {name}: {cnt}")

conn.close()
