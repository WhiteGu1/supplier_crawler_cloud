import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-20-retry
batch20 = [
    (33428, '玩具 > 玩具游戏 > 玩具车'),
    (33429, '玩具 > 玩具游戏 > 其他玩具'),
    (33430, '玩具 > 玩具游戏 > 其他玩具'),
    (33431, '玩具 > 玩具游戏 > 其他玩具'),
    (33432, '玩具 > 玩具游戏 > 其他玩具'),
    (33433, '玩具 > 玩具游戏 > 角色扮演'),
    (33434, '玩具 > 玩具游戏 > 角色扮演'),
    (33435, '玩具 > 玩具游戏 > 角色扮演'),
    (33436, '玩具 > 玩具游戏 > 音乐玩具'),
    (33437, '玩具 > 玩具游戏 > 益智玩具'),
]

total = 0
for pid, cat in batch20:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch20-retry=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
