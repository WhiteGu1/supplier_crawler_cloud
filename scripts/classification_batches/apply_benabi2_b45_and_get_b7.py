import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-4 (fixed duplicates)
  {"id": 20392, "category": "收纳整理", "desc": "三件套草编手提收纳篮"},
  {"id": 20393, "category": "卫浴用品", "desc": "白色铁艺网格浴室收纳篮"},
  {"id": 20394, "category": "卫浴用品", "desc": "多层马桶上方置物架"},
  {"id": 20395, "category": "卫浴用品", "desc": "黑色铁艺浴室伸缩置物架"},
  {"id": 20396, "category": "卫浴用品", "desc": "吸盘式浴室挂墙置物架"},
  {"id": 20397, "category": "厨房储物", "desc": "三组塑料分隔保鲜饭盒"},
  {"id": 20398, "category": "收纳整理", "desc": "透明塑料储物箱带彩色卡扣盖"},
  {"id": 20399, "category": "装饰品", "desc": "圆形石英挂钟黑白配色"},
  {"id": 20400, "category": "装饰品", "desc": "圆形石英挂钟黑白配色"},
  {"id": 20401, "category": "装饰品", "desc": "圆形石英挂钟黑白配色"},
  # benabi2-batch-5 (fixed duplicates)
  {"id": 20402, "category": "装饰品", "desc": "石英挂钟黑白两色"},
  {"id": 20403, "category": "装饰品", "desc": "石英挂钟黑白两色"},
  {"id": 20404, "category": "装饰品", "desc": "长方形流苏地垫吸水地毯"},
  {"id": 20405, "category": "装饰品", "desc": "三色爪印图案小型地垫"},
  {"id": 20406, "category": "装饰品", "desc": "几何图案长方形地垫"},
  {"id": 20407, "category": "装饰品", "desc": "菱形图案床边地垫配拖鞋"},
  {"id": 20408, "category": "装饰品", "desc": "多款带流苏图案地毯"},
  {"id": 20409, "category": "装饰品", "desc": "三款深色印花入户门垫"},
  {"id": 20410, "category": "装饰品", "desc": "圆形黄麻编织地毯"},
  {"id": 20411, "category": "派对用品", "desc": "三只礼盒配玫瑰金丝带"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"成功更新 {updated}/{len(results)} 条")

# 获取下一批次路径 (batch-7, 即第70~79条)
cur.execute("""
    SELECT id, image_local, name
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='') 
      AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
    LIMIT 10 OFFSET 70
""")
rows = cur.fetchall()
print(f"\nbatch-7 共 {len(rows)} 条:")
for pid, img, name in rows:
    print(f"  ID={pid} img=D:/projects/supplier_crawler/{img}")

conn.close()
