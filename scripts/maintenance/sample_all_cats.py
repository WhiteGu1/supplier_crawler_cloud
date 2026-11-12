import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 获取所有二级分类
cur.execute("""
    SELECT category, COUNT(*) as cnt 
    FROM products WHERE is_available=1 AND category LIKE '% > %' 
    GROUP BY category ORDER BY cnt DESC
""")
cats = cur.fetchall()

for c in cats:
    cat = c[0]
    cnt = c[1]
    print(f"\n{'='*80}")
    print(f"【{cat}】({cnt}条)")
    print(f"{'='*80}")
    # 取前30个商品名
    cur.execute("SELECT name FROM products WHERE is_available=1 AND category=%s LIMIT 30", (cat,))
    for r in cur.fetchall():
        print(f"  {r[0]}")

conn.close()
