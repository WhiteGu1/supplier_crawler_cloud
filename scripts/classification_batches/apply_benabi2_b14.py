import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-14
  {"id": 24974, "category": "婴幼儿用品", "desc": "儿童卡通水杯带背带"},
  {"id": 24975, "category": "运动户外", "desc": "渐变色运动水杯500ml"},
  {"id": 24976, "category": "餐饮用品", "desc": "磨砂玻璃水瓶配不锈钢盖"},
  {"id": 24977, "category": "运动户外", "desc": "塑料运动水杯一键弹盖"},
  {"id": 24978, "category": "运动户外", "desc": "大容量运动水瓶带提手"},
  {"id": 24979, "category": "运动户外", "desc": "渐变运动水杯弹盖带提手"},
  {"id": 24980, "category": "厨房储物", "desc": "透明玻璃储物罐带盖竖条纹"},
  {"id": 24981, "category": "装饰品", "desc": "浮雕花纹玻璃装饰罐带宝珠顶盖"},
  {"id": 24982, "category": "厨房餐具", "desc": "虹彩玻璃碗螺旋纹理"},
  {"id": 24983, "category": "厨房炊具", "desc": "7件套不锈钢刀具套装带刀座"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"成功更新 {updated}/{len(results)} 条")

# 查看剩余未分类数量
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='')")
total_remaining = cur.fetchone()[0]
print(f"benabi 总剩余未分类: {total_remaining}")

conn.close()
