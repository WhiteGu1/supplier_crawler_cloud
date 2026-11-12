import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-12 results
results = [
  {"id": 25044, "category": "厨房餐具", "desc": "青绿色手工玻璃杯竖条纹锤纹质感"},
  {"id": 25045, "category": "厨房餐具", "desc": "透明钻石纹雕花玻璃水杯"},
  {"id": 25046, "category": "厨房餐具", "desc": "菠萝纹塑料吸管杯带盖带吸管"},
  {"id": 25047, "category": "厨房餐具", "desc": "双层隔热玻璃杯圆润杯身"},
  {"id": 25048, "category": "厨房餐具", "desc": "双层玻璃杯高筒直身设计"},
  {"id": 25049, "category": "厨房餐具", "desc": "几何切面玻璃杯威士忌杯棱柱造型"},
  {"id": 25050, "category": "厨房餐具", "desc": "美人鱼鳞片双层不锈钢保温吸管杯"},
  {"id": 25051, "category": "厨房餐具", "desc": "双层玻璃杯盛装意式浓缩咖啡"},
  {"id": 25052, "category": "厨房炊具", "desc": "手动蔬菜脱水器沙拉甩干器"},
  {"id": 25053, "category": "餐饮用品", "desc": "方形竹木托盘早餐下午茶场景"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-12: 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
