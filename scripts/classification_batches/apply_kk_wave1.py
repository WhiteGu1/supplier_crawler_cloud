import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 第一波所有修正
fixes = [
    # b0
    (27870, '时尚配饰'),
    # b2
    (27956, '玩具游戏'),
    (27995, '电器电子'),
    (28004, '园艺户外'),
    # b3
    (28006, '电器电子'),
    (28007, '电器电子'),
    # b4
    (28091, '时尚配饰'),
    (28092, '数码科技'),
    (28093, '时尚配饰'),
    (28094, '时尚配饰'),
    (28095, '数码科技'),
    (28096, '数码科技'),
    (28097, '数码科技'),
    (28098, '数码科技'),
    (28099, '数码科技'),
    (28100, '数码科技'),
    (28101, '数码科技'),
    (28102, '数码科技'),
    (28103, '数码科技'),
    (28104, '数码科技'),
    (28105, '数码科技'),
]

updated = 0
for pid, cat in fixes:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
    updated += cur.rowcount

conn.commit()
print(f"第一波修正写入: {updated}/{len(fixes)} 条")

# 确认数码科技分类存在
cur.execute("SELECT COUNT(*) FROM products WHERE category='数码科技'")
cnt = cur.fetchone()[0]
print(f"数码科技分类总数: {cnt}")

conn.close()
