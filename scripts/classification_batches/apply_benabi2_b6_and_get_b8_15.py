import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-6
  {"id": 20412, "category": "派对用品", "desc": "黑色烫金边礼盒套装配蝴蝶结"},
  {"id": 20413, "category": "派对用品", "desc": "多色方形礼品盒配蝴蝶结"},
  {"id": 20414, "category": "派对用品", "desc": "红粉色爱心图案礼盒堆叠"},
  {"id": 20415, "category": "厨房餐具", "desc": "圆形编织草编餐垫杯垫"},
  {"id": 20416, "category": "厨房餐具", "desc": "圆形流苏边编织餐垫"},
  {"id": 20417, "category": "厨房餐具", "desc": "圆形厨房主题印花餐垫"},
  {"id": 20418, "category": "装饰品", "desc": "仿真绿叶球形盆栽摆件"},
  {"id": 20419, "category": "装饰品", "desc": "仿真苏铁盆栽摆件"},
  {"id": 20420, "category": "日用百货", "desc": "圆形电子体重秤钢化玻璃面"},
  {"id": 20421, "category": "卫浴用品", "desc": "涤纶浴帘套装含挂钩"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"成功更新 {updated}/{len(results)} 条")

# 获取 batch-8~15 路径 (offset 80, limit 80)
cur.execute("""
    SELECT id, image_local, name
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='') 
      AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
    LIMIT 80 OFFSET 80
""")
rows = cur.fetchall()
print(f"\nbatch-8~15 共 {len(rows)} 条:")
for i, (pid, img, name) in enumerate(rows):
    print(f"  {i}: ID={pid} img=D:/projects/supplier_crawler/{img}")

conn.close()
