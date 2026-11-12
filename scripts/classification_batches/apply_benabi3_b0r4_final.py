import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-0-retry4 results (the final batch!)
results = [
  {"id": 20352, "category": "厨房储物", "desc": "玻璃保鲜盒套装三只方形钢化玻璃密封盒卡扣式盒盖"},
  {"id": 20353, "category": "厨房餐具", "desc": "便携式塑料饭盒三色款透明翻盖带卡扣锁扣"},
  {"id": 20354, "category": "厨房储物", "desc": "黑色双层厨房沥水碗架金属材质可立放餐盘悬挂杯子"},
  {"id": 20355, "category": "厨房储物", "desc": "黑色铁艺厨房多功能收纳架侧边镂空刀叉图案木质底板"},
  {"id": 20356, "category": "厨房储物", "desc": "不锈钢双层厨房沥水架上层放碗碟侧边配刀叉筒"},
  {"id": 20357, "category": "餐饮用品", "desc": "Naosso品牌植物花卉印花桌布135x180cm防水防油"},
  {"id": 20358, "category": "厨房餐具", "desc": "透明玻璃马克杯菱形切面纹理杯身加厚棱角底座"},
  {"id": 20359, "category": "厨房餐具", "desc": "条纹玻璃凉水壶套装含壶和配套玻璃杯竖条纹锥形壶身"},
  {"id": 20360, "category": "厨房餐具", "desc": "南瓜纹玻璃马克杯三只装花瓣形杯口三色款"},
  {"id": 20361, "category": "厨房餐具", "desc": "锤纹玻璃马克杯六只套装彩色玻璃把手锤纹防滑隔热"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-0-retry4 (FINAL): 成功更新 {updated}/{len(results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining_with_img = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining_with_img}")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='')")
remaining_total = cur.fetchone()[0]
print(f"benabi 剩余未分类总计(含无图): {remaining_total}")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND category IS NOT NULL AND category != ''")
classified = cur.fetchone()[0]
print(f"benabi 已分类: {classified}")

conn.close()
