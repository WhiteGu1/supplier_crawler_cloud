import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-24
  {"id": 17873, "category": "日用百货", "desc": "家用立式熨衣板"},
  {"id": 17874, "category": "日用百货", "desc": "家用立式熨衣板"},
  {"id": 17875, "category": "日用百货", "desc": "家用立式熨衣板"},
  {"id": 17876, "category": "收纳整理", "desc": "金属网状储物篮带木质提手"},
  {"id": 17877, "category": "厨房储物", "desc": "铁艺厨房收纳提篮"},
  {"id": 17878, "category": "收纳整理", "desc": "布艺折叠储物筐带提手"},
  {"id": 17879, "category": "清洁用品", "desc": "玻璃瓶身长柄清洁刷"},
  {"id": 17880, "category": "收纳整理", "desc": "三层带轮移动置物推车"},
  {"id": 17881, "category": "厨房储物", "desc": "草编藤编方形托盘"},
  {"id": 17882, "category": "收纳整理", "desc": "SURME强力无痕粘钩"},
  # batch-25
  {"id": 17883, "category": "收纳整理", "desc": "浴室挂墙式金属置物架"},
  {"id": 17884, "category": "装饰品", "desc": "黑白圆形壁挂挂钟"},
  {"id": 17885, "category": "卫浴用品", "desc": "防滑地垫BIENVENIDO字样"},
  {"id": 17886, "category": "装饰品", "desc": "黑白几何图案方形抱枕"},
  {"id": 17887, "category": "装饰品", "desc": "红色立体格纹方形抱枕"},
  {"id": 17888, "category": "装饰品", "desc": "餐椅坐垫多色绗缝软垫"},
  {"id": 17889, "category": "装饰品", "desc": "渐变闪粉立体相框摆件套装"},
  {"id": 17890, "category": "装饰品", "desc": "织带蝴蝶结礼盒摆件"},
  {"id": 17891, "category": "收纳整理", "desc": "印花手提收纳箱"},
  {"id": 17892, "category": "收纳整理", "desc": "花卉印花手提收纳箱"},
  # batch-26
  {"id": 17893, "category": "厨房餐具", "desc": "软木餐垫套装"},
  {"id": 17894, "category": "装饰品", "desc": "大型仿真龟背竹绿植盆栽"},
  {"id": 17895, "category": "装饰品", "desc": "仿真小盆栽三件套"},
  {"id": 17896, "category": "装饰品", "desc": "仿真多肉植物组合盆栽"},
  {"id": 17897, "category": "装饰品", "desc": "四格黑色相框墙装饰画"},
  {"id": 17898, "category": "装饰品", "desc": "四格木色相框墙装饰画"},
  {"id": 17899, "category": "装饰品", "desc": "五格黑色相框墙装饰画"},
  {"id": 17900, "category": "装饰品", "desc": "四格白色相框墙装饰画"},
  {"id": 17901, "category": "装饰品", "desc": "圆形金属边几小茶几"},
  {"id": 17902, "category": "收纳整理", "desc": "圆形边几带布艺收纳篮"},
  # batch-27
  {"id": 17903, "category": "卫浴用品", "desc": "Benabi浴室防滑地垫"},
  {"id": 17904, "category": "卫浴用品", "desc": "菱形纹理浴室地垫"},
  {"id": 17905, "category": "卫浴用品", "desc": "浴室地垫使用场景展示"},
  {"id": 17906, "category": "卫浴用品", "desc": "浴室地垫使用场景展示"},
  {"id": 17907, "category": "卫浴用品", "desc": "透明吸盘式SPA浴室防滑沐浴垫"},
  {"id": 17908, "category": "卫浴用品", "desc": "PEVA防水防霉浴帘"},
  {"id": 17909, "category": "卫浴用品", "desc": "PEVA防水浴帘衬里"},
  {"id": 17910, "category": "卫浴用品", "desc": "玻璃喷壶浇花壶"},
  {"id": 17911, "category": "厨房餐具", "desc": "金属不锈钢咖啡搅拌勺套装"},
  {"id": 17912, "category": "卫浴用品", "desc": "水晶钻石装饰浴室窗帘挂钩"},
  # batch-28
  {"id": 17913, "category": "卫浴用品", "desc": "银色金属球链窗帘环浴帘挂钩"},
  {"id": 17914, "category": "卫浴用品", "desc": "大理石纹防水浴帘"},
  {"id": 17915, "category": "美妆个护", "desc": "4色装毛发梳气垫按摩梳"},
  {"id": 17916, "category": "文具办公", "desc": "6支装彩色铅笔"},
  {"id": 17917, "category": "文具办公", "desc": "12支装马卡龙色铅笔"},
  {"id": 17918, "category": "文具办公", "desc": "12支装粗头彩色铅笔"},
  {"id": 17919, "category": "文具办公", "desc": "卡通造型铅笔套装"},
  {"id": 17920, "category": "文具办公", "desc": "带卷笔刀功能自动铅笔"},
  {"id": 17921, "category": "文具办公", "desc": "BAIKU自动铅笔展示盒"},
  {"id": 17922, "category": "文具办公", "desc": "Cat Baby卡通猫造型圆珠笔"},
  # batch-29
  {"id": 17923, "category": "文具办公", "desc": "粉彩甜心果汁笔12支装"},
  {"id": 17924, "category": "文具办公", "desc": "卡通动物造型帽彩色圆珠笔"},
  {"id": 17925, "category": "文具办公", "desc": "六色软头纤维笔20支装"},
  {"id": 17926, "category": "文具办公", "desc": "12色彩色马克笔"},
  {"id": 17927, "category": "文具办公", "desc": "12色丙烯马克笔提盒装"},
  {"id": 17928, "category": "文具办公", "desc": "6支装滚轮印章笔"},
  {"id": 17929, "category": "文具办公", "desc": "12支双头丙烯马克笔"},
  {"id": 17930, "category": "文具办公", "desc": "24支双头丙烯马克笔"},
  {"id": 17931, "category": "文具办公", "desc": "36支双头丙烯马克笔"},
  {"id": 17932, "category": "文具办公", "desc": "60支双头丙烯马克笔"},
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
