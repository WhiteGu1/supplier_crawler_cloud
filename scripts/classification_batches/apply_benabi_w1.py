import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-0
  {"id": 15247, "category": "厨房餐具", "desc": "不锈钢勺子套装6支装"},
  {"id": 15252, "category": "厨房餐具", "desc": "琥珀色浮雕玻璃水杯6只装"},
  {"id": 15253, "category": "厨房储物", "desc": "琥珀色玻璃带盖储物罐"},
  {"id": 15254, "category": "厨房储物", "desc": "黑色旋转式玻璃调味瓶架"},
  {"id": 15255, "category": "派对用品", "desc": "6色小型丝带装饰礼品盒"},
  {"id": 15256, "category": "派对用品", "desc": "6色小型丝带装饰礼品盒"},
  {"id": 15257, "category": "卫浴用品", "desc": "不锈钢马桶刷带底座"},
  {"id": 15258, "category": "卫浴用品", "desc": "黑色哑光不锈钢马桶刷带底座"},
  {"id": 17273, "category": "厨房炊具", "desc": "黑色细网筛漏勺三件套"},
  {"id": 17274, "category": "厨房炊具", "desc": "黑色细网筛漏勺带长柄"},
  # batch-1
  {"id": 17275, "category": "餐饮用品", "desc": "不锈钢保温吸管杯三只装"},
  {"id": 17276, "category": "厨房炊具", "desc": "高硼硅玻璃法压壶带木盖"},
  {"id": 17277, "category": "装饰品", "desc": "绿色龙血树观叶盆栽"},
  {"id": 17278, "category": "厨房炊具", "desc": "不锈钢水果削皮刀粉色手柄"},
  {"id": 17279, "category": "厨房炊具", "desc": "六色硅胶烧烤烘焙刷"},
  {"id": 17280, "category": "厨房炊具", "desc": "硅胶条纹防滑隔热烤箱手套"},
  {"id": 17281, "category": "厨房炊具", "desc": "纯色布艺隔热手套配隔热垫"},
  {"id": 17282, "category": "厨房炊具", "desc": "格纹硅胶防滑隔热烤箱手套"},
  {"id": 17283, "category": "厨房炊具", "desc": "棉麻绗缝隔热手套配隔热垫"},
  {"id": 17284, "category": "厨房餐具", "desc": "24件不锈钢餐具套装"},
  # batch-2
  {"id": 17285, "category": "厨房餐具", "desc": "硅胶冰格制冰器带储冰桶"},
  {"id": 17286, "category": "餐饮用品", "desc": "玻璃水瓶/冷水壶配软木塞"},
  {"id": 17287, "category": "厨房餐具", "desc": "雕花印花玻璃水杯"},
  {"id": 17288, "category": "厨房餐具", "desc": "不锈钢分隔便当盒"},
  {"id": 17289, "category": "厨房餐具", "desc": "不锈钢分隔便当盒"},
  {"id": 17290, "category": "厨房餐具", "desc": "不锈钢分隔便当盒"},
  {"id": 17291, "category": "厨房储物", "desc": "不锈钢食物保鲜盒配塑料盖"},
  {"id": 17292, "category": "厨房储物", "desc": "不锈钢食物保鲜盒配塑料盖"},
  {"id": 17293, "category": "厨房储物", "desc": "不锈钢食物保鲜盒配塑料盖"},
  {"id": 17294, "category": "厨房储物", "desc": "不锈钢食物保鲜盒配塑料盖"},
  # batch-3
  {"id": 17295, "category": "厨房餐具", "desc": "不锈钢长方形保温饭盒"},
  {"id": 17296, "category": "厨房餐具", "desc": "儿童卡通分格不锈钢便当盒"},
  {"id": 17297, "category": "厨房餐具", "desc": "三件套卡通动物图案塑料便当盒"},
  {"id": 17298, "category": "厨房餐具", "desc": "不锈钢沥水保鲜盒配硅胶密封盖"},
  {"id": 17299, "category": "厨房餐具", "desc": "卡通太空主题塑料分隔便当盒"},
  {"id": 17300, "category": "厨房餐具", "desc": "不锈钢保鲜盒配透明盖及日期旋钮"},
  {"id": 17301, "category": "厨房餐具", "desc": "双层耐热玻璃咖啡杯/茶杯"},
  {"id": 17302, "category": "厨房餐具", "desc": "玻璃水壶带木塞GOOD MORNING印花"},
  {"id": 17303, "category": "厨房储物", "desc": "黑色铁艺配木底厨房纸巾立式收纳架"},
  {"id": 17304, "category": "厨房储物", "desc": "厨房卷纸立式收纳架"},
  # batch-4
  {"id": 17305, "category": "厨房储物", "desc": "黑色金属厨房纸巾架立式"},
  {"id": 17306, "category": "厨房储物", "desc": "黑色金属纸巾架配木底座"},
  {"id": 17307, "category": "厨房储物", "desc": "立式厨房纸巾架黑白两色"},
  {"id": 17308, "category": "运动户外", "desc": "户外保温水瓶双盖设计带提环"},
  {"id": 17309, "category": "运动户外", "desc": "户外保温水壶大容量不锈钢"},
  {"id": 17310, "category": "餐饮用品", "desc": "折叠硅胶咖啡杯便携随行杯"},
  {"id": 17311, "category": "厨房餐具", "desc": "玻璃法压壶带木盖"},
  {"id": 17312, "category": "厨房储物", "desc": "迷你桌面垃圾桶按压式翻盖"},
  {"id": 17313, "category": "厨房储物", "desc": "陶瓷厨房用具收纳罐配木底座"},
  {"id": 17314, "category": "宠物用品", "desc": "粘毛器除毛滚轮宠物毛发清理器"},
  # batch-5
  {"id": 17315, "category": "清洁用品", "desc": "卡通猫咪图案粘毛器滚筒式"},
  {"id": 17316, "category": "清洁用品", "desc": "动物印花粘毛器滚筒式"},
  {"id": 17317, "category": "厨房储物", "desc": "白色铁艺网格水果收纳篮带木质提手"},
  {"id": 17318, "category": "收纳整理", "desc": "三件套黄麻绳编织圆碗收纳筐"},
  {"id": 17319, "category": "收纳整理", "desc": "棉绳编织圆盘收纳篮三件套"},
  {"id": 17320, "category": "收纳整理", "desc": "棉绳编织圆盘收纳篮三件套"},
  {"id": 17321, "category": "收纳整理", "desc": "椭圆形草编藤编托盘带双把手"},
  {"id": 17322, "category": "厨房储物", "desc": "双耳编织麻绳水果面包收纳篮"},
  {"id": 17323, "category": "卫浴用品", "desc": "棉绳编织浴室收纳篮三件套"},
  {"id": 17324, "category": "卫浴用品", "desc": "棉绳编织浴室收纳篮三件套"},
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
