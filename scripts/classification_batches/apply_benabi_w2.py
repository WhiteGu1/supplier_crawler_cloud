import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-8
  {"id": 17345, "category": "厨房餐具", "desc": "棉麻编织圆形餐垫白色"},
  {"id": 17346, "category": "厨房餐具", "desc": "棉麻编织圆形餐垫黑色"},
  {"id": 17347, "category": "厨房餐具", "desc": "黑色圆形编织餐垫"},
  {"id": 17348, "category": "厨房餐具", "desc": "蕾丝花边圆形餐垫多色"},
  {"id": 17349, "category": "厨房餐具", "desc": "编织餐垫三件套"},
  {"id": 17350, "category": "厨房餐具", "desc": "圆形餐垫两件套"},
  {"id": 17351, "category": "厨房餐具", "desc": "圆形编织餐垫四件套"},
  {"id": 17352, "category": "厨房餐具", "desc": "流苏边圆形餐垫三件套"},
  {"id": 17353, "category": "装饰品", "desc": "仿真大型绿叶盆栽"},
  {"id": 17354, "category": "装饰品", "desc": "仿真小型球形绿植盆栽三件套"},
  # batch-9
  {"id": 17355, "category": "装饰品", "desc": "三盆仿真球形绿植盆栽"},
  {"id": 17356, "category": "装饰品", "desc": "大型仿真龙血树盆栽"},
  {"id": 17357, "category": "装饰品", "desc": "四件套麻绳编织花盆套装仿真绿植"},
  {"id": 17358, "category": "装饰品", "desc": "四件套三色编织花盆套装仿真绿植"},
  {"id": 17359, "category": "装饰品", "desc": "四件套双色编织花盆套装仿真绿植"},
  {"id": 17360, "category": "装饰品", "desc": "三联竖式悬挂相框组合白色"},
  {"id": 17361, "category": "装饰品", "desc": "四联组合挂墙相框水果主题"},
  {"id": 17362, "category": "装饰品", "desc": "七联组合挂墙相框复古摄影主题"},
  {"id": 17363, "category": "装饰品", "desc": "12只装DELUNE香薰蜡烛礼盒"},
  {"id": 17364, "category": "装饰品", "desc": "12只装香薰蜡烛礼盒"},
  # batch-10
  {"id": 17365, "category": "装饰品", "desc": "GUNA HOME香味蜡烛礼盒"},
  {"id": 17366, "category": "装饰品", "desc": "12件套DELUXE香味蜡烛礼盒"},
  {"id": 17367, "category": "装饰品", "desc": "12件套LOVE爱心图案香味蜡烛"},
  {"id": 17368, "category": "装饰品", "desc": "12件套LOVE/Home香味蜡烛礼盒"},
  {"id": 17369, "category": "装饰品", "desc": "12件装天然大豆蜡香味蜡烛"},
  {"id": 17370, "category": "装饰品", "desc": "12件套手工香味蜡烛粉色玻璃罐"},
  {"id": 17371, "category": "装饰品", "desc": "12件套手工梅森罐香味蜡烛"},
  {"id": 17372, "category": "装饰品", "desc": "Tili品牌25粒装茶蜡"},
  {"id": 17373, "category": "装饰品", "desc": "Delicate Aroma香味蜡烛三件套"},
  {"id": 17374, "category": "装饰品", "desc": "Citrus Zest柑橘香氛蜡烛"},
  # batch-11
  {"id": 17375, "category": "装饰品", "desc": "Juniper Collection香薰蜡烛"},
  {"id": 17376, "category": "装饰品", "desc": "磨砂纹理玻璃杯香薰蜡烛"},
  {"id": 17377, "category": "装饰品", "desc": "Aromatic Fragrance菱形纹理玻璃杯香薰蜡烛"},
  {"id": 17378, "category": "装饰品", "desc": "三色麻点纹理玻璃杯香薰蜡烛套装"},
  {"id": 17379, "category": "装饰品", "desc": "四色蕾丝纹理玻璃杯香薰蜡烛套装"},
  {"id": 17380, "category": "装饰品", "desc": "大豆蜡香薰蜡烛黑色礼盒装"},
  {"id": 17381, "category": "装饰品", "desc": "天然大豆蜡香薰蜡烛礼盒装"},
  {"id": 17382, "category": "装饰品", "desc": "天然大豆蜡香薰蜡烛礼盒装"},
  {"id": 17383, "category": "装饰品", "desc": "简约玻璃杯香薰蜡烛"},
  {"id": 17384, "category": "装饰品", "desc": "Deluxe香薰蜡烛礼盒套装"},
  # batch-12
  {"id": 17385, "category": "装饰品", "desc": "三色玻璃杯香薰蜡烛套装"},
  {"id": 17386, "category": "装饰品", "desc": "三件套玻璃杯香薰蜡烛"},
  {"id": 17387, "category": "装饰品", "desc": "四件装木盖彩色玻璃香薰蜡烛"},
  {"id": 17388, "category": "装饰品", "desc": "五色磨砂玻璃香薰蜡烛"},
  {"id": 17389, "category": "装饰品", "desc": "四款金盖透明玻璃香薰蜡烛"},
  {"id": 17390, "category": "装饰品", "desc": "四款方形彩盒香薰蜡烛"},
  {"id": 17391, "category": "装饰品", "desc": "多色包装香薰蜡烛礼盒装"},
  {"id": 17392, "category": "季节商品", "desc": "Autumn Spice秋季主题香薰蜡烛"},
  {"id": 17393, "category": "收纳整理", "desc": "透明PVC洗漱化妆包便携旅行收纳袋"},
  {"id": 17394, "category": "卫浴用品", "desc": "木质浴用品托盘套装"},
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
