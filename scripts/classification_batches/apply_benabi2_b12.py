import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-12
  {"id": 24954, "category": "卫浴用品", "desc": "多款图案PEVA浴帘套装"},
  {"id": 24955, "category": "卫浴用品", "desc": "灰色几何图案浴帘搭配防滑地垫"},
  {"id": 24956, "category": "卫浴用品", "desc": "14件套奢华浴帘套装"},
  {"id": 24957, "category": "电器电子", "desc": "便携式USB夹式小风扇"},
  {"id": 24958, "category": "餐饮用品", "desc": "不锈钢礼盒装葡萄酒开瓶器套装"},
  {"id": 24959, "category": "厨房炊具", "desc": "不锈钢双层蒸煮汤锅"},
  {"id": 24960, "category": "厨房炊具", "desc": "硅胶漏勺铲木柄"},
  {"id": 24961, "category": "厨房炊具", "desc": "迷你厨房工具三件套"},
  {"id": 24962, "category": "厨房炊具", "desc": "不锈钢蒜泥器压蒜器"},
  {"id": 24963, "category": "餐饮用品", "desc": "不锈钢螺旋鸡尾酒过滤网"},
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
