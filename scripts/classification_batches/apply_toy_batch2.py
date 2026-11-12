import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-2 manual classification by name
batch2 = [
    (18365, '玩具 > 玩具游戏 > 毛绒玩具'),
    (18366, '玩具 > 玩具游戏 > 毛绒玩具'),
    (18367, '玩具 > 玩具游戏 > 毛绒玩具'),
    (18368, '玩具 > 玩具游戏 > 玩具球'),
    (18369, '玩具 > 玩具游戏 > 玩具球'),
    (18370, '玩具 > 玩具游戏 > 玩具球'),
    (18371, '玩具 > 玩具游戏 > 玩具球'),
    (18372, '玩具 > 玩具游戏 > 玩具球'),
    (18373, '玩具 > 玩具游戏 > 玩具球'),
    (18374, '玩具 > 玩具游戏 > 玩具球'),
]

total = 0
for pid, cat in batch2:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch2=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
