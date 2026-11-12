import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# Remaining 10 products are all HUDSON 餐具 (Tenedor=叉, Cuchillo=刀, Juego de cubiertos=餐具套装, Cuchara de te=茶匙, Cuchara de Mesa=餐匙)
# They map to 厨房用品 > 餐具 > 刀叉勺
remaining = [
    (36008, 'Tenedor de Mesa negro HUDSON x 3'),
    (36009, 'Cuchillo de Mesa azul HUDSON x 12'),
    (36010, 'Cuchillo de Mesa negro HUDSON x 12'),
    (36011, 'Cuchillo de Mesa azul HUDSON x 3'),
    (36012, 'Cuchillo de Mesa negro HUDSON x 3'),
    (36013, 'Juego de cubiertos HUDSON Linea Daily 24 piezas'),
    (36014, 'Juego de cubiertos HUDSON Linea Daily 16 piezas'),
    (36015, 'Cuchara de te negro HUDSON x12'),
    (36016, 'Cuchara de Mesa negro HUDSON x12'),
    (36017, 'Tenedor de Mesa negro HUDSON x12'),
]

cat = '厨房用品 > 餐具 > 刀叉勺'
for pid, name in remaining:
    cur.execute("SELECT id FROM product_categories WHERE product_id=%s AND category=%s", (pid, cat))
    if cur.fetchone():
        print(f'{pid} {name[:30]}: already exists')
        continue
    cur.execute("INSERT INTO product_categories (product_id, category) VALUES (%s, %s)", (pid, cat))
    print(f'{pid} {name[:30]}: inserted')

# Also sync products.category
for pid, _ in remaining:
    cur.execute("UPDATE products SET category=%s WHERE id=%s AND (category IS NULL OR category='')", (cat, pid))

conn.commit()
print('Done. Total updated:', cur.rowcount)

# Verify
cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category=''")
print('Remaining uncategorized:', cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM product_categories")
print('Total product_categories rows:', cur.fetchone()[0])

conn.close()