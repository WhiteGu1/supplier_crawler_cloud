import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

# 模拟修复后的查询：主分类="玩具游戏"
cat = "玩具游戏"
sql = "SELECT COUNT(*) as total FROM products p JOIN suppliers s ON p.supplier_id=s.id WHERE p.is_available=1 AND (p.category=%s OR p.category LIKE %s)"
cur.execute(sql, (cat, cat + " > %"))
r = cur.fetchone()
print(f"主分类='玩具游戏' -> {r['total']} 条")

# 测试其他分类
for c in ['厨房餐具', '家居装饰', '箱包配件', '文具办公']:
    cur.execute(sql, (c, c + " > %"))
    r = cur.fetchone()
    print(f"主分类='{c}' -> {r['total']} 条")

# 测试全部分类
cur.execute("SELECT category, COUNT(*) as cnt FROM products WHERE is_available=1 GROUP BY category ORDER BY cnt DESC LIMIT 10")
print("\nTop 10 categories:")
for r in cur.fetchall():
    print(f"  '{r['category']}' -> {r['cnt']}")

conn.close()
