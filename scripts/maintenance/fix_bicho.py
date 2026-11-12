import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
ids = [18327,18328,18329,18330,18331,18332,18333]
updated = 0
for pid in ids:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", ("其他", pid))
    updated += cur.rowcount
conn.commit()
print(f"BICHO RED: {updated}/7")
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=3 AND (category IS NULL OR category='') AND is_available=1")
print(f"Trapoman remaining: {cur.fetchone()[0]}")
conn.close()
