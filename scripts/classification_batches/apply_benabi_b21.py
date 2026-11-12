import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-21
  {"id": 17843, "category": "厨房餐具", "desc": "多功能厨房剪刀红色手柄"},
  {"id": 17844, "category": "厨房餐具", "desc": "厨房剪刀黑白色款"},
  {"id": 17845, "category": "厨房餐具", "desc": "6件套陶瓷刀具套装"},
  {"id": 17846, "category": "厨房餐具", "desc": "4件套厨房刀具套装"},
  {"id": 17847, "category": "厨房储物", "desc": "铜色玻璃罐胡椒研磨器"},
  {"id": 17848, "category": "厨房储物", "desc": "铜色金属胡椒研磨器"},
  {"id": 17849, "category": "厨房储物", "desc": "铜色金属胡椒研磨器高身"},
  {"id": 17850, "category": "厨房储物", "desc": "三件套玻璃调料罐套装木盖配木勺"},
  {"id": 17851, "category": "厨房储物", "desc": "金属厨房纸巾架带木底座"},
  {"id": 17852, "category": "婴幼儿用品", "desc": "三色卡通造型儿童水壶"},
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
