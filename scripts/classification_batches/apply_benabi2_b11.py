import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-11
  {"id": 24944, "category": "美妆个护", "desc": "三色塑料气垫梳"},
  {"id": 24945, "category": "美妆个护", "desc": "三色椭圆气垫梳"},
  {"id": 24946, "category": "美妆个护", "desc": "木柄椭圆卷发气囊梳"},
  {"id": 24947, "category": "美妆个护", "desc": "木柄方形按摩梳套装"},
  {"id": 24948, "category": "美妆个护", "desc": "粉色金属柄便携卷发梳"},
  {"id": 24949, "category": "美妆个护", "desc": "紫色金属柄便携卷发梳"},
  {"id": 24950, "category": "美妆个护", "desc": "三色椭圆气囊梳"},
  {"id": 24951, "category": "美妆个护", "desc": "LOVELY梳子套装"},
  {"id": 24952, "category": "卫浴用品", "desc": "PEVA环保浴室浴帘含挂钩"},
  {"id": 24953, "category": "卫浴用品", "desc": "PEVA浴室浴帘含金属钩"},
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
