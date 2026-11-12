import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b31: 6条
b31 = [
    (29441, '五金工具'), (29442, '五金工具'), (29443, '五金工具'), (29444, '五金工具'),
    (29446, '家居收纳'), (29447, '家居收纳'),
]

# b32: 36条 (28 ESPEJO→家居装饰, 7 TOALLA→家居纺织, 1 VINCHA→时尚配饰)
b32_espejo = list(range(29462, 29490))  # 28条镜子→家居装饰
b32_toalla = [29490, 29491, 29493, 29494, 29495, 29504, 29505]  # 7条毛巾→家居纺织
b32_vincha = [29492]  # 1条发带→时尚配饰

# b33: 18条 毛巾/浴巾→家居纺织
b33 = list(range(29506, 29524))  # 29506-29523 = 18条

# b34: 16条
b34_bolsa = list(range(29567, 29581))  # 14条热水袋→家居百货
b34_balanza = [29581, 29582]  # 2条体重秤→卫浴用品

# Execute all
for pid, cat in b31:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

for pid in b32_espejo:
    cur.execute("UPDATE products SET category='家居装饰' WHERE id=%s", (pid,))

for pid in b32_toalla:
    cur.execute("UPDATE products SET category='家居纺织' WHERE id=%s", (pid,))

for pid in b32_vincha:
    cur.execute("UPDATE products SET category='时尚配饰' WHERE id=%s", (pid,))

for pid in b33:
    cur.execute("UPDATE products SET category='家居纺织' WHERE id=%s", (pid,))

for pid in b34_bolsa:
    cur.execute("UPDATE products SET category='家居百货' WHERE id=%s", (pid,))

for pid in b34_balanza:
    cur.execute("UPDATE products SET category='卫浴用品' WHERE id=%s", (pid,))

conn.commit()
total = len(b31) + len(b32_espejo) + len(b32_toalla) + len(b32_vincha) + len(b33) + len(b34_bolsa) + len(b34_balanza)
print(f"b31: {len(b31)}, b32: {len(b32_espejo)+len(b32_toalla)+len(b32_vincha)}, b33: {len(b33)}, b34: {len(b34_bolsa)+len(b34_balanza)}")
print(f"总计: {total}条写入完成")
conn.close()
