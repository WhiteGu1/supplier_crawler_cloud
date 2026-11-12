import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# Check supplier 3 and 1 items with '玩具 > 玩具游戏'
cur.execute("SELECT id, sku, name, image_local FROM products WHERE category = '玩具 > 玩具游戏' AND supplier_id IN (1, 3) ORDER BY supplier_id, id LIMIT 30")
print("=== supplier 1 & 3 with '玩具 > 玩具游戏' ===")
for r in cur.fetchall():
    has_img = 'Y' if r[3] else 'N'
    print(f'  sid={r[0]} id={r[1]} sku={r[2]} img={has_img} name={r[3][:50] if r[3] else ""}')

# Count
cur.execute("SELECT supplier_id, COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' GROUP BY supplier_id")
print("\n=== Breakdown ===")
for r in cur.fetchall():
    print(f'  supplier_id={r[0]}: {r[1]}')

# Panda remaining with image
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND category='玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f"\nPanda pending with image: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND category='玩具 > 玩具游戏' AND (image_local IS NULL OR image_local = '')")
print(f"Panda pending no image: {cur.fetchone()[0]}")

# Show some supplier 3 items
cur.execute("SELECT id, name FROM products WHERE category='玩具 > 玩具游戏' AND supplier_id=3 LIMIT 10")
print("\n=== Sample supplier 3 items ===")
for r in cur.fetchall():
    print(f'  id={r[0]} name={r[1]}')

conn.close()
