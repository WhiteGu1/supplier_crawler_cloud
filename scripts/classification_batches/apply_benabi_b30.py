import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-30
  {"id": 17933, "category": "文具办公", "desc": "Touch品牌12色双头马克笔套装"},
  {"id": 17934, "category": "文具办公", "desc": "Touch品牌24色双头马克笔套装"},
  {"id": 17935, "category": "文具办公", "desc": "Touch品牌36色双头马克笔套装"},
  {"id": 17936, "category": "文具办公", "desc": "Touch品牌60色双头马克笔套装"},
  {"id": 17937, "category": "文具办公", "desc": "18色丙烯马克笔套装"},
  {"id": 17938, "category": "文具办公", "desc": "36色丙烯马克笔套装"},
  {"id": 17939, "category": "文具办公", "desc": "48色丙烯马克笔套装"},
  {"id": 17940, "category": "文具办公", "desc": "60色丙烯马克笔套装"},
  {"id": 17941, "category": "文具办公", "desc": "白板笔3支套装配板擦"},
  {"id": 17942, "category": "文具办公", "desc": "荧光笔6支装"},
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
