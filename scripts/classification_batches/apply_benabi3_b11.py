import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-11 results
results = [
  {"id": 25034, "category": "厨房餐具", "desc": "透明玻璃马克杯方形玻璃把手简约现代"},
  {"id": 25035, "category": "厨房餐具", "desc": "G-HORSE品牌透明玻璃马克杯杯身切割花纹"},
  {"id": 25036, "category": "食品饮料", "desc": "柠檬蜂蜜茶饮品配柠檬片蜂蜜罐和玻璃茶杯"},
  {"id": 25037, "category": "厨房餐具", "desc": "白色陶瓷圆形餐盘宽边简约设计"},
  {"id": 25038, "category": "日用百货", "desc": "不锈钢保温瓶墨绿色和黑色两款可折叠手柄"},
  {"id": 25039, "category": "厨房餐具", "desc": "不锈钢保温随手杯蓝色和红色款带防滑手柄"},
  {"id": 25040, "category": "厨房餐具", "desc": "草莓造型创意吸管杯粉红色卡通设计配绿色吸管"},
  {"id": 25041, "category": "厨房餐具", "desc": "幻彩钻石纹塑料随行杯带盖带吸管4个装"},
  {"id": 25042, "category": "厨房餐具", "desc": "透明水晶玻璃水杯不规则树皮纹理手工吹制"},
  {"id": 25043, "category": "食品饮料", "desc": "蜂蜜柠檬茶饮品配柠檬片蜂蜜罐玻璃茶杯和白色茶壶"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-11: 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
