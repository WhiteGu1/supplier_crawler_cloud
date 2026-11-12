# -*- coding: utf-8 -*-
import pymysql
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123',
                       database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# product_categories表结构
cur.execute("SHOW COLUMNS FROM product_categories")
print('product_categories字段:')
for row in cur.fetchall():
    print(f'  {row[0]} ({row[1]})')

# 查看多分类样本
cur.execute("SELECT * FROM product_categories LIMIT 5")
print('\nproduct_categories样本:')
for row in cur.fetchall():
    print(f'  {row}')

# 查看中文一级分类
cur.execute("""SELECT DISTINCT SUBSTRING_INDEX(category, ' > ', 1) AS cat1 
FROM products WHERE category IS NOT NULL AND category != '' 
AND category NOT LIKE '%A%' AND category NOT LIKE '%B%' AND category NOT LIKE '%C%' 
AND category NOT LIKE '%D%' AND category NOT LIKE '%E%' AND category NOT LIKE '%F%' 
AND category NOT LIKE '%G%' AND category NOT LIKE '%H%' AND category NOT LIKE '%I%' 
AND category NOT LIKE '%J%' AND category NOT LIKE '%K%' AND category NOT LIKE '%L%' 
AND category NOT LIKE '%M%' AND category NOT LIKE '%N%' AND category NOT LIKE '%O%' 
AND category NOT LIKE '%P%' AND category NOT LIKE '%Q%' AND category NOT LIKE '%R%' 
AND category NOT LIKE '%S%' AND category NOT LIKE '%T%' AND category NOT LIKE '%U%' 
AND category NOT LIKE '%V%' AND category NOT LIKE '%W%' AND category NOT LIKE '%X%' 
AND category NOT LIKE '%Y%' AND category NOT LIKE '%Z%'
ORDER BY cat1""")
print('\n中文一级分类:')
for row in cur.fetchall():
    print(f'  {row[0]}')

conn.close()
