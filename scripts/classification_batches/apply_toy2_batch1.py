import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

batch1 = [
    (20135, '玩具 > 玩具游戏 > 解压玩具'),
    (33458, '玩具 > 玩具游戏 > 玩具车'),
    (33459, '玩具 > 玩具游戏 > 玩具车'),
    (33460, '玩具 > 玩具游戏 > 玩具车'),
    (33461, '玩具 > 玩具游戏 > 玩具车'),
    (33462, '玩具 > 玩具游戏 > 玩具车'),
    (33463, '玩具 > 玩具游戏 > 玩具车'),
    (33464, '玩具 > 玩具游戏 > 玩具车'),
    (33465, '玩具 > 玩具游戏 > 玩具车'),
    (33466, '玩具 > 玩具游戏 > 玩具车'),
]

for pid, cat in batch1:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))

conn.commit()
print(f'Written: {len(batch1)} items (batch1-retry2)')

cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining: {cur.fetchone()[0]}')
conn.close()
