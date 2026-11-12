import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 找不同一级分类下的同名二级
cur.execute("""
    SELECT DISTINCT 
           SUBSTRING_INDEX(category, ' > ', 1) as l1,
           SUBSTRING_INDEX(SUBSTRING_INDEX(category, ' > ', 2), ' > ', -1) as l2
    FROM products 
    WHERE is_available=1 AND category LIKE '% > %'
    ORDER BY l2, l1
""")
rows = cur.fetchall()

# 按二级名分组
from collections import defaultdict
l2_groups = defaultdict(list)
for l1, l2 in rows:
    l2_groups[l2].append(l1)

print("=== 重名二级分类 ===")
for l2, l1s in sorted(l2_groups.items()):
    if len(l1s) > 1:
        print(f"\n  「{l2}」 出现在: {', '.join(l1s)}")
        for l1 in l1s:
            cat = f"{l1} > {l2}"
            cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1 AND category=%s OR category LIKE %s", (cat, cat + ' > %'))
            cnt = cur.fetchone()[0]
            print(f"    {l1} > {l2}: {cnt}条")

conn.close()
