import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-22 (GLM-5.2)
  {"id": 25154, "category": "宠物用品", "desc": "灰色圆顶猫窝带悬挂玩具"},
  {"id": 25155, "category": "宠物用品", "desc": "灰色圆顶猫窝半封闭设计"},
  {"id": 25156, "category": "宠物用品", "desc": "蓝色圆形宠物床爪印图案"},
  {"id": 25157, "category": "宠物用品", "desc": "蓝色圆形猫床爪印图案"},
  {"id": 25158, "category": "宠物用品", "desc": "蓝色圆形宠物床爪印图案"},
  {"id": 25159, "category": "宠物用品", "desc": "蓝色圆形宠物床爪印图案"},
  {"id": 25160, "category": "宠物用品", "desc": "蓝色圆形宠物床爪印图案"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-22: 成功更新 {updated}/{len(results)} 条")

# 剩余有图未分类
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
