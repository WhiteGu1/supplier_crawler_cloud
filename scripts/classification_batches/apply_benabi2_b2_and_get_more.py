import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-2
  {"id": 20342, "category": "厨房餐具", "desc": "透明高脚红酒杯"},
  {"id": 20343, "category": "厨房餐具", "desc": "玻璃咖啡杯带把手"},
  {"id": 20344, "category": "餐饮用品", "desc": "塑料便当盒多色内置餐具"},
  {"id": 20345, "category": "餐饮用品", "desc": "多格分格便当盒带卡扣"},
  {"id": 20346, "category": "餐饮用品", "desc": "保温便当包午餐袋"},
  {"id": 20347, "category": "婴幼儿用品", "desc": "儿童卡通便当盒恐龙造型"},
  {"id": 20348, "category": "厨房餐具", "desc": "蓝色纹理玻璃吸管杯"},
  {"id": 20349, "category": "餐饮用品", "desc": "提花餐桌布"},
  {"id": 20350, "category": "餐饮用品", "desc": "白色提花餐桌布"},
  {"id": 20351, "category": "厨房储物", "desc": "玻璃保鲜便当盒带盖"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"成功更新 {updated}/{len(results)} 条")

# 获取下一批次的正确路径 (batch-3 ~ batch-7, 即第30~79条)
cur.execute("""
    SELECT id, image_local, name
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='') 
      AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
    LIMIT 50 OFFSET 30
""")
rows = cur.fetchall()
print(f"\n下一批次(batch-3~7)共 {len(rows)} 条:")
for i, (pid, img, name) in enumerate(rows):
    print(f"  {i}: ID={pid} img=D:/projects/supplier_crawler/{img}")

conn.close()
