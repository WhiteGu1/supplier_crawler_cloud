import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-21
batch21 = [
    (33438, '玩具 > 玩具游戏 > 桌游'),
    (33439, '玩具 > 玩具游戏 > 音乐玩具'),
    (33440, '玩具 > 玩具游戏 > 音乐玩具'),
    (33441, '玩具 > 玩具游戏 > 音乐玩具'),
    (33442, '玩具 > 玩具游戏 > 手工DIY'),
    (33443, '玩具 > 玩具游戏 > 角色扮演'),
    (33444, '玩具 > 玩具游戏 > 解压玩具'),
    (33445, '玩具 > 玩具游戏 > 毛绒玩具'),
    (33446, '玩具 > 玩具游戏 > 解压玩具'),
    (33447, '玩具 > 玩具游戏 > 解压玩具'),
]

total = 0
for pid, cat in batch21:
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
    total += 1

conn.commit()
print(f'Written: {total} items (batch21=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
