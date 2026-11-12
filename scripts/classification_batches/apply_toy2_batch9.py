import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

batch9 = [
    (33679, '玩具 > 玩具游戏 > 角色扮演'),
    (33680, '玩具 > 玩具游戏 > 角色扮演'),
    (33681, '玩具 > 玩具游戏 > 角色扮演'),  # PISTOLA LANZA DARDOS -> 角色扮演 (修正)
    (33682, '玩具 > 玩具游戏 > 益智玩具'),
    (33684, '玩具 > 玩具游戏 > 益智玩具'),
    (33685, '玩具 > 玩具游戏 > 毛绒玩具'),
    (33686, '玩具 > 玩具游戏 > 益智玩具'),
    (33687, '玩具 > 玩具游戏 > 毛绒玩具'),
    (33688, '玩具 > 玩具游戏 > 手工DIY'),
    (33689, '玩具 > 玩具游戏 > 益智玩具'),
]

for pid, cat in batch9:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))

conn.commit()
print(f'Written: {len(batch9)} items (batch9)')

cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining: {cur.fetchone()[0]}')
conn.close()
