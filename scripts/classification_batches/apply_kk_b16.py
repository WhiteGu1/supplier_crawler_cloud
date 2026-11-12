import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b16: 23条 厨房储物→厨房餐具 (保温杯/杯壶)
b16_ids = list(range(28669, 28692))
for pid in b16_ids:
    cur.execute("UPDATE products SET category='厨房餐具' WHERE id=%s", (pid,))

conn.commit()
print(f"b16: {len(b16_ids)}条写入完成")

conn.close()
