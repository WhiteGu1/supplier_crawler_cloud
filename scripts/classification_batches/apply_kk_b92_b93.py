import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b92: 2条修正
b92 = [
    (32489, '家居纺织'), (32490, '家居纺织')
]
for pid, cat in b92:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
conn.commit()
print(f"b92: {len(b92)}条写入完成")

# b93: 2条修正
b93 = [
    (32553, '婴幼儿用品'), (32554, '婴幼儿用品')
]
for pid, cat in b93:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
conn.commit()
print(f"b93: {len(b93)}条写入完成")
conn.close()
