import pymysql, json, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

total = 0
for fname in ['diego10_r2b2_result.json', 'diego10_r2b3_result.json']:
    path = f'D:/projects/supplier_crawler/{fname}'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for item in data:
        cur.execute("UPDATE products SET category=%s WHERE id=%s", (item['category'], item['id']))
    total += len(data)
    print(f"{fname}: {len(data)} 条")

conn.commit()
print(f"\n总计更新 {total} 条记录")
conn.close()
