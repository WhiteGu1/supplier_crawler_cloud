import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-22
batch22 = [
    (33448, '玩具 > 玩具游戏 > 解压玩具'),
    (33449, '玩具 > 玩具游戏 > 解压玩具'),
    (33450, '玩具 > 玩具游戏 > 解压玩具'),
    (33451, '玩具 > 玩具游戏 > 手工DIY'),
    (33452, '玩具 > 玩具游戏 > 其他玩具'),
    (33453, '玩具 > 玩具游戏 > 其他玩具'),
    (33454, '玩具 > 玩具游戏 > 其他玩具'),
    (33455, '玩具 > 玩具游戏 > 其他玩具'),
    (33456, '玩具 > 玩具游戏 > 其他玩具'),
    (33457, '玩具 > 玩具游戏 > 其他玩具'),
]

total = 0
for pid, cat in batch22:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch22=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
