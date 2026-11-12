import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-40
  {"id": 20305, "category": "卫浴用品", "desc": "浴室防滑地垫"},
  {"id": 20306, "category": "卫浴用品", "desc": "浴室防滑地垫"},
  {"id": 20307, "category": "卫浴用品", "desc": "浴室防滑地垫"},
  {"id": 20308, "category": "卫浴用品", "desc": "浴室防滑地垫"},
  {"id": 20309, "category": "卫浴用品", "desc": "浴室防滑地垫"},
  {"id": 20310, "category": "装饰品", "desc": "抱枕"},
  {"id": 20311, "category": "装饰品", "desc": "抱枕"},
  {"id": 20312, "category": "装饰品", "desc": "抱枕"},
  {"id": 20313, "category": "装饰品", "desc": "抱枕"},
  {"id": 20314, "category": "装饰品", "desc": "抱枕"},
  # batch-41
  {"id": 20315, "category": "厨房炊具", "desc": "不锈钢开罐器"},
  {"id": 20316, "category": "餐饮用品", "desc": "电动红酒开瓶器"},
  {"id": 20317, "category": "厨房炊具", "desc": "5件套硅胶刮刀铲"},
  {"id": 20318, "category": "厨房炊具", "desc": "5件套厨房刀具礼盒"},
  {"id": 20319, "category": "厨房炊具", "desc": "4件套不锈钢奶酪刨丝器"},
  {"id": 20320, "category": "餐饮用品", "desc": "透明玻璃油壶醋瓶"},
  {"id": 20321, "category": "厨房储物", "desc": "竹木旋转调味罐架"},
  {"id": 20322, "category": "厨房炊具", "desc": "方形竹木砧板"},
  {"id": 20323, "category": "婴幼儿用品", "desc": "儿童吸管水杯配卡通挂饰"},
  {"id": 20324, "category": "运动户外", "desc": "迷彩便携运动水壶"},
  # batch-42
  {"id": 20325, "category": "餐饮用品", "desc": "三色塑料运动水瓶"},
  {"id": 20326, "category": "餐饮用品", "desc": "磨砂金属运动水瓶三件套"},
  {"id": 20327, "category": "厨房储物", "desc": "波浪纹玻璃储物罐带木盖"},
  {"id": 20328, "category": "厨房储物", "desc": "木盖透明玻璃储物罐"},
  {"id": 20329, "category": "厨房储物", "desc": "木盖玻璃调料储物罐三件套"},
  {"id": 20330, "category": "餐饮用品", "desc": "带把玻璃水杯3件套"},
  {"id": 20331, "category": "厨房储物", "desc": "南瓜形木盖透明玻璃储物罐"},
  {"id": 20332, "category": "餐饮用品", "desc": "菱形纹理玻璃冷水壶"},
  {"id": 20333, "category": "餐饮用品", "desc": "竖纹玻璃凉水壶"},
  {"id": 20334, "category": "厨房储物", "desc": "硅胶半球盖圆形冰格模具"},
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
