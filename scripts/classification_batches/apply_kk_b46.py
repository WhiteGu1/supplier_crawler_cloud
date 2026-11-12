import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b46: 8条修正
b46 = [
    (30168, '箱包配件'), (30169, '箱包配件'), (30170, '箱包配件'),
    (30171, '箱包配件'), (30172, '箱包配件'), (30173, '箱包配件'),
    (30174, '箱包配件'), (30199, '旅行用品')
]

for pid, cat in b46:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b46: {len(b46)}条写入完成")
conn.close()
