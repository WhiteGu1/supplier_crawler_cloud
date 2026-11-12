import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-16
  {"id": 25074, "category": "收纳整理", "desc": "竹制沙发扶手托盘"},
  {"id": 25075, "category": "厨房储物", "desc": "玻璃保鲜盒三件套蓝色密封盖"},
  {"id": 25076, "category": "装饰品", "desc": "木制墙面置物架配花瓶"},
  {"id": 25077, "category": "卫浴用品", "desc": "透明强力无痕吸盘挂钩"},
  {"id": 25078, "category": "装饰品", "desc": "流苏地毯棉麻条纹"},
  {"id": 25079, "category": "装饰品", "desc": "雪尼尔流苏几何图案地毯"},
  {"id": 25080, "category": "派对用品", "desc": "小号礼品盒套装配丝带"},
  {"id": 25081, "category": "厨房储物", "desc": "透明玻璃糖果碗带盖波浪边"},
  {"id": 25082, "category": "厨房储物", "desc": "水晶玻璃糖罐菱格纹雕刻"},
  {"id": 25083, "category": "厨房储物", "desc": "琥珀色条纹玻璃储物罐带盖"},
  # benabi2-batch-17
  {"id": 25084, "category": "厨房储物", "desc": "带盖条纹玻璃储物罐"},
  {"id": 25085, "category": "餐饮用品", "desc": "灰色PVC编织餐垫"},
  {"id": 25086, "category": "餐饮用品", "desc": "圆形草编餐垫"},
  {"id": 25087, "category": "餐饮用品", "desc": "黑色圆形草编餐垫隔热垫"},
  {"id": 25088, "category": "餐饮用品", "desc": "圆形草编餐垫米色棉布包边"},
  {"id": 25089, "category": "装饰品", "desc": "编织流苏地毯入户门垫"},
  {"id": 25090, "category": "餐饮用品", "desc": "编织餐垫两件套黑白"},
  {"id": 25091, "category": "餐饮用品", "desc": "白色圆形编织餐垫"},
  {"id": 25092, "category": "照明灯具", "desc": "电池供电星形LED串灯"},
  {"id": 25093, "category": "照明灯具", "desc": "黄铜色金属台灯无线充电款"},
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
