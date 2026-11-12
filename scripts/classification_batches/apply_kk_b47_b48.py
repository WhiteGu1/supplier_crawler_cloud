import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b47: 7条修正
b47 = [
    (30217, '箱包配件'), (30218, '数码科技'), (30220, '箱包配件'),
    (30221, '箱包配件'), (30222, '箱包配件'),
    (30223, '数码科技'), (30224, '数码科技')
]

# b48: 12条修正 花盆/浇水壶→园艺户外
b48 = [
    (30282, '园艺户外'), (30283, '园艺户外'), (30284, '园艺户外'),
    (30286, '园艺户外'), (30287, '园艺户外'), (30288, '园艺户外'),
    (30289, '园艺户外'), (30290, '园艺户外'), (30291, '园艺户外'),
    (30292, '园艺户外'), (30293, '园艺户外'), (30295, '园艺户外')
]

for pid, cat in b47:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
for pid, cat in b48:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b47: {len(b47)}条, b48: {len(b48)}条, 共{len(b47)+len(b48)}条写入完成")
conn.close()
