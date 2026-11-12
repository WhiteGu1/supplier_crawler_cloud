import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-7 results
results = [
  {"id": 24994, "category": "餐饮用品", "desc": "透明玻璃水壶冷水壶带把手和竖纹纹理"},
  {"id": 24995, "category": "厨房餐具", "desc": "带木质盖子的透明玻璃水壶简约现代"},
  {"id": 24996, "category": "厨房餐具", "desc": "硅胶大冰格制冰模具带分隔双格设计搭配冰夹"},
  {"id": 24997, "category": "厨房餐具", "desc": "带竹盖透明玻璃水壶配同款小玻璃杯竖纹玻璃工艺"},
  {"id": 24998, "category": "餐饮用品", "desc": "透明玻璃凉水壶带白色塑料手柄和盖子竖条纹理"},
  {"id": 24999, "category": "厨房餐具", "desc": "三只保温壶真空暖壶金属外壳配木质手柄"},
  {"id": 25000, "category": "厨房储物", "desc": "带竹盖和配套竹勺的透明玻璃密封罐"},
  {"id": 25001, "category": "厨房餐具", "desc": "带不锈钢盖的菱格纹玻璃水壶钻石切割纹理"},
  {"id": 25002, "category": "餐饮用品", "desc": "带木盖透明玻璃水壶搭配玻璃饮用杯"},
  {"id": 25003, "category": "厨房餐具", "desc": "烟灰色几何多面体无柄玻璃水杯威士忌杯五只装"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-7: 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
