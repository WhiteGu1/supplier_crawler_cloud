import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-29 (from previous retry result)
batch29 = [
    (33519, '玩具 > 玩具游戏 > 益智玩具'),
    (33520, '玩具 > 玩具游戏 > 其他玩具'),
    (33521, '玩具 > 玩具游戏 > 解压玩具'),
    (33522, '玩具 > 玩具游戏 > 玩具车'),
    (33523, '玩具 > 玩具游戏 > 玩具车'),
    (33525, '玩具 > 玩具游戏 > 手工DIY'),
    (33528, '玩具 > 玩具游戏 > 手工DIY'),
    (33529, '玩具 > 玩具游戏 > 手工DIY'),
    (33532, '玩具 > 玩具游戏 > 玩具车'),
    (33533, '玩具 > 玩具游戏 > 玩具车'),
]

total = 0
for pid, cat in batch29:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch29=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
