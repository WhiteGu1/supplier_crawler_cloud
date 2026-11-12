import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b10: 18条修正
# 厨房餐具→厨房炊具 (8条: 调酒器/开瓶器/制冰盒)
b10_to_cookware = [28388, 28389, 28390, 28391, 28392, 28393, 28394, 28395]
for pid in b10_to_cookware:
    cur.execute("UPDATE products SET category='厨房炊具' WHERE id=%s", (pid,))

# 厨房炊具→厨房储物 (10条: 餐具收纳盒/架)
b10_to_storage = [28396, 28397, 28398, 28399, 28400, 28401, 28402, 28403, 28404, 28405]
for pid in b10_to_storage:
    cur.execute("UPDATE products SET category='厨房储物' WHERE id=%s", (pid,))

# b13: 6条修正 厨房餐具→厨房储物 (DISPENSER分配器)
b13_fixes = [28548, 28549, 28550, 28551, 28552, 28553]
for pid in b13_fixes:
    cur.execute("UPDATE products SET category='厨房储物' WHERE id=%s", (pid,))

conn.commit()
print(f"b10: 18条写入, b13: 6条写入, 合计24条")

conn.close()
