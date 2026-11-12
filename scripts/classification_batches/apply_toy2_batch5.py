import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

batch5 = [
    (33606, '玩具 > 玩具游戏 > 益智玩具'),
    (33608, '玩具 > 玩具游戏 > 其他玩具'),
    (33611, '玩具 > 玩具游戏 > 积木/拼装'),
    (33613, '玩具 > 玩具游戏 > 角色扮演'),
    (33615, '玩具 > 玩具游戏 > 角色扮演'),
    (33631, '玩具 > 玩具游戏 > 玩具车'),
    (33632, '玩具 > 玩具游戏 > 玩具车'),
    (33633, '玩具 > 玩具游戏 > 角色扮演'),
    (33643, '玩具 > 玩具游戏 > 桌游'),
    (33644, '玩具 > 玩具游戏 > 积木/拼装'),
]

for pid, cat in batch5:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))

conn.commit()
print(f'Written: {len(batch5)} items (batch5)')

cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining: {cur.fetchone()[0]}')
conn.close()
