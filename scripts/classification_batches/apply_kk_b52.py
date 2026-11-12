import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b52: 6条修正
b52 = [
    (30473, '园艺户外'), (30474, '园艺户外'), (30475, '园艺户外'),
    (30476, '园艺户外'), (30477, '园艺户外'),
    (30478, '电器电子')
]

for pid, cat in b52:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b52: {len(b52)}条写入完成")
conn.close()
