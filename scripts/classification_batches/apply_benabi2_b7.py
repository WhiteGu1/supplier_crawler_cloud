import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # benabi2-batch-7 (only correct IDs from task: 20452-20456, 24904-24908)
  {"id": 20452, "category": "文具办公", "desc": "不锈钢剪刀三件套"},
  {"id": 20453, "category": "文具办公", "desc": "彩色便签条标签贴"},
  {"id": 20454, "category": "文具办公", "desc": "迷你订书机三件套"},
  {"id": 20455, "category": "餐饮用品", "desc": "保温保冷手提袋野餐包三件套"},
  {"id": 20456, "category": "照明灯具", "desc": "可调节折叠台灯"},
  # 24904-24908 的分类结果不确定（子agent输出了错误ID），暂不写入
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
