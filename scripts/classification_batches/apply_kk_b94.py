import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b94: 20条 玩具游戏→箱包配件 (32563-32582)
b94 = [
    (32563, '箱包配件'), (32564, '箱包配件'), (32565, '箱包配件'),
    (32566, '箱包配件'), (32567, '箱包配件'), (32568, '箱包配件'),
    (32569, '箱包配件'), (32570, '箱包配件'), (32571, '箱包配件'),
    (32572, '箱包配件'), (32573, '箱包配件'), (32574, '箱包配件'),
    (32575, '箱包配件'), (32576, '箱包配件'), (32577, '箱包配件'),
    (32578, '箱包配件'), (32579, '箱包配件'), (32580, '箱包配件'),
    (32581, '箱包配件'), (32582, '箱包配件')
]
for pid, cat in b94:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
conn.commit()
print(f"b94: {len(b94)}条写入完成")
conn.close()
