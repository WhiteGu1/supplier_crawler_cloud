import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-12 (子agent查库修正后的结果)
batch12 = [
    (18573, '玩具 > 玩具游戏 > 其他玩具'),
    (18574, '玩具 > 玩具游戏 > 其他玩具'),
    (18575, '玩具 > 玩具游戏 > 其他玩具'),
    (18576, '玩具 > 玩具游戏 > 玩具球'),
    (18577, '玩具 > 玩具游戏 > 玩具球'),
    (18578, '玩具 > 玩具游戏 > 玩具球'),
    (18579, '玩具 > 玩具游戏 > 玩具球'),
    (18580, '玩具 > 玩具游戏 > 玩具球'),
    (18581, '玩具 > 玩具游戏 > 其他玩具'),
    (18582, '玩具 > 玩具游戏 > 其他玩具'),
]

total = 0
for pid, cat in batch12:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch12=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
