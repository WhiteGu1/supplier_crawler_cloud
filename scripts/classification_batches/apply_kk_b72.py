import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute("UPDATE products SET category=%s WHERE id=%s", ('玩具游戏', 31456))
conn.commit()
print("b72: 1条修正写入完成 (ID 31456 日用百货→玩具游戏)")
conn.close()
