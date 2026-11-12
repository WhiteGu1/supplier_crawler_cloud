import pymysql
conn = pymysql.connect(host='localhost',user='root',password='admin123',database='supplier_crawler')
cursor = conn.cursor()
cursor.execute('SELECT id, name FROM suppliers')
print('suppliers:', cursor.fetchall())
cursor.execute('SELECT supplier_id, COUNT(*) FROM products GROUP BY supplier_id')
print('products:', cursor.fetchall())
conn.close()
