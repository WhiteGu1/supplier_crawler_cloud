"""获取467条无分类商品，分成10批，每批约50条，输出JSON供subagent分类"""
import pymysql, json, sys
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}

conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("""SELECT p.id, p.name, p.sku, p.brand, p.supplier_id, p.price,
               p.category as current_category, p.image_local,
               s.name as supplier_name
               FROM products p LEFT JOIN suppliers s ON p.supplier_id = s.id
               WHERE (p.category IS NULL OR p.category='')
               ORDER BY p.id""")
rows = cur.fetchall()
conn.close()

for r in rows:
    r['price'] = float(r['price']) if r['price'] else 0

# 获取现有分类列表
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category!='' ORDER BY category")
cats = [r[0] for r in cur.fetchall()]
conn.close()

print(f"无分类商品: {len(rows)}")
print(f"现有分类数: {len(cats)}")

# 分批输出
batch_size = 50
batches = []
for i in range(0, len(rows), batch_size):
    batches.append(rows[i:i+batch_size])

# 写入文件
import os
out_dir = r"D:\projects\supplier_crawler\classify_cache\new_products"
os.makedirs(out_dir, exist_ok=True)

for i, batch in enumerate(batches):
    with open(os.path.join(out_dir, f"input_batch_{i}.json"), "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)

# 写入分类列表
with open(os.path.join(out_dir, "category_list.json"), "w", encoding="utf-8") as f:
    json.dump(cats, f, ensure_ascii=False, indent=2)

print(f"分批: {len(batches)}批, 每批{batch_size}条")
print(f"输出目录: {out_dir}")
for i, b in enumerate(batches):
    print(f"  Batch {i}: {len(b)}条 (id {b[0]['id']}~{b[-1]['id']})")
