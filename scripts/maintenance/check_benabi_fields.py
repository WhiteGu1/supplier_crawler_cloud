import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 查看products表结构
cur.execute("DESCRIBE products")
for row in cur.fetchall():
    print(row)

print("\n--- 查看ID=2680的完整记录 ---")
cur.execute("SELECT * FROM products WHERE id=2680")
cols = [d[0] for d in cur.description]
row = cur.fetchone()
if row:
    for c, v in zip(cols, row):
        print(f"  {c} = {repr(v)[:100]}")

# 查看之前成功的商品（ID=17793）的图片字段
print("\n--- 查看ID=17793的图片字段 ---")
cur.execute("SELECT id, name, image_local, image_url FROM products WHERE id=17793")
cols = [d[0] for d in cur.description]
row = cur.fetchone()
if row:
    for c, v in zip(cols, row):
        print(f"  {c} = {repr(v)[:150]}")

conn.close()
