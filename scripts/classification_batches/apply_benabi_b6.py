import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-6
  {"id": 17325, "category": "收纳整理", "desc": "棉绳编织浴室毛巾收纳篮"},
  {"id": 17326, "category": "厨房储物", "desc": "棉绳编织双耳水果面包篮"},
  {"id": 17327, "category": "厨房储物", "desc": "棉绳编织双耳水果面包篮"},
  {"id": 17328, "category": "收纳整理", "desc": "棉绳编织方形杂物收纳篮"},
  {"id": 17329, "category": "收纳整理", "desc": "黑色折叠式脏衣篮木质边框"},
  {"id": 17330, "category": "收纳整理", "desc": "布艺折叠脏衣篓带提手"},
  {"id": 17331, "category": "清洁用品", "desc": "银丝金属丝清洁布厨房抹布"},
  {"id": 17332, "category": "装饰品", "desc": "黑色金属框圆形装饰镜"},
  {"id": 17333, "category": "装饰品", "desc": "黑色金属框圆形装饰镜"},
  {"id": 17334, "category": "装饰品", "desc": "黑色金属框圆形装饰镜"},
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
