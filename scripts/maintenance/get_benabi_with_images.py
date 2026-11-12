import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 查询有图片的未分类商品
cur.execute("""
    SELECT id, image_local, name
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='') 
      AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
""")
rows = cur.fetchall()
print(f"有图片但未分类: {len(rows)} 条")

# 输出所有ID和路径，每批10个
batches = []
for i in range(0, len(rows), 10):
    batch = rows[i:i+10]
    batches.append(batch)
    
print(f"共 {len(batches)} 批")

# 输出每批的JSON
for i, batch in enumerate(batches):
    items = []
    for pid, img, name in batch:
        full_path = f"D:/projects/supplier_crawler/{img}"
        items.append({"id": pid, "path": full_path, "name": name[:50] if name else ""})
    print(f"\n=== batch-{i} ===")
    for item in items:
        print(f"  ID:{item['id']} path:{item['path']} name:{item['name']}")

conn.close()
