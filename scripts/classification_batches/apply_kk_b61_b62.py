import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b61: 44条 派对用品→时尚配饰 (30906-30949)
b61_ids = list(range(30906, 30950))
b61 = [(pid, '时尚配饰') for pid in b61_ids]

# b62: 20条 + 2条补充 = 22条
b62 = [
    (30970, '宠物用品'), (30971, '宠物用品'), (30972, '宠物用品'),
    (30973, '宠物用品'), (30974, '宠物用品'), (30975, '宠物用品'),
    (30976, '宠物用品'), (30977, '宠物用品'), (30978, '宠物用品'),
    (30979, '宠物用品'), (30980, '宠物用品'), (30981, '宠物用品'),
    (30983, '婴幼儿用品'), (30984, '五金工具'),
    (30985, '日用百货'), (30986, '婴幼儿用品'),
    (30987, '日用百货'), (30988, '日用百货'),
    (30990, '日用百货'), (30991, '日用百货'),
    # 补充2条
    (30989, '日用百货'), (30992, '五金工具')
]

for pid, cat in b61:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
for pid, cat in b62:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b61: {len(b61)}条, b62: {len(b62)}条, 共{len(b61)+len(b62)}条写入完成")
conn.close()
