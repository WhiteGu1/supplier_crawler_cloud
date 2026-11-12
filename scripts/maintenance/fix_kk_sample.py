import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 修正抽样发现的2条
fixes = [
    (28914, '厨房餐具'),
    (32247, '服装服饰'),
]
for pid, cat in fixes:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
    print(f"  ID:{pid} -> {cat} ({cur.rowcount}条)")

conn.commit()

# 确认服装服饰分类是否在标准列表中
cur.execute("SELECT COUNT(*) FROM products WHERE category='服装服饰'")
cnt = cur.fetchone()[0]
print(f"\n服装服饰分类总数: {cnt}")

conn.close()
