import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b5: 50条全部 日用百货→数码科技 (ID 28106-28155)
for pid in range(28106, 28156):
    cur.execute("UPDATE products SET category='数码科技' WHERE id=%s", (pid,))

# b6: 26条修正
b6_fixes = [
    (28156, '数码科技'), (28157, '数码科技'), (28158, '数码科技'), (28159, '数码科技'),
    (28160, '数码科技'), (28161, '数码科技'), (28162, '数码科技'), (28163, '数码科技'),
    (28164, '数码科技'), (28165, '数码科技'), (28166, '数码科技'), (28167, '数码科技'),
    (28168, '数码科技'),
    (28169, '电器电子'), (28170, '电器电子'),
    (28171, '数码科技'), (28172, '数码科技'), (28173, '数码科技'),
    (28174, '电器电子'), (28175, '电器电子'), (28176, '电器电子'),
    (28177, '玩具游戏'),
    (28178, '美妆个护'),
    (28180, '旅行用品'),
    (28181, '数码科技'),
]
for pid, cat in b6_fixes:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b5: 50条写入, b6: {len(b6_fixes)}条写入")

# 确认
cur.execute("SELECT COUNT(*) FROM products WHERE category='数码科技'")
print(f"数码科技分类总数: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM products WHERE category='旅行用品'")
print(f"旅行用品分类总数: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM products WHERE category='美妆个护'")
print(f"美妆个护分类总数: {cur.fetchone()[0]}")

conn.close()
