import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b20: 16条修正
# 玩具游戏→婴幼儿用品 (14条: 婴儿餐具/学饮杯)
b20_baby = list(range(28890, 28904))
for pid in b20_baby:
    cur.execute("UPDATE products SET category='婴幼儿用品' WHERE id=%s", (pid,))

# 玩具游戏→厨房餐具 (2条: 铝制水瓶)
b20_tableware = [28904, 28905]
for pid in b20_tableware:
    cur.execute("UPDATE products SET category='厨房餐具' WHERE id=%s", (pid,))

conn.commit()
print(f"b20: {len(b20_baby) + len(b20_tableware)}条写入完成")
conn.close()
