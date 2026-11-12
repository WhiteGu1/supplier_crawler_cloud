import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-14-retry
batch14 = [
    (18597, '玩具 > 玩具游戏 > 手工DIY'),
    (18598, '玩具 > 玩具游戏 > 其他玩具'),
    (18599, '玩具 > 玩具游戏 > 手工DIY'),
    (18600, '玩具 > 玩具游戏 > 手工DIY'),
    (18601, '玩具 > 玩具游戏 > 手工DIY'),
    (18602, '玩具 > 玩具游戏 > 手工DIY'),
    (18603, '玩具 > 玩具游戏 > 手工DIY'),
    (18604, '玩具 > 玩具游戏 > 手工DIY'),
    (18606, '玩具 > 玩具游戏 > 手工DIY'),
    (18607, '玩具 > 玩具游戏 > 手工DIY'),
]

total = 0
for pid, cat in batch14:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch14=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
