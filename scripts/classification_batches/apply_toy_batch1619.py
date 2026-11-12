import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-16
batch16 = [
    (18621, '玩具 > 玩具游戏 > 益智玩具'),
    (18622, '玩具 > 玩具游戏 > 益智玩具'),
    (18629, '玩具 > 玩具游戏 > 角色扮演'),
    (18630, '玩具 > 玩具游戏 > 角色扮演'),
    (18631, '玩具 > 玩具游戏 > 角色扮演'),
    (18632, '玩具 > 玩具游戏 > 其他玩具'),
    (18636, '玩具 > 玩具游戏 > 其他玩具'),
    (33395, '玩具 > 玩具游戏 > 其他玩具'),
    (33396, '玩具 > 玩具游戏 > 手工DIY'),
    (33397, '玩具 > 玩具游戏 > 其他玩具'),
]

# batch-19
batch19 = [
    (33418, '玩具 > 玩具游戏 > 玩具车'),
    (33419, '玩具 > 玩具游戏 > 玩具车'),
    (33420, '玩具 > 玩具游戏 > 玩具车'),
    (33421, '玩具 > 玩具游戏 > 角色扮演'),
    (33422, '玩具 > 玩具游戏 > 玩具车'),
    (33423, '玩具 > 玩具游戏 > 玩具车'),
    (33424, '玩具 > 玩具游戏 > 玩具车'),
    (33425, '玩具 > 玩具游戏 > 玩具车'),
    (33426, '玩具 > 玩具游戏 > 玩具车'),
    (33427, '玩具 > 玩具游戏 > 玩具车'),
]

total = 0
for batch in [batch16, batch19]:
    for pid, cat in batch:
        cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
        total += 1

conn.commit()
print(f'Written: {total} items (batch16=10, batch19=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
