import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

results = [
  # batch-35
  {"id": 17983, "category": "美妆个护", "desc": "黑色折叠手持化妆镜带长柄"},
  {"id": 17984, "category": "收纳整理", "desc": "折叠式旅行收纳包多色"},
  {"id": 17985, "category": "收纳整理", "desc": "折叠式旅行收纳包图案款"},
  {"id": 17986, "category": "收纳整理", "desc": "多色马卡龙化妆收纳包"},
  {"id": 17987, "category": "文具办公", "desc": "COOL SPORT印花笔袋"},
  {"id": 17988, "category": "文具办公", "desc": "Happy time印花笔袋"},
  {"id": 17989, "category": "文具办公", "desc": "猫爪图案透明PVC笔袋"},
  {"id": 17990, "category": "文具办公", "desc": "YOU SHOULD羽绒感笔袋"},
  {"id": 17991, "category": "文具办公", "desc": "卡通狗狗造型毛绒笔袋"},
  {"id": 17992, "category": "文具办公", "desc": "DO YOU/NICE DAYS印花笔袋"},
  # batch-36
  {"id": 17993, "category": "文具办公", "desc": "5色荧光便签指示标签"},
  {"id": 17994, "category": "文具办公", "desc": "猫咪造型便签本"},
  {"id": 17995, "category": "收纳整理", "desc": "透明PVC拉链文件袋"},
  {"id": 17996, "category": "文具办公", "desc": "5色透明塑料按扣文件袋"},
  {"id": 17997, "category": "文具办公", "desc": "彩色透明按扣塑料文件袋"},
  {"id": 17998, "category": "文具办公", "desc": "卡通造型立体线圈笔记本"},
  {"id": 17999, "category": "五金工具", "desc": "JZcutter美工刀套装"},
  {"id": 18000, "category": "五金工具", "desc": "美工刀4件套"},
  {"id": 18001, "category": "五金工具", "desc": "18mm美工刀两件套"},
  {"id": 18002, "category": "五金工具", "desc": "18mm重型美工刀"},
  # batch-37
  {"id": 18003, "category": "文具办公", "desc": "订书机套装3件套"},
  {"id": 18004, "category": "文具办公", "desc": "迷你订书机套装4色"},
  {"id": 18005, "category": "文具办公", "desc": "办公三件套订书机订书钉打孔器"},
  {"id": 18006, "category": "文具办公", "desc": "迷你订书机吸塑卡装4色"},
  {"id": 18007, "category": "文具办公", "desc": "订书机套装含订书钉3色"},
  {"id": 18008, "category": "文具办公", "desc": "办公三件套3色"},
  {"id": 18009, "category": "文具办公", "desc": "办公三件套4色"},
  {"id": 18010, "category": "文具办公", "desc": "标准订书钉1000枚"},
  {"id": 18011, "category": "文具办公", "desc": "订书机套装含500枚订书钉"},
  {"id": 18012, "category": "文具办公", "desc": "订书机套装含订书钉4色"},
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
