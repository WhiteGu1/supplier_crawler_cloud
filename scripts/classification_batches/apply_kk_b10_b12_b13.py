import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b10: 18条
b10_cookware = [28388, 28389, 28390, 28391, 28392, 28393, 28394, 28395]
b10_storage = [28396, 28397, 28398, 28399, 28400, 28401, 28402, 28403, 28404, 28405]
for pid in b10_cookware:
    cur.execute("UPDATE products SET category='厨房炊具' WHERE id=%s", (pid,))
for pid in b10_storage:
    cur.execute("UPDATE products SET category='厨房储物' WHERE id=%s", (pid,))

# b12: 34条
# 厨房炊具→厨房餐具 (8条: CUBIERTERO + SET CUBIERTOS)
b12_to_tableware = [28456, 28457, 28458, 28459, 28460, 28461, 28462, 28463]
for pid in b12_to_tableware:
    cur.execute("UPDATE products SET category='厨房餐具' WHERE id=%s", (pid,))

# 厨房餐具→厨房炊具 (26条: PAVA烧水壶)
b12_to_cookware = list(range(28465, 28491))
for pid in b12_to_cookware:
    cur.execute("UPDATE products SET category='厨房炊具' WHERE id=%s", (pid,))

# b13: 6条 厨房餐具→厨房储物
b13_storage = [28548, 28549, 28550, 28551, 28552, 28553]
for pid in b13_storage:
    cur.execute("UPDATE products SET category='厨房储物' WHERE id=%s", (pid,))

conn.commit()
total = 18 + 34 + 6
print(f"b10: 18条, b12: 34条, b13: 6条, 合计{total}条写入完成")

conn.close()
