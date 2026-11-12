import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-27
batch27 = [
    (33499, '玩具 > 玩具游戏 > 角色扮演'),
    (33500, '玩具 > 玩具游戏 > 玩具车'),
    (33501, '玩具 > 玩具游戏 > 解压玩具'),
    (33502, '玩具 > 玩具游戏 > 音乐玩具'),
    (33503, '玩具 > 玩具游戏 > 其他玩具'),
    (33504, '玩具 > 玩具游戏 > 其他玩具'),
    (33505, '玩具 > 玩具游戏 > 其他玩具'),
    (33506, '玩具 > 玩具游戏 > 解压玩具'),
    (33507, '玩具 > 玩具游戏 > 益智玩具'),
    (33508, '玩具 > 玩具游戏 > 益智玩具'),
]

total = 0
for pid, cat in batch27:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch27=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
