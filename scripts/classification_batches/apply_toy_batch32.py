import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-32
batch32 = [
    (33569, '玩具 > 玩具游戏 > 解压玩具'),
    (33570, '玩具 > 玩具游戏 > 解压玩具'),
    (33571, '玩具 > 玩具游戏 > 解压玩具'),
    (33575, '玩具 > 玩具游戏 > 角色扮演'),
    (33576, '玩具 > 玩具游戏 > 积木/拼装'),
    (33578, '玩具 > 玩具游戏 > 拼图'),
    (33581, '玩具 > 玩具游戏 > 积木/拼装'),
    (33582, '玩具 > 玩具游戏 > 积木/拼装'),
    (33583, '玩具 > 玩具游戏 > 积木/拼装'),
    (33584, '玩具 > 玩具游戏 > 其他玩具'),
]

total = 0
for pid, cat in batch32:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch32=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
