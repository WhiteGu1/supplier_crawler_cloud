import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b56: 2条 ARMARIO→家居家具
b56 = [(30699, '家居家具'), (30700, '家居家具')]

# b57: 34条 铁制酒瓶架/装饰摆件→家居装饰
b57_ids = list(range(30722, 30756))  # 30722-30755
b57 = [(pid, '家居装饰') for pid in b57_ids]

# b59: 8条 电子闹钟→电器电子(5), 装饰品→家居装饰(3)
b59 = [
    (30806, '电器电子'), (30807, '电器电子'), (30808, '电器电子'),
    (30809, '电器电子'), (30810, '电器电子'),
    (30811, '家居装饰'), (30812, '家居装饰'), (30813, '家居装饰')
]

for pid, cat in b56:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
for pid, cat in b57:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
for pid, cat in b59:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b56: {len(b56)}条, b57: {len(b57)}条, b59: {len(b59)}条, 共{len(b56)+len(b57)+len(b59)}条写入完成")
conn.close()
