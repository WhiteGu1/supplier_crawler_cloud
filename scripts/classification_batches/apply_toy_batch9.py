import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-9: all 其他玩具 (burbujero)
batch9 = [
    (18543, '玩具 > 玩具游戏 > 其他玩具'),
    (18544, '玩具 > 玩具游戏 > 其他玩具'),
    (18545, '玩具 > 玩具游戏 > 其他玩具'),
    (18546, '玩具 > 玩具游戏 > 其他玩具'),
    (18547, '玩具 > 玩具游戏 > 其他玩具'),
    (18548, '玩具 > 玩具游戏 > 其他玩具'),
    (18549, '玩具 > 玩具游戏 > 其他玩具'),
    (18550, '玩具 > 玩具游戏 > 其他玩具'),
    (18551, '玩具 > 玩具游戏 > 其他玩具'),
    (18552, '玩具 > 玩具游戏 > 其他玩具'),
]

total = 0
for pid, cat in batch9:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch9=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
