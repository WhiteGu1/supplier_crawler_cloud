import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-25
batch25 = [
    (33478, '玩具 > 玩具游戏 > 角色扮演'),
    (33479, '玩具 > 玩具游戏 > 桌游'),
    (33480, '玩具 > 玩具游戏 > 角色扮演'),
    (33481, '玩具 > 玩具游戏 > 角色扮演'),
    (33482, '玩具 > 玩具游戏 > 角色扮演'),
    (33484, '玩具 > 玩具游戏 > 玩具车'),
    (33485, '玩具 > 玩具游戏 > 玩具车'),
    (33486, '玩具 > 玩具游戏 > 玩具车'),
    (33487, '玩具 > 玩具游戏 > 角色扮演'),
    (33488, '玩具 > 玩具游戏 > 角色扮演'),
]

total = 0
for pid, cat in batch25:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch25=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
