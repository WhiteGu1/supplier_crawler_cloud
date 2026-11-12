import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b9: 37条修正
# 砧板/切板 12条 → 厨房炊具 (28307-28318)
for pid in range(28307, 28319):
    cur.execute("UPDATE products SET category='厨房炊具' WHERE id=%s", (pid,))

# 托盘/早餐架 25条 → 餐饮用品 (28319-28342)
for pid in range(28319, 28343):
    cur.execute("UPDATE products SET category='餐饮用品' WHERE id=%s", (pid,))

conn.commit()
print("b9: 37条写入完成")

# 总进度统计
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=10")
total = cur.fetchone()[0]
cur.execute("SELECT category, COUNT(*) FROM products WHERE supplier_id=10 GROUP BY category ORDER BY COUNT(*) DESC")
cats = cur.fetchall()
print(f"\nKK供应商总数据: {total}条")
print("分类分布:")
for cat, cnt in cats:
    print(f"  {cat}: {cnt}")

conn.close()
