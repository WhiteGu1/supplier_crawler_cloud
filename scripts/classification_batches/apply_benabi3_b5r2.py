import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-5-retry2 results
results = [
  {"id": 20442, "category": "收纳整理", "desc": "透明亚克力多层化妆品收纳盒带抽屉和分区置物架"},
  {"id": 20443, "category": "美妆个护", "desc": "黑色双层网纱化妆包带星形拉链吊坠和手提带"},
  {"id": 20444, "category": "收纳整理", "desc": "多功能桌面分格收纳盒马卡龙色系带小抽屉和隔板"},
  {"id": 20445, "category": "美妆个护", "desc": "梳妆台场景含圆形化妆镜收纳盒化妆刷及各类化妆品"},
  {"id": 20446, "category": "文具办公", "desc": "Benabi机器人主题可擦笔自动铅笔盒装多色"},
  {"id": 20447, "category": "文具办公", "desc": "猫咪日记系列卡通动物造型圆珠笔10色套装36支盒装"},
  {"id": 20448, "category": "文具办公", "desc": "儿童印章水彩笔套装12色透明便携盒装"},
  {"id": 20449, "category": "文具办公", "desc": "Benabi双头马克笔12支装透明塑料盒带黄色提手"},
  {"id": 20450, "category": "文具办公", "desc": "三角楔形橡皮擦白色专业美术绘图用"},
  {"id": 20451, "category": "文具办公", "desc": "3D乌龟造型橡皮擦4色12个装可爱卡通立体造型"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-5-retry2: 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
