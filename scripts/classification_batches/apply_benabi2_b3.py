import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-3
  {"id": 20382, "category": "厨房炊具", "desc": "爪印造型冰棒硅胶模具"},
  {"id": 20383, "category": "厨房餐具", "desc": "保温壶真空咖啡壶木手柄"},
  {"id": 20384, "category": "清洁用品", "desc": "三色卡通动物脚踏垃圾桶"},
  {"id": 20385, "category": "厨房餐具", "desc": "黑色铁艺网状水果篮"},
  {"id": 20386, "category": "厨房储物", "desc": "白色金属线厨房置物架"},
  {"id": 20387, "category": "收纳整理", "desc": "透明亚克力三层阶梯式收纳架"},
  {"id": 20388, "category": "厨房储物", "desc": "三件套透明玻璃保鲜盒"},
  {"id": 20389, "category": "收纳整理", "desc": "灰色无纺布三层悬挂式收纳袋"},
  {"id": 20390, "category": "收纳整理", "desc": "可折叠金属晾衣架"},
  {"id": 20391, "category": "收纳整理", "desc": "三件套麻绳编织收纳篮"},
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
