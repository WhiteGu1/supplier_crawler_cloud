import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b40: 2条 多米诺骨牌→玩具游戏
b40 = [(29887, '玩具游戏'), (29888, '玩具游戏')]

# b41: 4条 编织纸袋→派对用品
b41 = [(29937, '派对用品'), (29938, '派对用品'), (29939, '派对用品'), (29940, '派对用品')]

for pid, cat in b40:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
for pid, cat in b41:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b40: {len(b40)}, b41: {len(b41)}, 共{len(b40)+len(b41)}条写入完成")
conn.close()
