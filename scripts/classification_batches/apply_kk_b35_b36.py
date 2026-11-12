import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b35: 2条
b35 = [(29625, '厨房储物'), (29655, '厨房储物')]

# b36: 6条 衣架/挂篮→家居收纳
b36 = [(29679, '家居收纳'), (29680, '家居收纳'), (29681, '家居收纳'),
       (29682, '家居收纳'), (29683, '家居收纳'), (29684, '家居收纳')]

for pid, cat in b35:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
for pid, cat in b36:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b35: {len(b35)}, b36: {len(b36)}, 共{len(b35)+len(b36)}条写入完成")
conn.close()
