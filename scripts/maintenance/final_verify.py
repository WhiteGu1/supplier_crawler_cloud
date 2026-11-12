import sys
sys.stdout.reconfigure(encoding='utf-8')
import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# Final verification
cur.execute("SELECT COUNT(*) FROM products")
total_products = cur.fetchone()[0]
print('Total products:', total_products)

cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category=''")
uncat = cur.fetchone()[0]
print('Uncategorized products:', uncat)

cur.execute("SELECT COUNT(*) FROM products WHERE is_new=1")
new_products = cur.fetchone()[0]
print('is_new=1 products:', new_products)

cur.execute("SELECT COUNT(*) FROM products WHERE is_new=1 AND (category IS NULL OR category='')")
new_uncat = cur.fetchone()[0]
print('is_new=1 uncategorized:', new_uncat)

cur.execute("SELECT COUNT(*) FROM product_categories")
total_pc = cur.fetchone()[0]
print('product_categories rows:', total_pc)

cur.execute("SELECT COUNT(DISTINCT product_id) FROM product_categories")
pc_products = cur.fetchone()[0]
print('products in product_categories:', pc_products)

cur.execute("SELECT COUNT(DISTINCT category) FROM product_categories")
unique_cats = cur.fetchone()[0]
print('unique category paths:', unique_cats)

# Verify 36008-36022 are categorized
cur.execute("SELECT id, category FROM products WHERE id BETWEEN 36008 AND 36022 ORDER BY id")
print()
print('HUDSON 36008-36022 status:')
for r in cur.fetchall():
    print(' ', r)

conn.close()