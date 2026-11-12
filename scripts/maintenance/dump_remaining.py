import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute('SELECT id, name FROM products WHERE supplier_id=3 AND (category IS NULL OR category="") AND is_available=1 ORDER BY id')
rows = cur.fetchall()
with open('D:/projects/supplier_crawler/trapoman_remaining.txt', 'w', encoding='utf-8') as f:
    for pid, name in rows:
        f.write(f'{pid}\t{name}\n')
print(f'wrote {len(rows)} rows')
conn.close()
