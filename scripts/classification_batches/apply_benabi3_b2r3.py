import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-2-retry3 results
results = [
  {"id": 20372, "category": "餐饮用品", "desc": "带盖带吸管塑料随行杯6个装黑紫粉三色"},
  {"id": 20373, "category": "餐饮用品", "desc": "双层玻璃杯圆鼓形杯身隔热防烫"},
  {"id": 20374, "category": "餐饮用品", "desc": "透明双层玻璃杯圆润椭圆形隔热防烫"},
  {"id": 20375, "category": "餐饮用品", "desc": "琥珀色竖条纹高脚玻璃杯复古艺术风格"},
  {"id": 20376, "category": "餐饮用品", "desc": "透明高脚红酒杯郁金香形杯身"},
  {"id": 20377, "category": "餐饮用品", "desc": "深烟灰色锤纹带盖吸管杯配玻璃吸管"},
  {"id": 20378, "category": "餐饮用品", "desc": "方格纹金边威士忌杯套装配玻璃酒瓶"},
  {"id": 20379, "category": "餐饮用品", "desc": "带吸管和手柄保温吸管杯4色装配硅胶防滑套"},
  {"id": 20380, "category": "餐饮用品", "desc": "透明玻璃水杯威士忌杯竖条棱纹底部刻花"},
  {"id": 20381, "category": "厨房炊具", "desc": "波浪花环形蛋糕模具咕咕霍夫模具不粘涂层"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-2-retry3: 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
