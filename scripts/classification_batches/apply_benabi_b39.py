import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-39
  {"id": 20295, "category": "厨房餐具", "desc": "四色不锈钢奶酪刨丝器套装"},
  {"id": 20296, "category": "厨房餐具", "desc": "绿色PP塑料切菜板"},
  {"id": 20297, "category": "厨房餐具", "desc": "橙色PP塑料切菜板"},
  {"id": 20298, "category": "餐饮用品", "desc": "透明竖纹玻璃水瓶带软木塞"},
  {"id": 20299, "category": "餐饮用品", "desc": "烟灰色竖纹玻璃水瓶带软木塞"},
  {"id": 20300, "category": "装饰品", "desc": "米灰白几何钻石图案毛绒簇绒抱枕"},
  {"id": 20301, "category": "装饰品", "desc": "米白灰雪佛龙箭头图案毛绒簇绒抱枕"},
  {"id": 20302, "category": "装饰品", "desc": "三色立体泡泡纹针织抱枕"},
  {"id": 20303, "category": "卫浴用品", "desc": "三色浴室防滑地垫带BATH字母"},
  {"id": 20304, "category": "卫浴用品", "desc": "三色长毛浴室防滑垫"},
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
