import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-26
batch26 = [
    (33489, '玩具 > 玩具游戏 > 角色扮演'),
    (33490, '玩具 > 玩具游戏 > 角色扮演'),
    (33491, '玩具 > 玩具游戏 > 角色扮演'),
    (33492, '玩具 > 玩具游戏 > 角色扮演'),
    (33493, '玩具 > 玩具游戏 > 角色扮演'),
    (33494, '玩具 > 玩具游戏 > 益智玩具'),
    (33495, '玩具 > 玩具游戏 > 角色扮演'),
    (33496, '玩具 > 玩具游戏 > 角色扮演'),
    (33497, '玩具 > 玩具游戏 > 角色扮演'),
    (33498, '玩具 > 玩具游戏 > 角色扮演'),
]

# batch-28
batch28 = [
    (33509, '玩具 > 玩具游戏 > 益智玩具'),
    (33510, '玩具 > 玩具游戏 > 益智玩具'),
    (33511, '玩具 > 玩具游戏 > 益智玩具'),
    (33512, '玩具 > 玩具游戏 > 益智玩具'),
    (33513, '玩具 > 玩具游戏 > 益智玩具'),
    (33514, '玩具 > 玩具游戏 > 益智玩具'),
    (33515, '玩具 > 玩具游戏 > 益智玩具'),
    (33516, '玩具 > 玩具游戏 > 益智玩具'),
    (33517, '玩具 > 玩具游戏 > 益智玩具'),
    (33518, '玩具 > 玩具游戏 > 益智玩具'),
]

total = 0
for pid, cat in batch26 + batch28:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch26=10 + batch28=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
