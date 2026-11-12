import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-16
  {"id": 17793, "category": "厨房餐具", "desc": "儿童不锈钢分格便当盒"},
  {"id": 17794, "category": "厨房餐具", "desc": "儿童不锈钢双层便当盒"},
  {"id": 17795, "category": "厨房储物", "desc": "灰色超细纤维碗碟沥水垫"},
  {"id": 17796, "category": "厨房储物", "desc": "白色人字纹吸水沥水垫"},
  {"id": 17797, "category": "厨房餐具", "desc": "玻璃调味瓶盐罐带不锈钢撒料盖"},
  {"id": 17798, "category": "餐饮用品", "desc": "户外露营不锈钢保温水壶"},
  {"id": 17799, "category": "餐饮用品", "desc": "户外露营不锈钢保温水壶多色款"},
  {"id": 17800, "category": "餐饮用品", "desc": "玻璃木塞水壶配4只玻璃杯"},
  {"id": 17801, "category": "餐饮用品", "desc": "儿童塑料吸管水杯5色款"},
  {"id": 17802, "category": "餐饮用品", "desc": "儿童塑料吸管水杯多色款"},
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
