import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

batch0 = [
    (18734, '玩具 > 玩具游戏 > 角色扮演'),
    (18764, '玩具 > 玩具游戏 > 其他玩具'),
    (18765, '玩具 > 玩具游戏 > 其他玩具'),
    (18766, '玩具 > 玩具游戏 > 其他玩具'),
    (18767, '玩具 > 玩具游戏 > 其他玩具'),
    (18781, '玩具 > 玩具游戏 > 角色扮演'),
    (18983, '玩具 > 玩具游戏 > 其他玩具'),
    (19890, '玩具 > 玩具游戏 > 其他玩具'),
    (19950, '玩具 > 玩具游戏 > 其他玩具'),
    (20085, '玩具 > 玩具游戏 > 其他玩具'),
]

for pid, cat in batch0:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))

conn.commit()
print(f'Written: {len(batch0)} items (batch0)')

cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining: {cur.fetchone()[0]}')
conn.close()
