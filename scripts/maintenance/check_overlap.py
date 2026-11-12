import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

print("=== 家居生活 ===")
cur.execute("SELECT category, COUNT(*) FROM products WHERE is_available=1 AND category LIKE '家居生活 > %' GROUP BY category ORDER BY COUNT(*) DESC")
for r in cur.fetchall():
    print(f"  {r[1]:5d}  {r[0]}")

print("\n=== 杂货 ===")
cur.execute("SELECT category, COUNT(*) FROM products WHERE is_available=1 AND category LIKE '杂货 > %' GROUP BY category ORDER BY COUNT(*) DESC")
for r in cur.fetchall():
    print(f"  {r[1]:5d}  {r[0]}")

# 看看杂货下的商品样本
print("\n=== 杂货 > 日用百货 商品样本 ===")
cur.execute("SELECT name FROM products WHERE is_available=1 AND category='杂货 > 日用百货' LIMIT 20")
for r in cur.fetchall():
    print(f"  {r[0]}")

print("\n=== 杂货 > 其他 商品样本 ===")
cur.execute("SELECT name FROM products WHERE is_available=1 AND category='杂货 > 其他' LIMIT 20")
for r in cur.fetchall():
    print(f"  {r[0]}")

print("\n=== 杂货 > 食品饮料 商品样本 ===")
cur.execute("SELECT name FROM products WHERE is_available=1 AND category='杂货 > 食品饮料' LIMIT 10")
for r in cur.fetchall():
    print(f"  {r[0]}")

print("\n=== 家居生活 > 家居杂货 商品样本 ===")
cur.execute("SELECT name FROM products WHERE is_available=1 AND category='家居生活 > 家居杂货' LIMIT 10")
for r in cur.fetchall():
    print(f"  {r[0]}")

conn.close()
