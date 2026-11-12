import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b26: 2条 厨房餐具→家居装饰 (CENTRO DE MESA 桌面装饰)
b26 = [(29200, '家居装饰'), (29204, '家居装饰')]
for pid, cat in b26:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

# b27: 4条修正
b27 = [
    (29216, '家居收纳'),   # ALHAJERO 首饰盒
    (29217, '家居装饰'),   # CENTRO DE MESA 桌面装饰
    (29218, '家居收纳'),   # ALHAJERO 首饰盒
    (29233, '厨房炊具'),   # JARRO MEDIDOR 量杯
]
for pid, cat in b27:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b26: {len(b26)}条, b27: {len(b27)}条, 共{len(b26)+len(b27)}条写入完成")
conn.close()
