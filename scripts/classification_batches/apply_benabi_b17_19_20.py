import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-16 (pending)
  # batch-17
  {"id": 17803, "category": "餐饮用品", "desc": "四款不锈钢保温吸管杯"},
  {"id": 17804, "category": "清洁用品", "desc": "陶瓷质感带木柄清洁刷"},
  {"id": 17805, "category": "厨房储物", "desc": "黑色金属网抽屉式厨房收纳篮"},
  {"id": 17806, "category": "厨房储物", "desc": "黑色金属网抽屉式厨房储物篮"},
  {"id": 17807, "category": "装饰品", "desc": "沙发抱枕组合多色"},
  {"id": 17808, "category": "装饰品", "desc": "米色立体锯齿纹路装饰抱枕"},
  {"id": 17809, "category": "装饰品", "desc": "白底紫色竖条纹装饰抱枕"},
  {"id": 17810, "category": "装饰品", "desc": "三色椅垫坐垫带绑带"},
  {"id": 17811, "category": "派对用品", "desc": "灰色和黑色礼盒套装"},
  {"id": 17812, "category": "派对用品", "desc": "黑色配金色丝带礼品盒"},
  # batch-19
  {"id": 17823, "category": "装饰品", "desc": "户外阳台人造草坪地垫"},
  {"id": 17824, "category": "装饰品", "desc": "复古组合相框墙饰"},
  {"id": 17825, "category": "装饰品", "desc": "多格组合相框墙饰"},
  {"id": 17826, "category": "装饰品", "desc": "黑白组合相框墙饰"},
  {"id": 17827, "category": "卫浴用品", "desc": "菱形纹浴室地垫"},
  {"id": 17828, "category": "清洁用品", "desc": "网纱沐浴球"},
  {"id": 17829, "category": "卫浴用品", "desc": "彩色花朵造型擦澡球"},
  {"id": 17830, "category": "宠物用品", "desc": "灰色羊羔绒宠物窝三件套"},
  {"id": 17831, "category": "宠物用品", "desc": "灰色方形羊羔绒宠物窝床"},
  {"id": 17832, "category": "宠物用品", "desc": "灰色脚印图案宠物窝垫三件套"},
  # batch-20
  {"id": 17833, "category": "宠物用品", "desc": "灰色爪印图案宠物狗床垫"},
  {"id": 17834, "category": "宠物用品", "desc": "灰色爪印图案方形宠物狗床垫"},
  {"id": 17835, "category": "宠物用品", "desc": "蓝色爪印图案圆形宠物窝"},
  {"id": 17836, "category": "宠物用品", "desc": "蓝色爪印图案圆形宠物窝"},
  {"id": 17837, "category": "宠物用品", "desc": "蓝色爪印图案圆形宠物窝"},
  {"id": 17838, "category": "宠物用品", "desc": "蓝色爪印图案圆形宠物窝"},
  {"id": 17839, "category": "宠物用品", "desc": "蓝色爪印图案圆形宠物窝"},
  {"id": 17840, "category": "宠物用品", "desc": "蓝色爪印图案圆形宠物窝"},
  {"id": 17841, "category": "厨房炊具", "desc": "木柄硅胶铲"},
  {"id": 17842, "category": "厨房炊具", "desc": "木质手柄圆锥形奶酪刨丝器"},
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
