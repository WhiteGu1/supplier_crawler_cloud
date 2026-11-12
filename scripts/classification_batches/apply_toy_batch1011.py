import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-10
batch10 = [
    (18553, '玩具 > 玩具游戏 > 其他玩具'),
    (18554, '玩具 > 玩具游戏 > 其他玩具'),
    (18555, '玩具 > 玩具游戏 > 其他玩具'),
    (18556, '玩具 > 玩具游戏 > 其他玩具'),
    (18557, '玩具 > 玩具游戏 > 其他玩具'),
    (18558, '玩具 > 玩具游戏 > 益智玩具'),
    (18559, '玩具 > 玩具游戏 > 解压玩具'),
    (18560, '玩具 > 玩具游戏 > 解压玩具'),
    (18561, '玩具 > 玩具游戏 > 解压玩具'),
    (18562, '玩具 > 玩具游戏 > 解压玩具'),
]

# batch-11
batch11 = [
    (18563, '玩具 > 玩具游戏 > 解压玩具'),
    (18564, '玩具 > 玩具游戏 > 其他玩具'),
    (18565, '玩具 > 玩具游戏 > 其他玩具'),
    (18566, '玩具 > 玩具游戏 > 其他玩具'),
    (18567, '玩具 > 玩具游戏 > 益智玩具'),
    (18568, '玩具 > 玩具游戏 > 益智玩具'),
    (18569, '玩具 > 玩具游戏 > 益智玩具'),
    (18570, '玩具 > 玩具游戏 > 角色扮演'),
    (18571, '玩具 > 玩具游戏 > 其他玩具'),
    (18572, '玩具 > 玩具游戏 > 其他玩具'),
]

total = 0
for batch in [batch10, batch11]:
    for pid, cat in batch:
        cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
        total += 1

conn.commit()
print(f'Written: {total} items (batch10=10, batch11=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
