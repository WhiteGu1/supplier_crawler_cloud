"""
合并"杂货"到"家居生活"，消除重复分类
- 杂货 > 日用百货  -> 家居生活 > 日用杂货
- 杂货 > 其他      -> 家居生活 > 日用杂货
- 杂货 > 食品饮料  -> 厨房用品 > 食品饮料
- 家居生活 > 家居杂货 -> 家居生活 > 日用杂货
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

MIGRATIONS = [
    ("杂货 > 日用百货",   "家居生活 > 日用杂货"),
    ("杂货 > 其他",       "家居生活 > 日用杂货"),
    ("杂货 > 食品饮料",   "厨房用品 > 食品饮料"),
    ("家居生活 > 家居杂货", "家居生活 > 日用杂货"),
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

for old_cat, new_cat in MIGRATIONS:
    cur.execute("UPDATE products SET category=%s WHERE category=%s AND is_available=1", (new_cat, old_cat))
    print(f"  {old_cat:20s} -> {new_cat:20s}  ({cur.rowcount} 条)")

conn.commit()

# 验证结果
print("\n=== 合并后 一级分类统计 ===")
cur.execute("""
    SELECT SUBSTRING_INDEX(category, ' > ', 1) as main_cat, COUNT(*) as cnt
    FROM products WHERE is_available=1 AND category!=''
    GROUP BY main_cat ORDER BY cnt DESC
""")
for r in cur.fetchall():
    print(f"  {r[1]:5d}  {r[0]}")

print("\n=== 家居生活 二级分类 ===")
cur.execute("SELECT category, COUNT(*) FROM products WHERE is_available=1 AND category LIKE '家居生活 > %' GROUP BY category ORDER BY COUNT(*) DESC")
for r in cur.fetchall():
    print(f"  {r[1]:5d}  {r[0]}")

# 确认"杂货"已消除
cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE '杂货 > %' AND is_available=1")
remaining = cur.fetchone()[0]
print(f"\n残留'杂货'分类: {remaining}")

conn.close()
