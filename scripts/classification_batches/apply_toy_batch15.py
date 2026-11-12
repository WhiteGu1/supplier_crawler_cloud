import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-15
batch15 = [
    (18609, '玩具 > 玩具游戏 > 角色扮演'),
    (18610, '玩具 > 玩具游戏 > 其他玩具'),
    (18611, '玩具 > 玩具游戏 > 其他玩具'),
    (18612, '玩具 > 玩具游戏 > 玩具车'),
    (18613, '玩具 > 玩具游戏 > 玩具车'),
    (18614, '玩具 > 玩具游戏 > 玩具车'),
    (18615, '玩具 > 玩具游戏 > 玩具车'),
    (18616, '玩具 > 玩具游戏 > 其他玩具'),
    (18617, '玩具 > 玩具游戏 > 其他玩具'),
    (18618, '玩具 > 玩具游戏 > 其他玩具'),
]

total = 0
for pid, cat in batch15:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch15=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
