import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-30
batch30 = [
    (33534, '玩具 > 玩具游戏 > 玩具车'),
    (33535, '玩具 > 玩具游戏 > 玩具车'),
    (33536, '玩具 > 玩具游戏 > 益智玩具'),
    (33537, '玩具 > 玩具游戏 > 益智玩具'),
    (33538, '玩具 > 玩具游戏 > 其他玩具'),
    (33539, '玩具 > 玩具游戏 > 益智玩具'),
    (33540, '玩具 > 玩具游戏 > 解压玩具'),
    (33541, '玩具 > 玩具游戏 > 益智玩具'),
    (33543, '玩具 > 玩具游戏 > 桌游'),
    (33545, '玩具 > 玩具游戏 > 解压玩具'),
]

# batch-31
batch31 = [
    (33546, '玩具 > 玩具游戏 > 手工DIY'),
    (33549, '玩具 > 玩具游戏 > 桌游'),
    (33550, '玩具 > 玩具游戏 > 手工DIY'),
    (33551, '玩具 > 玩具游戏 > 手工DIY'),
    (33553, '玩具 > 玩具游戏 > 其他玩具'),
    (33556, '玩具 > 玩具游戏 > 玩具车'),
    (33557, '玩具 > 玩具游戏 > 益智玩具'),
    (33558, '玩具 > 玩具游戏 > 玩具车'),
    (33559, '玩具 > 玩具游戏 > 积木/拼装'),
    (33568, '玩具 > 玩具游戏 > 角色扮演'),
]

total = 0
for pid, cat in batch30 + batch31:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch30=10 + batch31=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
