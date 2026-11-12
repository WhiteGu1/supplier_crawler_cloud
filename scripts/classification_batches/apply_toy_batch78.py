import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-7: 8 玩具车 (monopatin) + 2 角色扮演 (pistola)
batch7 = [
    (18490, '玩具 > 玩具游戏 > 玩具车'),
    (18491, '玩具 > 玩具游戏 > 玩具车'),
    (18492, '玩具 > 玩具游戏 > 玩具车'),
    (18493, '玩具 > 玩具游戏 > 玩具车'),
    (18494, '玩具 > 玩具游戏 > 玩具车'),
    (18496, '玩具 > 玩具游戏 > 玩具车'),
    (18497, '玩具 > 玩具游戏 > 玩具车'),
    (18498, '玩具 > 玩具游戏 > 玩具车'),
    (18531, '玩具 > 玩具游戏 > 角色扮演'),
    (18532, '玩具 > 玩具游戏 > 角色扮演'),
]

# batch-8: 5 角色扮演 (pistola) + 5 其他玩具 (burbujero)
batch8 = [
    (18533, '玩具 > 玩具游戏 > 角色扮演'),
    (18534, '玩具 > 玩具游戏 > 角色扮演'),
    (18535, '玩具 > 玩具游戏 > 角色扮演'),
    (18536, '玩具 > 玩具游戏 > 角色扮演'),
    (18537, '玩具 > 玩具游戏 > 角色扮演'),
    (18538, '玩具 > 玩具游戏 > 其他玩具'),
    (18539, '玩具 > 玩具游戏 > 其他玩具'),
    (18540, '玩具 > 玩具游戏 > 其他玩具'),
    (18541, '玩具 > 玩具游戏 > 其他玩具'),
    (18542, '玩具 > 玩具游戏 > 其他玩具'),
]

total = 0
for batch in [batch7, batch8]:
    for pid, cat in batch:
        cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
        total += 1

conn.commit()
print(f'Written: {total} items (batch7=10, batch8=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
