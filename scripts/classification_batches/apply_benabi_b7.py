import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-7
  {"id": 17335, "category": "卫浴用品", "desc": "圆形LED浴室壁挂镜带触控开关"},
  {"id": 17336, "category": "美妆个护", "desc": "金框方形桌面梳妆镜"},
  {"id": 17337, "category": "美妆个护", "desc": "金框方形LED梳妆台镜带触控"},
  {"id": 17338, "category": "美妆个护", "desc": "金框方形LED梳妆台镜带触控"},
  {"id": 17339, "category": "美妆个护", "desc": "金框方形桌面梳妆镜"},
  {"id": 17340, "category": "美妆个护", "desc": "金框方形LED梳妆台镜带触控"},
  {"id": 17341, "category": "卫浴用品", "desc": "黑色边框全身落地穿衣镜"},
  {"id": 17342, "category": "卫浴用品", "desc": "金色边框全身落地穿衣镜"},
  {"id": 17343, "category": "餐饮用品", "desc": "圆形编织餐垫白灰粉三色"},
  {"id": 17344, "category": "餐饮用品", "desc": "圆形编织餐垫多色"},
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
