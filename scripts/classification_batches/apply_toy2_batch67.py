import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

batch6 = [
    (33645, '玩具 > 玩具游戏 > 积木/拼装'),
    (33646, '玩具 > 玩具游戏 > 积木/拼装'),
    (33648, '玩具 > 玩具游戏 > 桌游'),
    (33649, '玩具 > 玩具游戏 > 桌游'),
    (33650, '玩具 > 玩具游戏 > 桌游'),
    (33651, '玩具 > 玩具游戏 > 桌游'),
    (33652, '玩具 > 玩具游戏 > 桌游'),
    (33653, '玩具 > 玩具游戏 > 桌游'),
    (33654, '玩具 > 玩具游戏 > 手工DIY'),
    (33655, '玩具 > 玩具游戏 > 其他玩具'),
]

batch7 = [
    (33656, '玩具 > 玩具游戏 > 桌游'),
    (33657, '玩具 > 玩具游戏 > 桌游'),
    (33658, '玩具 > 玩具游戏 > 桌游'),
    (33659, '玩具 > 玩具游戏 > 其他玩具'),
    (33660, '玩具 > 玩具游戏 > 桌游'),
    (33661, '玩具 > 玩具游戏 > 桌游'),
    (33662, '玩具 > 玩具游戏 > 桌游'),
    (33663, '玩具 > 玩具游戏 > 桌游'),
    (33665, '玩具 > 玩具游戏 > 其他玩具'),
    (33666, '玩具 > 玩具游戏 > 其他玩具'),
]

total = 0
for pid, cat in batch6 + batch7:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch6+7)')

cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining: {cur.fetchone()[0]}')
conn.close()
