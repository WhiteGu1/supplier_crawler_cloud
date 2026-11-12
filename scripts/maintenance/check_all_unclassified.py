# Check unclassified progress
import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT supplier_id, COUNT(*) as cnt FROM products WHERE category IS NULL OR category = '' GROUP BY supplier_id ORDER BY cnt DESC")
print('=== NULL/empty category breakdown ===')
for r in cur.fetchall():
    print(f'  supplier_id={r[0]}: {r[1]} items')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏'")
print(f"\nTotal 'pending panda' (category=玩具 > 玩具游戏): {cur.fetchone()[0]}")

cur.execute("SELECT supplier_id, COUNT(*) as total FROM products GROUP BY supplier_id ORDER BY supplier_id")
print('\n=== All suppliers ===')
for r in cur.fetchall():
    print(f'  supplier_id={r[0]}: {r[1]} total')

# Panda specific
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND category IS NULL OR category = '' OR category = '玩具 > 玩具游戏'")
print(f"\nPanda total unclassified: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND image_local IS NOT NULL AND image_local != '' AND (category IS NULL OR category = '' OR category = '玩具 > 玩具游戏')")
print(f"Panda unclassified with image: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND (image_local IS NULL OR image_local = '') AND (category IS NULL OR category = '' OR category = '玩具 > 玩具游戏')")
print(f"Panda unclassified no image: {cur.fetchone()[0]}")

conn.close()
