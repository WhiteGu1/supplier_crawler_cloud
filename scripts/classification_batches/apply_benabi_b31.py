import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-31
  {"id": 17943, "category": "文具办公", "desc": "6支装荧光笔1.4mm笔尖"},
  {"id": 17944, "category": "文具办公", "desc": "卡通胡萝卜造型荧光笔套装"},
  {"id": 17945, "category": "文具办公", "desc": "可擦荧光笔6支双头标记笔"},
  {"id": 17946, "category": "文具办公", "desc": "卡通动物造型荧光笔套装6支"},
  {"id": 17947, "category": "文具办公", "desc": "高光马克笔3支猫爪造型"},
  {"id": 17948, "category": "文具办公", "desc": "6支装猫爪造型荧光笔套装"},
  {"id": 17949, "category": "文具办公", "desc": "运动主题章鱼造型荧光笔套装"},
  {"id": 17950, "category": "文具办公", "desc": "恐龙造型荧光笔套装6支"},
  {"id": 17951, "category": "文具办公", "desc": "2B橡皮30块装"},
  {"id": 17952, "category": "文具办公", "desc": "卡通小熊造型修正贴12个装"},
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
