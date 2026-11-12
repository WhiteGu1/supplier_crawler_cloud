import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-17
batch17 = [
    (33398, '玩具 > 玩具游戏 > 手工DIY'),
    (33399, '玩具 > 玩具游戏 > 积木/拼装'),
    (33400, '玩具 > 玩具游戏 > 手工DIY'),
    (33401, '玩具 > 玩具游戏 > 其他玩具'),
    (33402, '玩具 > 玩具游戏 > 手工DIY'),
    (33403, '玩具 > 玩具游戏 > 玩具车'),
    (33404, '玩具 > 玩具游戏 > 玩具车'),
    (33405, '玩具 > 玩具游戏 > 角色扮演'),
    (33406, '玩具 > 玩具游戏 > 玩具车'),
    (33407, '玩具 > 玩具游戏 > 手工DIY'),
]

# batch-18
batch18 = [
    (33408, '玩具 > 玩具游戏 > 角色扮演'),
    (33409, '玩具 > 玩具游戏 > 角色扮演'),
    (33410, '玩具 > 玩具游戏 > 角色扮演'),
    (33411, '玩具 > 玩具游戏 > 角色扮演'),
    (33412, '玩具 > 玩具游戏 > 角色扮演'),
    (33413, '玩具 > 玩具游戏 > 角色扮演'),
    (33414, '玩具 > 玩具游戏 > 手工DIY'),
    (33415, '玩具 > 玩具游戏 > 角色扮演'),
    (33416, '玩具 > 玩具游戏 > 玩具车'),
    (33417, '玩具 > 玩具游戏 > 玩具车'),
]

total = 0
for batch in [batch17, batch18]:
    for pid, cat in batch:
        cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
        total += 1

conn.commit()
print(f'Written: {total} items (batch17=10, batch18=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
