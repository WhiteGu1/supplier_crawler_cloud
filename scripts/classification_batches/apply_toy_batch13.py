import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-13
batch13 = [
    (18583, '玩具 > 玩具游戏 > 角色扮演'),
    (18584, '玩具 > 玩具游戏 > 角色扮演'),
    (18585, '玩具 > 玩具游戏 > 角色扮演'),
    (18586, '玩具 > 玩具游戏 > 音乐玩具'),
    (18588, '玩具 > 玩具游戏 > 角色扮演'),
    (18589, '玩具 > 玩具游戏 > 益智玩具'),
    (18590, '玩具 > 玩具游戏 > 益智玩具'),
    (18593, '玩具 > 玩具游戏 > 角色扮演'),
    (18594, '玩具 > 玩具游戏 > 角色扮演'),
    (18596, '玩具 > 玩具游戏 > 益智玩具'),
]

total = 0
for pid, cat in batch13:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch13=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
