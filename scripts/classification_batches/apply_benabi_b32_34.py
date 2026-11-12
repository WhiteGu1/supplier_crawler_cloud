import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-32
  {"id": 17953, "category": "文具办公", "desc": "恐龙造型橡皮擦4件套"},
  {"id": 17954, "category": "文具办公", "desc": "动物蛋糕造型橡皮擦"},
  {"id": 17955, "category": "文具办公", "desc": "太空主题橡皮擦"},
  {"id": 17956, "category": "文具办公", "desc": "机器人造型卷笔刀"},
  {"id": 17957, "category": "文具办公", "desc": "卡通汉堡造型橡皮擦"},
  {"id": 17958, "category": "文具办公", "desc": "猫爪造型滚轮橡皮擦"},
  {"id": 17959, "category": "文具办公", "desc": "二合一卷笔刀橡皮擦组合"},
  {"id": 17960, "category": "文具办公", "desc": "猫爪造型橡皮卷笔刀2合1"},
  {"id": 17961, "category": "文具办公", "desc": "独角兽造型橡皮卷笔刀2合1"},
  {"id": 17962, "category": "文具办公", "desc": "猫爪软糖造型推拉橡皮"},
  # batch-33
  {"id": 17963, "category": "文具办公", "desc": "彩色塑料柄不锈钢剪刀"},
  {"id": 17964, "category": "文具办公", "desc": "儿童安全塑料柄剪刀"},
  {"id": 17965, "category": "文具办公", "desc": "儿童塑料柄剪刀"},
  {"id": 17966, "category": "文具办公", "desc": "不锈钢剪刀多色塑料手柄"},
  {"id": 17967, "category": "文具办公", "desc": "塑料柄剪刀多色"},
  {"id": 17968, "category": "文具办公", "desc": "塑料柄剪刀多色"},
  {"id": 17969, "category": "文具办公", "desc": "塑料柄剪刀多色"},
  {"id": 17970, "category": "文具办公", "desc": "不锈钢儿童剪刀"},
  {"id": 17971, "category": "文具办公", "desc": "6支套装平头画笔"},
  {"id": 17972, "category": "文具办公", "desc": "彩色手动转笔刀套装"},
  # batch-34
  {"id": 17973, "category": "文具办公", "desc": "2合1橡皮卷笔刀恐龙主题"},
  {"id": 17974, "category": "文具办公", "desc": "2合1橡皮卷笔刀太空人主题"},
  {"id": 17975, "category": "文具办公", "desc": "2合1橡皮卷笔刀熊主题"},
  {"id": 17976, "category": "文具办公", "desc": "运动主题铅笔卷笔刀"},
  {"id": 17977, "category": "文具办公", "desc": "卡通主题文具套装"},
  {"id": 17978, "category": "文具办公", "desc": "恐龙主题铅笔橡皮套装"},
  {"id": 17979, "category": "文具办公", "desc": "独角兽主题铅笔橡皮套装"},
  {"id": 17980, "category": "文具办公", "desc": "透明塑料圆头小圆规"},
  {"id": 17981, "category": "美妆个护", "desc": "黑色塑料柄手持化妆镜"},
  {"id": 17982, "category": "美妆个护", "desc": "黑色塑料柄手持化妆镜"},
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
