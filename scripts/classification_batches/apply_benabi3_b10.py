import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-10 results
results = [
  {"id": 25024, "category": "餐饮用品", "desc": "米白色亚麻棉麻餐桌布北欧简约风格"},
  {"id": 25025, "category": "餐饮用品", "desc": "Bermuda Textiles长方形餐桌布聚酯纤维140x180cm"},
  {"id": 25026, "category": "餐饮用品", "desc": "Especial Textiles长方形餐桌布100%聚酯纤维140x180cm"},
  {"id": 25027, "category": "餐饮用品", "desc": "Benalis Textiles长方形餐桌布140x180cm三色"},
  {"id": 25028, "category": "餐饮用品", "desc": "Bennabi Textiles长方形桌布100%涤纶140x180cm四色"},
  {"id": 25029, "category": "餐饮用品", "desc": "Textiles品牌长方形桌布100%聚酯纤维140x180cm四色"},
  {"id": 25030, "category": "餐饮用品", "desc": "Benobi Textiles矩形桌布三件套140x180cm"},
  {"id": 25031, "category": "餐饮用品", "desc": "Benobi Textiles长方形餐桌布100%聚酯纤维140x180cm三色"},
  {"id": 25032, "category": "餐饮用品", "desc": "Naonao品牌桌布140x220cm北欧风格抽象几何图案"},
  {"id": 25033, "category": "餐饮用品", "desc": "儿童青蛙造型分隔餐盘三格分区竹纤维密胺材质"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-10: 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
