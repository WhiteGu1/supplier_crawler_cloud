import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-13
  {"id": 17395, "category": "卫浴用品", "desc": "木质小桶装浴室配件套装"},
  {"id": 17396, "category": "美妆个护", "desc": "黑色金属支架圆形台式化妆镜"},
  {"id": 17397, "category": "美妆个护", "desc": "黑色金属支架拱形台式化妆镜"},
  {"id": 17398, "category": "美妆个护", "desc": "黑色金属支架方形圆角台式化妆镜"},
  {"id": 17399, "category": "文具办公", "desc": "儿童彩绘艺术套装"},
  {"id": 17400, "category": "文具办公", "desc": "大号彩笔绘画套装"},
  {"id": 17401, "category": "收纳整理", "desc": "金属扣铝合金收纳箱太空宇航员图案"},
  {"id": 17402, "category": "箱包配件", "desc": "多色长款笔袋化妆包"},
  {"id": 17403, "category": "箱包配件", "desc": "儿童双肩背包Good Luck字样"},
  {"id": 17678, "category": "厨房炊具", "desc": "不锈钢水果削皮器"},
  # batch-14 (注意17678重复，只取一条)
  {"id": 17679, "category": "厨房餐具", "desc": "Benabi竹木砧板"},
  {"id": 17680, "category": "厨房餐具", "desc": "Benabi竹木砧板带手柄"},
  {"id": 17681, "category": "厨房储物", "desc": "黑色金属网格圆柱形收纳篮"},
  {"id": 17682, "category": "装饰品", "desc": "黑色椭圆形台式梳妆镜"},
  {"id": 17683, "category": "装饰品", "desc": "黑色椭圆形台式梳妆镜"},
  {"id": 17779, "category": "厨房炊具", "desc": "硅胶漏勺木质手柄"},
  {"id": 17780, "category": "餐饮用品", "desc": "玻璃水壶配玻璃杯"},
  {"id": 17781, "category": "厨房储物", "desc": "不锈钢长方形便当盒配透明密封盖"},
  {"id": 17782, "category": "厨房储物", "desc": "不锈钢长方形便当盒配透明密封盖"},
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
