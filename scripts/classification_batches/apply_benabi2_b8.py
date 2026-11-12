import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-8
  {"id": 24919, "category": "厨房炊具", "desc": "硅胶裱花袋套装"},
  {"id": 24920, "category": "收纳整理", "desc": "金属网格储物篮木质把手"},
  {"id": 24921, "category": "收纳整理", "desc": "金属网格储物篮木质把手"},
  {"id": 24922, "category": "收纳整理", "desc": "深灰色布艺折叠收纳箱"},
  {"id": 24923, "category": "收纳整理", "desc": "布艺折叠收纳箱深灰米白"},
  {"id": 24924, "category": "厨房储物", "desc": "厨房台面下挂式金属置物架"},
  {"id": 24925, "category": "装饰品", "desc": "拱形黑色边框装饰镜"},
  {"id": 24926, "category": "装饰品", "desc": "圆形金色边框装饰镜"},
  {"id": 24927, "category": "装饰品", "desc": "圆形黑色边框装饰镜"},
  {"id": 24928, "category": "收纳整理", "desc": "门后挂式衣钩架"},
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
