import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 导出KK全量数据用于复查
cur.execute("""
    SELECT id, name, category 
    FROM products WHERE supplier_id=10 
    ORDER BY id
""")
rows = cur.fetchall()
print(f"KK总数据: {len(rows)} 条")

# 按当前分类分组，看每类的商品名称抽样
cur.execute("""
    SELECT category, COUNT(*) as cnt 
    FROM products WHERE supplier_id=10 
    GROUP BY category ORDER BY cnt DESC
""")
cats = cur.fetchall()
print("\n各分类抽样:")
for cat, cnt in cats:
    cur.execute("""
        SELECT id, name FROM products 
        WHERE supplier_id=10 AND category=%s 
        ORDER BY RAND() LIMIT 3
    """, (cat,))
    samples = cur.fetchall()
    print(f"\n  [{cat}] ({cnt}条)")
    for s in samples:
        print(f"    ID:{s[0]} {s[1][:70] if s[1] else 'N/A'}")

conn.close()
