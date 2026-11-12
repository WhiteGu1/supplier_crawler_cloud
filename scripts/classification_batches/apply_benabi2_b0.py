import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-0
  {"id": 6175, "category": "厨房储物", "desc": "玻璃调味瓶油壶"},
  {"id": 6756, "category": "收纳整理", "desc": "黑色金属多层鞋架"},
  {"id": 17778, "category": "厨房炊具", "desc": "硅胶锅铲漏勺套装"},
  {"id": 17813, "category": "派对用品", "desc": "红黑色礼品包装盒"},
  {"id": 17814, "category": "派对用品", "desc": "礼品包装盒含手表"},
  {"id": 17815, "category": "派对用品", "desc": "礼品包装盒含手表"},
  {"id": 17816, "category": "派对用品", "desc": "多色礼品包装盒"},
  {"id": 17817, "category": "装饰品", "desc": "圆形挂镜玄关装饰"},
  {"id": 17818, "category": "装饰品", "desc": "圆形挂镜玄关装饰"},
  {"id": 17819, "category": "装饰品", "desc": "金色边框矩形镜玄关装饰"},
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
