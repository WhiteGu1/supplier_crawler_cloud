import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-6 results
results = [
  {"id": 24909, "category": "厨房餐具", "desc": "不锈钢面团刮刀3件套带彩色硅胶手柄和刻度"},
  {"id": 24910, "category": "厨房储物", "desc": "带棱纹玻璃罐配木质盖子用于储存干货"},
  {"id": 24911, "category": "厨房储物", "desc": "带棱纹玻璃罐配木质盖子用于储存干货"},
  {"id": 24912, "category": "厨房储物", "desc": "带棱纹玻璃罐配木质盖子用于储存干货"},
  {"id": 24913, "category": "厨房餐具", "desc": "装饰性压花玻璃杯用于饮用饮料"},
  {"id": 24914, "category": "文具办公", "desc": "黑色金属丝网桌面文件收纳架双格文件分类"},
  {"id": 24915, "category": "装饰品", "desc": "金属螺旋翻页照片便签展示架配椭圆形木质底座"},
  {"id": 24916, "category": "厨房储物", "desc": "厨房水槽收纳架木质底座配金属丝框架"},
  {"id": 24917, "category": "厨房餐具", "desc": "烟棕色棱纹玻璃高脚杯"},
  {"id": 24918, "category": "厨房炊具", "desc": "可重复使用硅胶裱花袋套装配不锈钢裱花嘴"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-6: 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

# 获取剩余所有有图未分类的ID和路径，用于后续分批
cur.execute("""
    SELECT id, image_local
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='') 
      AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
""")
rows = cur.fetchall()
print(f"\n剩余 {len(rows)} 条:")
for i, (pid, img) in enumerate(rows):
    print(f"  {i}: ID={pid} img=D:/projects/supplier_crawler/{img}")

conn.close()
