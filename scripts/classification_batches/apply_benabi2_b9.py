import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-9
  {"id": 24904, "category": "厨房餐具", "desc": "黑色金字塔形奶酪擦丝器"},
  {"id": 24905, "category": "餐饮用品", "desc": "翼型酒瓶开瓶器套装"},
  {"id": 24906, "category": "厨房储物", "desc": "金属立式厨房纸巾架"},
  {"id": 24907, "category": "厨房储物", "desc": "木底座锅盖砧板收纳架"},
  {"id": 24908, "category": "厨房炊具", "desc": "不锈钢网状漏勺三件套"},
  {"id": 24929, "category": "收纳整理", "desc": "围巾腰带收纳挂架"},
  {"id": 24930, "category": "装饰品", "desc": "三色金属烛台"},
  {"id": 24931, "category": "装饰品", "desc": "黑色圆形茶几细金属腿"},
  {"id": 24932, "category": "卫浴用品", "desc": "浴室防滑地垫多色套装"},
  {"id": 24933, "category": "美妆个护", "desc": "气垫按摩梳"},
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
