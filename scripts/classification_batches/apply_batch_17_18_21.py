import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-17
  {"id": 2346, "category": "日用百货", "desc": "白色双面胶带卷"},
  {"id": 2347, "category": "日用百货", "desc": "两卷透明/白色双面胶带"},
  {"id": 2348, "category": "日用百货", "desc": "单卷白色双面胶带"},
  {"id": 2349, "category": "日用百货", "desc": "Canse品牌双面胶带卷"},
  {"id": 2350, "category": "日用百货", "desc": "Can-FIX品牌牛皮纸包装胶带两卷"},
  {"id": 2351, "category": "日用百货", "desc": "Canse品牌透明双面胶带卷"},
  {"id": 2352, "category": "日用百货", "desc": "牛皮纸包装胶带卷，棕色"},
  {"id": 2353, "category": "日用百货", "desc": "Can-FIX FITA DE EMBALAR包装胶带卷"},
  {"id": 2354, "category": "日用百货", "desc": "Canse品牌透明封箱胶带卷"},
  {"id": 2355, "category": "日用百货", "desc": "牛皮纸/湿水牛皮胶带卷，棕色"},
  # batch-18 (注意：id 2358 重复了，只取一条)
  {"id": 2356, "category": "派对用品", "desc": "Fuegolandia彩色生日蜡烛套装"},
  {"id": 2357, "category": "派对用品", "desc": "Candela水气球100个装"},
  {"id": 2358, "category": "派对用品", "desc": "Candela彩色水气球派对套装"},
  {"id": 2359, "category": "派对用品", "desc": "Candela Play彩色派对气球"},
  {"id": 2360, "category": "派对用品", "desc": "Candela多色彩条喷雾"},
  {"id": 2361, "category": "派对用品", "desc": "Candela Tiki派对彩带喷雾三色装"},
  {"id": 2362, "category": "派对用品", "desc": "Magic Re-lighting螺旋蜡烛"},
  {"id": 2363, "category": "其他", "desc": "Martin Blust Gaucho Dorada民谣吉他弦"},
  {"id": 2364, "category": "其他", "desc": "Martin Blust Extra Light电吉他弦"},
  {"id": 2365, "category": "五金工具", "desc": "Curing Led快干/瞬间胶粘剂"},
  # batch-21
  {"id": 2386, "category": "五金工具", "desc": "LUXOM黑色塑料扎带200x3.6mm 100只装"},
  {"id": 2387, "category": "五金工具", "desc": "LUXOM黑色尼龙扎带/束线带"},
  {"id": 2388, "category": "五金工具", "desc": "LUXOM黑色塑料扎带/束线带散装"},
  {"id": 2389, "category": "五金工具", "desc": "LUXOM白色特氟龙生料带"},
  {"id": 2390, "category": "卫浴用品", "desc": "Candela自动感应皂液器"},
  {"id": 2391, "category": "玩具游戏", "desc": "Hot Wheels风火轮迷你合金小汽车"},
  {"id": 2392, "category": "玩具游戏", "desc": "彩色塑料沙锤乐器玩具"},
  {"id": 2393, "category": "玩具游戏", "desc": "彩色花纹弹力球/泡沫球"},
  {"id": 2394, "category": "宠物用品", "desc": "彩色磨牙弹力球宠物玩具"},
  {"id": 2395, "category": "玩具游戏", "desc": "粉色橡胶弹力球"},
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
