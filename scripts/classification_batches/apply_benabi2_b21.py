import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-21 results (GLM-5.2)
results = [
  {"id": 25144, "category": "个人防护", "desc": "折叠雨伞套装四色便携防雨防晒"},
  {"id": 25145, "category": "宠物用品", "desc": "宠物狗床多尺寸蓝黑色爪印图案"},
  {"id": 25146, "category": "宠物用品", "desc": "长方形宠物狗床灰色绒面腊肠犬"},
  {"id": 25147, "category": "宠物用品", "desc": "灰色长方形宠物床柔软绒面围边"},
  {"id": 25148, "category": "宠物用品", "desc": "大号宠物狗床灰色双色中大型犬"},
  {"id": 25149, "category": "宠物用品", "desc": "宠物狗床三尺寸灰米双色爪印"},
  {"id": 25150, "category": "宠物用品", "desc": "宠物狗垫犬舍垫浅灰爪印三尺寸"},
  {"id": 25151, "category": "宠物用品", "desc": "宠物垫浅灰爪印围边金毛幼犬"},
  {"id": 25152, "category": "宠物用品", "desc": "猫立方宠物窝灰双色圆形入口脚凳"},
  {"id": 25153, "category": "宠物用品", "desc": "猫立方屋灰色双色多功能宠物家具"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-21: 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
