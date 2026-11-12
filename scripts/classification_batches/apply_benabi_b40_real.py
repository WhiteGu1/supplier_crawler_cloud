import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-40 (real results from subagent)
  {"id": 20305, "category": "卫浴用品", "desc": "玻璃按压式皂液器"},
  {"id": 20306, "category": "卫浴用品", "desc": "黑色陶瓷按压式皂液器"},
  {"id": 20307, "category": "卫浴用品", "desc": "网纱沐浴球浴花"},
  {"id": 20308, "category": "宠物用品", "desc": "宠物窝狗床"},
  {"id": 20309, "category": "宠物用品", "desc": "方形宠物狗床"},
  {"id": 20310, "category": "厨房炊具", "desc": "四孔煎蛋锅白色"},
  {"id": 20311, "category": "厨房炊具", "desc": "四孔煎蛋锅大理石纹"},
  {"id": 20312, "category": "厨房餐具", "desc": "不锈钢削皮器"},
  {"id": 20313, "category": "厨房餐具", "desc": "迷你硅胶厨具三件套"},
  {"id": 20314, "category": "厨房餐具", "desc": "不锈钢披萨滚刀"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"成功更新 {updated}/{len(results)} 条")

# 查询有图片的未分类商品
cur.execute("""
    SELECT id, image_local 
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='') 
      AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
""")
rows = cur.fetchall()
print(f"\n有图片但未分类: {len(rows)} 条")
for pid, img in rows[:10]:
    print(f"  ID={pid}, img={img}")

# 查询无图片的未分类商品
cur.execute("""
    SELECT COUNT(*) 
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='') 
      AND (image_local IS NULL OR image_local = '')
""")
cnt = cur.fetchone()[0]
print(f"\n无图片且未分类: {cnt} 条")

# 总计
cur.execute("""
    SELECT COUNT(*) 
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='')
""")
total = cur.fetchone()[0]
print(f"benabi 总未分类: {total} 条")

conn.close()
