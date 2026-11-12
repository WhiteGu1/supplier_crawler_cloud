import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-1
  {"id": 17820, "category": "装饰品", "desc": "圆形壁挂装饰镜皮革挂带"},
  {"id": 17821, "category": "装饰品", "desc": "圆形壁挂装饰镜皮革挂带"},
  {"id": 17822, "category": "餐饮用品", "desc": "几何镂空餐垫隔热垫"},
  {"id": 20335, "category": "厨房餐具", "desc": "塑料制冰格八格连体"},
  {"id": 20336, "category": "厨房餐具", "desc": "透明玻璃水壶带把手配玻璃杯"},
  {"id": 20337, "category": "厨房餐具", "desc": "带金属盖玻璃凉水壶配玻璃杯"},
  {"id": 20338, "category": "厨房餐具", "desc": "菱形纹理玻璃果汁壶配玻璃杯"},
  {"id": 20339, "category": "厨房餐具", "desc": "不锈钢真空保温壶配木手柄"},
  {"id": 20340, "category": "厨房储物", "desc": "玻璃密封储物罐配竹盖和竹勺"},
  {"id": 20341, "category": "厨房餐具", "desc": "锤纹玻璃水壶带金属盖配玻璃杯"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"成功更新 {updated}/{len(results)} 条")
conn.close()
