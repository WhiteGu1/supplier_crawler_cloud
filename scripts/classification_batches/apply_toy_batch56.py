import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-5: all 玩具车
batch5 = [
    (18468, '玩具 > 玩具游戏 > 玩具车'),
    (18469, '玩具 > 玩具游戏 > 玩具车'),
    (18472, '玩具 > 玩具游戏 > 玩具车'),
    (18473, '玩具 > 玩具游戏 > 玩具车'),
    (18474, '玩具 > 玩具游戏 > 玩具车'),
    (18475, '玩具 > 玩具游戏 > 玩具车'),
    (18476, '玩具 > 玩具游戏 > 玩具车'),
    (18477, '玩具 > 玩具游戏 > 玩具车'),
    (18478, '玩具 > 玩具游戏 > 玩具车'),
    (18479, '玩具 > 玩具游戏 > 玩具车'),
]

# batch-6: 9 玩具车 + 1 其他玩具 (monopatin)
batch6 = [
    (18480, '玩具 > 玩具游戏 > 玩具车'),
    (18481, '玩具 > 玩具游戏 > 玩具车'),
    (18482, '玩具 > 玩具游戏 > 玩具车'),
    (18483, '玩具 > 玩具游戏 > 玩具车'),
    (18484, '玩具 > 玩具游戏 > 玩具车'),
    (18485, '玩具 > 玩具游戏 > 玩具车'),
    (18486, '玩具 > 玩具游戏 > 玩具车'),
    (18487, '玩具 > 玩具游戏 > 玩具车'),
    (18488, '玩具 > 玩具游戏 > 玩具车'),
    (18489, '玩具 > 玩具游戏 > 其他玩具'),
]

total = 0
for batch in [batch5, batch6]:
    for pid, cat in batch:
        cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
        total += 1

conn.commit()
print(f'Written: {total} items (batch5=10, batch6=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
