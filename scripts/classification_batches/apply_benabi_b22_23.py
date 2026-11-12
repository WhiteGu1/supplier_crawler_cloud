import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-22
  {"id": 17853, "category": "厨房餐具", "desc": "透明玻璃水杯配金色搅拌棒"},
  {"id": 17854, "category": "厨房餐具", "desc": "竖条纹纹理玻璃水杯与花瓶组合"},
  {"id": 17855, "category": "婴幼儿用品", "desc": "卡通动物造型儿童吸管水杯"},
  {"id": 17856, "category": "婴幼儿用品", "desc": "卡通图案分格便当饭盒"},
  {"id": 17857, "category": "婴幼儿用品", "desc": "动物图案儿童塑料便当盒"},
  {"id": 17858, "category": "厨房餐具", "desc": "不锈钢分隔保鲜饭盒"},
  {"id": 17859, "category": "厨房储物", "desc": "灰色硅胶沥水架搭配吸水抹布"},
  {"id": 17860, "category": "厨房储物", "desc": "琥珀色玻璃储物罐配木质盖"},
  {"id": 17861, "category": "婴幼儿用品", "desc": "卡通长颈鹿图案儿童便当盒"},
  {"id": 17862, "category": "婴幼儿用品", "desc": "卡通动物图案儿童便当盒"},
  # batch-23
  {"id": 17863, "category": "厨房储物", "desc": "玻璃胡椒研磨器黑色硅胶盖"},
  {"id": 17864, "category": "餐饮用品", "desc": "NAENSO桌布套装绿叶印花"},
  {"id": 17865, "category": "厨房餐具", "desc": "双层玻璃茶杯套装"},
  {"id": 17866, "category": "厨房炊具", "desc": "Benabi法式滤压咖啡壶"},
  {"id": 17867, "category": "厨房炊具", "desc": "Benabi法式滤压咖啡壶"},
  {"id": 17868, "category": "厨房炊具", "desc": "Benabi法式滤压咖啡壶"},
  {"id": 17869, "category": "餐饮用品", "desc": "红色硅胶餐垫竹纤维面料"},
  {"id": 17870, "category": "厨房餐具", "desc": "彩色硅胶蛋糕马芬杯套装"},
  {"id": 17871, "category": "厨房储物", "desc": "不锈钢保温水壶带提手"},
  {"id": 17872, "category": "收纳整理", "desc": "竹制餐具收纳架分格设计"},
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
