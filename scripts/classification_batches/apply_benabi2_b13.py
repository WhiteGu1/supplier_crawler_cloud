import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-13
  {"id": 24964, "category": "厨房餐具", "desc": "硅胶木柄不粘厨勺"},
  {"id": 24965, "category": "厨房餐具", "desc": "硅胶木柄漏勺"},
  {"id": 24966, "category": "厨房餐具", "desc": "硅胶木柄汤勺"},
  {"id": 24967, "category": "厨房餐具", "desc": "厨房刀具套装含剪刀刀架"},
  {"id": 24968, "category": "厨房餐具", "desc": "不锈钢切肉大刀"},
  {"id": 24969, "category": "餐饮用品", "desc": "6件套不锈钢吸管"},
  {"id": 24970, "category": "厨房餐具", "desc": "硅胶防烫隔热手套"},
  {"id": 24971, "category": "婴幼儿用品", "desc": "卡通动物儿童背带水杯"},
  {"id": 24972, "category": "婴幼儿用品", "desc": "卡通动物造型儿童水杯"},
  {"id": 24973, "category": "婴幼儿用品", "desc": "熊猫青蛙卡通儿童背带水杯"},
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
