import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-15
  {"id": 24984, "category": "厨房储物", "desc": "菱形纹玻璃密封罐黑色盖"},
  {"id": 24985, "category": "厨房储物", "desc": "木盖玻璃储物罐套装"},
  {"id": 24986, "category": "厨房储物", "desc": "软木塞玻璃瓶装杂粮"},
  {"id": 24987, "category": "厨房储物", "desc": "琥珀色玻璃储物罐玻璃盖"},
  {"id": 24988, "category": "厨房储物", "desc": "波浪纹玻璃储物罐木盖"},
  {"id": 24989, "category": "厨房储物", "desc": "琥珀色竖纹玻璃罐竹盖"},
  {"id": 24990, "category": "厨房储物", "desc": "木盖玻璃调味罐"},
  {"id": 24991, "category": "厨房储物", "desc": "木盖玻璃调味罐"},
  {"id": 24992, "category": "厨房储物", "desc": "木盖玻璃调味罐"},
  {"id": 24993, "category": "厨房储物", "desc": "灰色玻璃糖罐木盖水晶把手"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"成功更新 {updated}/{len(results)} 条")

# 获取 batch-16~23 路径 (offset 150, limit 80)
cur.execute("""
    SELECT id, image_local, name
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='') 
      AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
    LIMIT 80 OFFSET 150
""")
rows = cur.fetchall()
print(f"\nbatch-16~23 共 {len(rows)} 条:")
for i, (pid, img, name) in enumerate(rows):
    print(f"  {i}: ID={pid} img=D:/projects/supplier_crawler/{img}")

conn.close()
