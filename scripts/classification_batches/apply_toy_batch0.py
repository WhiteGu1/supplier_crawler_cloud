import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-0 results (restore &gt; to >)
results = [
    (17445, '玩具 > 玩具游戏 > 解压玩具'),
    (17446, '玩具 > 玩具游戏 > 解压玩具'),
    (17447, '玩具 > 玩具游戏 > 解压玩具'),
    (17448, '玩具 > 玩具游戏 > 解压玩具'),
    (17449, '玩具 > 玩具游戏 > 解压玩具'),
    (18726, '玩具 > 玩具游戏 > 桌游'),
    (18727, '玩具 > 玩具游戏 > 桌游'),
    (18728, '玩具 > 玩具游戏 > 其他玩具'),
    (18729, '玩具 > 玩具游戏 > 其他玩具'),
    (18730, '玩具 > 玩具游戏 > 其他玩具'),
]

for pid, cat in results:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))

conn.commit()
print(f'batch-0: {len(results)} items written')

# Check remaining
cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
