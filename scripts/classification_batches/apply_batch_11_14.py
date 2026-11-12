import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-11 和 batch-14 的结果
new_results = [
  # batch-11
  {"id": 2286, "category": "文具办公", "desc": "KK-402 电子计算器，办公学习用"},
  {"id": 2287, "category": "个人防护", "desc": "木质柄抛光刷，可用于鞋面/衣物护理"},
  {"id": 2288, "category": "鞋履护理", "desc": "El Mono 白色鞋带，蜡质绳鞋带"},
  {"id": 2289, "category": "鞋履护理", "desc": "El Mono 彩色鞋带（橙蓝黄绿混装）"},
  {"id": 2290, "category": "鞋履护理", "desc": "El Mono 棕色蜡质绳鞋带"},
  {"id": 2291, "category": "鞋履护理", "desc": "El Mono 黑色蜡质绳鞋带"},
  {"id": 2292, "category": "鞋履护理", "desc": "El Mono 白色蜡质绳鞋带"},
  {"id": 2293, "category": "鞋履护理", "desc": "El Mono 黑色蜡质绳鞋带"},
  {"id": 2294, "category": "鞋履护理", "desc": "El Mono 白色蜡质绳鞋带"},
  {"id": 2295, "category": "鞋履护理", "desc": "El Mono 棕色蜡质绳鞋带"},
  # batch-14
  {"id": 2316, "category": "运动户外", "desc": "APOLO 5.5mm气枪铅弹(0.84g)"},
  {"id": 2317, "category": "运动户外", "desc": "Bestway充气气垫床带脚泵"},
  {"id": 2318, "category": "运动户外", "desc": "Bestway单人气垫床"},
  {"id": 2319, "category": "运动户外", "desc": "Bestway手动充气泵(Air Hammer)"},
  {"id": 2320, "category": "派对用品", "desc": "柠檬粉/糖果粉派对用小罐装"},
  {"id": 2321, "category": "玩具游戏", "desc": "GENERALA家庭骰子游戏套装"},
  {"id": 2322, "category": "派对用品", "desc": "蓝色派对气球装饰套装"},
  {"id": 2323, "category": "派对用品", "desc": "Casino 40张防水可洗塑料餐巾"},
  {"id": 2324, "category": "派对用品", "desc": "Casino 50张防水可洗塑料餐巾"},
  {"id": 2325, "category": "玩具游戏", "desc": "Casino Numero Grande大号扑克牌"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

updated = 0
for r in new_results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount

conn.commit()
print(f"成功更新 {updated}/{len(new_results)} 条商品分类")
conn.close()
