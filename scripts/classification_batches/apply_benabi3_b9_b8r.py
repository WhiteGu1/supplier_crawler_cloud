import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-9 results
results9 = [
  {"id": 25014, "category": "厨房储物", "desc": "罗纹玻璃储物罐三件套带软木球盖"},
  {"id": 25015, "category": "美妆个护", "desc": "便携式迷你加湿器面部喷雾器灰色半透明"},
  {"id": 25016, "category": "厨房餐具", "desc": "黑色金属线框沥水架带木质手柄和接水盘"},
  {"id": 25017, "category": "厨房餐具", "desc": "三层黑色金属沥水架带盘架杯架刀叉筒及接水盘"},
  {"id": 25018, "category": "厨房餐具", "desc": "双层黑色金属沥水架带刀叉筒和接水盘"},
  {"id": 25019, "category": "厨房餐具", "desc": "不锈钢线框沥水架带木质手柄黑色接水盘和刀叉筒"},
  {"id": 25020, "category": "厨房炊具", "desc": "黑色金属线框拱形面包架可放置烤炉上方"},
  {"id": 25021, "category": "餐饮用品", "desc": "白色亚麻桌布自然纹理"},
  {"id": 25022, "category": "餐饮用品", "desc": "白色亚麻桌布矩形自然垂坠"},
  {"id": 25023, "category": "餐饮用品", "desc": "米色亚麻桌布自然褶皱质感"},
]

# batch-8-retry results
results8 = [
  {"id": 25004, "category": "厨房餐具", "desc": "水晶玻璃杯套装6只钻石切割菱形纹理"},
  {"id": 25005, "category": "厨房储物", "desc": "便携式保温餐具组合三层叠放保鲜便当盒和随身保温杯"},
  {"id": 25006, "category": "厨房储物", "desc": "三件套分隔便当盒带透明上盖和卡扣密封"},
  {"id": 25007, "category": "厨房储物", "desc": "三格分格便当盒套装紫粉绿三色"},
  {"id": 25008, "category": "厨房储物", "desc": "粉红色方形便当盒1000ml带透明盖分隔板及配套叉勺"},
  {"id": 25009, "category": "箱包配件", "desc": "三款小型斜挎包邮差包灰藏青黑三色"},
  {"id": 25010, "category": "厨房餐具", "desc": "带把手高硼硅玻璃马克杯琥珀色和虹彩色"},
  {"id": 25011, "category": "餐饮用品", "desc": "透明玻璃啤酒杯高脚带柄造型"},
  {"id": 25012, "category": "厨房餐具", "desc": "透明玻璃沙拉碗宽口圆底配木制沙拉叉"},
  {"id": 25013, "category": "厨房储物", "desc": "水晶切割花纹玻璃糖罐圆筒形带盖及小勺"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

updated = 0
for r in results9 + results8:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-9 + batch-8-retry: 成功更新 {updated}/{len(results9)+len(results8)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
