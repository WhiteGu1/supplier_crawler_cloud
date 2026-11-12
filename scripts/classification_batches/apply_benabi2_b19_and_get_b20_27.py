import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-19 (GLM-5.2)
  {"id": 25104, "category": "照明灯具", "desc": "现代简约台灯玫瑰金金属质感"},
  {"id": 25105, "category": "清洁用品", "desc": "超细纤维清洁布抹布四条装"},
  {"id": 25106, "category": "卫浴用品", "desc": "星形图案毛巾多色四条装"},
  {"id": 25107, "category": "卫浴用品", "desc": "透明PVC椭圆形防滑沐浴垫"},
  {"id": 25108, "category": "卫浴用品", "desc": "淡蓝色透明椭圆形防滑浴缸垫"},
  {"id": 25109, "category": "卫浴用品", "desc": "恒洁品牌淋浴浴帘蓝色海洋鱼类"},
  {"id": 25110, "category": "卫浴用品", "desc": "灰色烟熏玻璃按压式皂液器"},
  {"id": 25111, "category": "卫浴用品", "desc": "米色卫浴用品套装五件套"},
  {"id": 25112, "category": "卫浴用品", "desc": "仿石纹理卫浴配件套装"},
  {"id": 25113, "category": "卫浴用品", "desc": "透明亚克力卫浴用品套装"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"成功更新 {updated}/{len(results)} 条")

# 获取 batch-20~27 路径 (offset 170, limit 80)
cur.execute("""
    SELECT id, image_local, name
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='') 
      AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
    LIMIT 80 OFFSET 170
""")
rows = cur.fetchall()
print(f"\nbatch-20~27 共 {len(rows)} 条:")
for i, (pid, img, name) in enumerate(rows):
    print(f"  {i}: ID={pid} img=D:/projects/supplier_crawler/{img}")

# 剩余有图未分类
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"\nbenabi 剩余有图未分类: {remaining}")

conn.close()
