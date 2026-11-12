import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-18 (GLM-5.2)
  {"id": 25094, "category": "装饰品", "desc": "人造薰衣草盆栽白色花盆"},
  {"id": 25095, "category": "装饰品", "desc": "人造黄杨木球形绿植"},
  {"id": 25096, "category": "装饰品", "desc": "人造斑叶盆栽绿白叶片"},
  {"id": 25097, "category": "装饰品", "desc": "人造薰衣草配蕨类盆栽六角花盆"},
  {"id": 25098, "category": "装饰品", "desc": "人造白色绣球花盆栽"},
  {"id": 25099, "category": "装饰品", "desc": "大型人造热带植物象耳叶"},
  {"id": 25100, "category": "装饰品", "desc": "人造蕨类植物盆栽一对"},
  {"id": 25101, "category": "装饰品", "desc": "人造龙舌兰芦荟风格植物"},
  {"id": 25102, "category": "装饰品", "desc": "装饰性透明玻璃碗气泡纹理"},
  {"id": 25103, "category": "其他", "desc": "白色金属框架边桌置物桌"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"成功更新 {updated}/{len(results)} 条")

# 剩余有图未分类
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
