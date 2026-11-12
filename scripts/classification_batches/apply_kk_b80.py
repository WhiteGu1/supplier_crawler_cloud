import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b80: 28条 派对用品→婴幼儿用品 (31878-31905)
b80_ids = list(range(31878, 31906))

for pid in b80_ids:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", ('婴幼儿用品', pid))

conn.commit()
print(f"b80: {len(b80_ids)}条写入完成 (派对用品→婴幼儿用品)")
conn.close()
