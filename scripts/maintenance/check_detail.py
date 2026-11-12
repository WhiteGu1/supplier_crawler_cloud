import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# Who has category = '玩具 > 玩具游戏'?
cur.execute("SELECT supplier_id, COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' GROUP BY supplier_id ORDER BY COUNT(*) DESC")
print("=== category='玩具 > 玩具游戏' by supplier ===")
for r in cur.fetchall():
    print(f'  supplier_id={r[0]}: {r[1]}')

# NULL/empty details
cur.execute("SELECT supplier_id, id, sku, name, image_local FROM products WHERE category IS NULL OR category = '' ORDER BY supplier_id, id")
print("\n=== NULL/empty category items ===")
for r in cur.fetchall():
    has_img = 'Y' if r[4] else 'N'
    print(f'  sid={r[0]} id={r[1]} sku={r[2]} img={has_img} name={r[3][:50]}')

conn.close()
