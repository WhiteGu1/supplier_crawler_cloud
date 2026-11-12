import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-13 results
results13 = [
  {"id": 25054, "category": "厨房炊具", "desc": "法压壶法式滤压壶透明玻璃壶身配竹木盖和手柄"},
  {"id": 25055, "category": "厨房餐具", "desc": "花边波浪边圆形蛋糕模具布丁杯金属材质"},
  {"id": 25056, "category": "厨房餐具", "desc": "硅胶冰棒模具雪糕模具4种马卡龙配色3连排"},
  {"id": 25057, "category": "厨房餐具", "desc": "硅胶蛋糕模具6连花型甜甜圈形品牌Berclan"},
  {"id": 25058, "category": "厨房餐具", "desc": "方形菊花边烤盘烘焙模具金属不粘涂层"},
  {"id": 25059, "category": "电器电子", "desc": "电位器旋钮调节旋钮黑色塑料配红色箭头指示"},
  {"id": 25060, "category": "收纳整理", "desc": "厨房餐具沥水篮收纳篮塑料材质带沥水孔和分类隔板"},
  {"id": 25061, "category": "收纳整理", "desc": "冰箱鸡蛋收纳盒透明塑料倾斜式设计配白色盖子"},
  {"id": 25062, "category": "厨房储物", "desc": "透明带锁扣方形储物罐四面黑色卡扣密封"},
  {"id": 25063, "category": "收纳整理", "desc": "衣物防尘罩防尘袋60x90cm深蓝和卡其两色"},
]

# batch-14 results
results14 = [
  {"id": 25064, "category": "收纳整理", "desc": "白色旅行洗漱包配透明视窗顶部拉链和侧面提手"},
  {"id": 25065, "category": "厨房储物", "desc": "黑色铁艺网格厨房储物篮带木质提手"},
  {"id": 25066, "category": "清洁用品", "desc": "厨房清洁用金属丝清洁球配清洁海绵"},
  {"id": 25067, "category": "清洁用品", "desc": "硅胶清洁手套蓝色和绿色表面带防滑颗粒"},
  {"id": 25068, "category": "卫浴用品", "desc": "壁挂式浴室置物架黑色金属框架配木色底板吸盘免打孔"},
  {"id": 25069, "category": "厨房储物", "desc": "黑色金属线网壁挂置物架带挂钩背板可挂墙收纳调料瓶罐"},
  {"id": 25070, "category": "餐饮用品", "desc": "椭圆形编织托盘餐篮天然海草纤维手工编织"},
  {"id": 25071, "category": "收纳整理", "desc": "五个不同尺寸麻绳编织收纳篮嵌套式设计天然黄麻绳"},
  {"id": 25072, "category": "卫浴用品", "desc": "金色免打孔壁挂挂钩透明背胶设计浴室瓷砖墙面安装"},
  {"id": 25073, "category": "卫浴用品", "desc": "透明吸盘式免打孔壁挂钩圆形设计配不锈钢挂杆"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results13 + results14:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-13 + batch-14: 成功更新 {updated}/{len(results13)+len(results14)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
