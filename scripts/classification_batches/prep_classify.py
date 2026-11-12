import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 总数
cur.execute('SELECT COUNT(*) FROM products WHERE is_available=1')
total = cur.fetchone()[0]
print(f'商品总数: {total}')

# 现有分类列表
cur.execute("SELECT DISTINCT category FROM products WHERE is_available=1 AND category IS NOT NULL AND category!='' ORDER BY category")
cats = [r[0] for r in cur.fetchall()]
print(f'现有分类数: {len(cats)}')

# 有图/无图
cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1 AND image_local IS NOT NULL AND image_local!=''")
has_img = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1 AND (image_local IS NULL OR image_local='')")
no_img = cur.fetchone()[0]
print(f'有图: {has_img}, 无图: {no_img}')

# 商品字段
cur.execute('DESCRIBE products')
fields = [r[0] for r in cur.fetchall()]
print(f'字段: {fields}')

# 取一条样本
cur.execute('SELECT id, name, sku, brand, supplier_id, price, category, image_local FROM products WHERE is_available=1 LIMIT 1')
r = cur.fetchone()
print(f'样本: id={r[0]}, name={r[1]}, sku={r[2]}, brand={r[3]}, sup_id={r[4]}, price={r[5]}, cat={r[6]}, img={r[7]}')

# 供应商名映射
cur.execute('SELECT id, name FROM suppliers')
sups = {r[0]: r[1] for r in cur.fetchall()}
print(f'供应商: {sups}')

conn.close()

# 输出分类列表
print('=== CATEGORY_LIST ===')
for c in cats:
    print(c)
