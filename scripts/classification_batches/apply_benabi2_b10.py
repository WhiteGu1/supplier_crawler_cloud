import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-10 (all hair brushes)
  {"id": 24934, "category": "美妆个护", "desc": "椭圆按摩气囊梳粉白配色"},
  {"id": 24935, "category": "美妆个护", "desc": "圆筒卷发梳粉白配色"},
  {"id": 24936, "category": "美妆个护", "desc": "矩形卷发梳粉米色"},
  {"id": 24937, "category": "美妆个护", "desc": "椭圆气囊按摩梳马卡龙配色"},
  {"id": 24938, "category": "美妆个护", "desc": "椭圆气囊按摩梳粉蓝绿紫"},
  {"id": 24939, "category": "美妆个护", "desc": "椭圆猪鬃美发梳原木手柄"},
  {"id": 24940, "category": "美妆个护", "desc": "椭圆猪鬃美发梳原木手柄"},
  {"id": 24941, "category": "美妆个护", "desc": "椭圆气囊梳糖果色冰棒手柄"},
  {"id": 24942, "category": "美妆个护", "desc": "椭圆气囊梳马卡龙色"},
  {"id": 24943, "category": "美妆个护", "desc": "矩形气囊按摩梳马卡龙色"},
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
