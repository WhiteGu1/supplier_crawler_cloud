import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-38
  {"id": 20285, "category": "厨房炊具", "desc": "硅胶厨房工具套装"},
  {"id": 20286, "category": "厨房炊具", "desc": "木柄不锈钢披萨滚轮刀"},
  {"id": 20287, "category": "婴幼儿用品", "desc": "儿童卡通小鸡造型勺叉餐具"},
  {"id": 20288, "category": "婴幼儿用品", "desc": "儿童动物造型不锈钢叉勺餐具套装"},
  {"id": 20289, "category": "厨房餐具", "desc": "玻璃碗四件套礼盒装"},
  {"id": 20290, "category": "厨房储物", "desc": "三层玻璃调味罐带木盖"},
  {"id": 20291, "category": "厨房炊具", "desc": "木柄不锈钢松肉锤"},
  {"id": 20292, "category": "厨房餐具", "desc": "硅藻土吸水杯垫碗碟沥水垫"},
  {"id": 20293, "category": "厨房炊具", "desc": "不锈钢硅胶头厨房夹"},
  {"id": 20294, "category": "厨房炊具", "desc": "四件套不锈钢刨丝器"},
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
