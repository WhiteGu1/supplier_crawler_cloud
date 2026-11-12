import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-3-retry2 results
results = [
  {"id": 20422, "category": "卫浴用品", "desc": "BH品牌浴帘套装180x180cm含12个挂钩多种颜色图案"},
  {"id": 20423, "category": "卫浴用品", "desc": "Nainoo品牌PEVA浴帘180x180cm五种颜色含配套挂钩"},
  {"id": 20424, "category": "卫浴用品", "desc": "黑色陶瓷按压式分配瓶菱形浮雕纹理竹木装饰环"},
  {"id": 20425, "category": "卫浴用品", "desc": "彩色玻璃按压瓶套装6个菠萝形菱格纹银色按压泵头"},
  {"id": 20426, "category": "卫浴用品", "desc": "沐浴球沐浴花2个装蓝白和粉白配色尼龙网状材质"},
  {"id": 20427, "category": "收纳整理", "desc": "透明玻璃储物罐竹木盖圆柱形密封罐可收纳棉签化妆品"},
  {"id": 20428, "category": "卫浴用品", "desc": "落地式金属卫生纸架可放正在使用卷纸底部储存备用卷纸"},
  {"id": 20429, "category": "卫浴用品", "desc": "哑光黑色卫浴套装6件垃圾桶马桶刷皂液瓶漱口杯肥皂碟卷纸架"},
  {"id": 20430, "category": "卫浴用品", "desc": "北欧风黑色竖纹竹木盖卫浴套装6件"},
  {"id": 20431, "category": "卫浴用品", "desc": "多功能落地式金属线材卫生纸收纳架顶部置物篮中部挂杆底部储物篮"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-3-retry2: 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
