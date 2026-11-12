import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

batch4 = [
    (33584, '玩具 > 玩具游戏 > 积木/拼装'),
    (33585, '玩具 > 玩具游戏 > 音乐玩具'),  # ORGANO=电子琴 -> 音乐玩具 (修正)
    (33586, '玩具 > 玩具游戏 > 拼图'),  # ROMPECABEZAS=拼图 (修正)
    (33587, '玩具 > 玩具游戏 > 拼图'),  # ROMPECABEZAS=拼图 (修正)
    (33591, '玩具 > 玩具游戏 > 音乐玩具'),
    (33595, '玩具 > 玩具游戏 > 其他玩具'),  # TROMPO陀螺
    (33596, '玩具 > 玩具游戏 > 角色扮演'),  # SET MANICURA
    (33597, '玩具 > 玩具游戏 > 角色扮演'),
    (33598, '玩具 > 玩具游戏 > 角色扮演'),
    (33599, '玩具 > 玩具游戏 > 角色扮演'),
]

for pid, cat in batch4:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))

conn.commit()
print(f'Written: {len(batch4)} items (batch4)')

cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining: {cur.fetchone()[0]}')
conn.close()
