import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# KK供应商ID
cur.execute("SELECT id, name FROM suppliers WHERE name LIKE '%KK%' OR name LIKE '%kk%'")
print('=== KK供应商 ===')
for r in cur.fetchall():
    print(f'  id={r[0]} name={r[1]}')

# KK商品总数、可用、缺失、新商品
cur.execute("SELECT COUNT(*), SUM(is_available), SUM(is_missing), SUM(is_new) FROM products WHERE supplier_id=10")
r = cur.fetchone()
print(f'\n=== KK商品统计 ===')
print(f'  总数={r[0]} 可用={r[1]} 缺失={r[2]} 新商品={r[3]}')

# 最近导入的KK商品
cur.execute("SELECT id, name, sku, is_new, is_available, is_missing, created_at FROM products WHERE supplier_id=10 ORDER BY id DESC LIMIT 10")
print(f'\n=== KK最近10条商品 ===')
for r in cur.fetchall():
    print(f'  id={r[0]} sku={r[2]} new={r[3]} avail={r[4]} miss={r[5]} created={r[6]} name={r[1][:40]}')

# 所有供应商缺失统计
cur.execute("SELECT s.id, s.name, COUNT(*) as missing FROM products p JOIN suppliers s ON p.supplier_id=s.id WHERE p.is_missing=1 GROUP BY s.id ORDER BY missing DESC")
print(f'\n=== 各供应商缺失商品 ===')
for r in cur.fetchall():
    print(f'  {r[0]} {r[1]}: {r[2]}')

# KK今日导入的商品
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=10 AND created_at > NOW() - INTERVAL 1 DAY")
r = cur.fetchone()
print(f'\n=== KK今日导入 ===')
print(f'  今日新增={r[0]}')

# KK供应商创建时间
cur.execute("SELECT id, name, created_at FROM suppliers WHERE id=10")
r = cur.fetchone()
print(f'\n=== KK供应商信息 ===')
print(f'  id={r[0]} name={r[1]} created={r[2]}')

conn.close()
