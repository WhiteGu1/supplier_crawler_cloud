import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-1 results
results = [
  {"id": 20362, "category": "厨房餐具", "desc": "竖纹玻璃水杯带竹木盖和玻璃吸管"},
  {"id": 20363, "category": "厨房餐具", "desc": "透明玻璃杯带粉色手柄、竹木盖和玻璃吸管"},
  {"id": 20364, "category": "厨房餐具", "desc": "方形玻璃梅森杯带手柄、竹木盖和吸管"},
  {"id": 20365, "category": "厨房餐具", "desc": "竖纹花纹玻璃马克杯带金色边饰和手柄"},
  {"id": 20366, "category": "厨房餐具", "desc": "切割花纹水晶风格透明玻璃杯"},
  {"id": 20367, "category": "厨房餐具", "desc": "四只珍珠奶茶造型创意饮水杯套装"},
  {"id": 20368, "category": "厨房餐具", "desc": "花纹玻璃啤酒杯/扎杯带手柄"},
  {"id": 20369, "category": "厨房餐具", "desc": "四只镭射渐变塑料随行杯带穹顶盖和吸管"},
  {"id": 20370, "category": "厨房餐具", "desc": "无柄葡萄酒杯"},
  {"id": 20371, "category": "厨房餐具", "desc": "星巴克渐变菱格纹冷饮随行杯带吸管"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-1: 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
