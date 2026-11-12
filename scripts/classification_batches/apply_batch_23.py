import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-23
  {"id": 2406, "category": "照明灯具", "desc": "Candela LED灯泡 20W E27螺口"},
  {"id": 2407, "category": "照明灯具", "desc": "Candela LED高功率灯泡 30W E27"},
  {"id": 2408, "category": "照明灯具", "desc": "Candela LED高功率灯泡 40W E27"},
  {"id": 2409, "category": "照明灯具", "desc": "Candela LED高功率灯泡 48W"},
  {"id": 2410, "category": "照明灯具", "desc": "Candela LED高功率灯泡 70W"},
  {"id": 2411, "category": "照明灯具", "desc": "Candela LED高功率灯泡 9W E27"},
  {"id": 2412, "category": "照明灯具", "desc": "Candela LED灯泡 12W E27"},
  {"id": 2413, "category": "照明灯具", "desc": "Candela LED经典款灯泡 15W E27"},
  {"id": 2414, "category": "照明灯具", "desc": "Candela LED灯泡 7W E27"},
  {"id": 2415, "category": "派对用品", "desc": "六色节日主题闪光胶水笔套装"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"成功更新 {updated}/{len(results)} 条")
conn.close()
