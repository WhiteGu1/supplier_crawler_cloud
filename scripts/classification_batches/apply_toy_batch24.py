import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-24
batch24 = [
    (33468, '玩具 > 玩具游戏 > 玩具车'),
    (33469, '玩具 > 玩具游戏 > 玩具车'),
    (33470, '玩具 > 玩具游戏 > 玩具车'),
    (33471, '玩具 > 玩具游戏 > 玩具车'),
    (33472, '玩具 > 玩具游戏 > 角色扮演'),
    (33473, '玩具 > 玩具游戏 > 玩具车'),
    (33474, '玩具 > 玩具游戏 > 角色扮演'),
    (33475, '玩具 > 玩具游戏 > 益智玩具'),
    (33476, '玩具 > 玩具游戏 > 角色扮演'),
    (33477, '玩具 > 玩具游戏 > 角色扮演'),
]

total = 0
for pid, cat in batch24:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch24=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
