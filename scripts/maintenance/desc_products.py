import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 先看表结构
cur.execute("DESCRIBE products")
cols = cur.fetchall()
print("products表字段:")
for c in cols:
    print(f"  {c[0]} ({c[1]})")

conn.close()
