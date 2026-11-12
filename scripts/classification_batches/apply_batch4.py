import pymysql, json, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

with open('D:/projects/supplier_crawler/diego50_batch4_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (item['category'], item['id']))
    print(f"  ID:{item['id']} -> {item['category']}")

conn.commit()
print(f"\n已更新 {len(data)} 条记录")
conn.close()
