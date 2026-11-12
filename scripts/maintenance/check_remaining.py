import sys
sys.stdout.reconfigure(encoding='utf-8')
import pymysql

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# 查看剩余9条无分类商品的详情
cur.execute("SELECT id, supplier_id, name, sku, image_local FROM products WHERE category IS NULL OR category = '' ORDER BY id")
rows = cur.fetchall()
print(f"剩余无分类商品 {len(rows)} 条:")
for r in rows:
    print(f"  id={r['id']} supplier={r['supplier_id']} name={r['name']} sku={r['sku']} img={r['image_local']}")

conn.close()
