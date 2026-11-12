import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
# 检查supplier_id=5的商品ID范围和image_local前缀
cur.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM products WHERE supplier_id=5")
print('Diego(supplier_id=5):', cur.fetchone())
# 检查ID>2475的supplier_id=5的商品图片路径
cur.execute("SELECT id, name, image_local FROM products WHERE supplier_id=5 AND id > 2475 AND image_local IS NOT NULL AND image_local != '' ORDER BY id LIMIT 5")
for r in cur.fetchall():
    print(f'  ID:{r[0]} name:{r[1][:30]} img:{r[2][:50]}')
# 检查images/osa路径的商品属于哪个供应商
cur.execute("SELECT supplier_id, COUNT(*) FROM products WHERE image_local LIKE 'images/osa/%' GROUP BY supplier_id")
print('images/osa/ 供应商分布:', cur.fetchall())
# 检查Diego供应商的图片路径前缀
cur.execute("SELECT SUBSTRING_INDEX(image_local, '/', 2) as prefix, COUNT(*) FROM products WHERE supplier_id=5 AND image_local IS NOT NULL AND image_local != '' GROUP BY prefix")
print('Diego图片路径前缀:', cur.fetchall())
conn.close()
