import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-15 结果
results = [
  {"id": 2326, "category": "玩具游戏", "desc": "HADANA品牌塑封扑克牌(50张/40张装)"},
  {"id": 2327, "category": "玩具游戏", "desc": "HADANA罗马风格塑封扑克牌"},
  {"id": 2328, "category": "玩具游戏", "desc": "HACHAZO品牌彩色塑封扑克牌"},
  {"id": 2329, "category": "玩具游戏", "desc": "HACHAZO塑封扑克牌(多款图案)"},
  {"id": 2330, "category": "玩具游戏", "desc": "HACHAZO扑克/桥牌塑封卡牌"},
  {"id": 2331, "category": "玩具游戏", "desc": "Washable可水洗全塑料扑克牌"},
  {"id": 2332, "category": "玩具游戏", "desc": "UNO经典纸牌游戏(家用卡牌)"},
  {"id": 2333, "category": "玩具游戏", "desc": "西班牙风格塑封扑克牌展示装"},
  {"id": 2334, "category": "日用百货", "desc": "Candela白色纸胶带(10mm×50m,遮蔽/美纹胶带)"},
  {"id": 2335, "category": "日用百货", "desc": "Candela白色纸胶带(美纹胶带卷装)"},
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
