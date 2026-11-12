import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

batch3 = [
    (33533, '玩具 > 玩具游戏 > 角色扮演'),
    (33569, '玩具 > 玩具游戏 > 解压玩具'),  # SLIME -> 解压玩具 (修正)
    (33570, '玩具 > 玩具游戏 > 解压玩具'),
    (33571, '玩具 > 玩具游戏 > 解压玩具'),
    (33575, '玩具 > 玩具游戏 > 角色扮演'),
    (33576, '玩具 > 玩具游戏 > 积木/拼装'),
    (33578, '玩具 > 玩具游戏 > 积木/拼装'),  # ROMPECABEZAS拼图但Minecraft积木风格 -> 积木/拼装
    (33581, '玩具 > 玩具游戏 > 积木/拼装'),
    (33582, '玩具 > 玩具游戏 > 积木/拼装'),
    (33583, '玩具 > 玩具游戏 > 积木/拼装'),
]

for pid, cat in batch3:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))

conn.commit()
print(f'Written: {len(batch3)} items (batch3)')

cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining: {cur.fetchone()[0]}')
conn.close()
