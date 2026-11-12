import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-22
  {"id": 2396, "category": "玩具游戏", "desc": "粉色实心橡胶球/弹力球"},
  {"id": 2397, "category": "玩具游戏", "desc": "红白条纹橡胶球/弹力玩具球"},
  {"id": 2398, "category": "玩具游戏", "desc": "红白条纹橡胶球/弹力玩具球"},
  {"id": 2399, "category": "玩具游戏", "desc": "红白箭头条纹橡胶弹力球"},
  {"id": 2400, "category": "玩具游戏", "desc": "红白斑纹橡胶弹力球"},
  {"id": 2401, "category": "玩具游戏", "desc": "红白条橡胶弹力球"},
  {"id": 2402, "category": "清洁用品", "desc": "彩色塑料扫帚套装(扫帚+簸箕)"},
  {"id": 2403, "category": "运动户外", "desc": "彩色网状球拍(附球,沙滩/休闲玩具)"},
  {"id": 2404, "category": "运动户外", "desc": "彩色塑料呼啦圈"},
  {"id": 2405, "category": "运动户外", "desc": "彩色塑料呼啦圈(多色套装)"},
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
