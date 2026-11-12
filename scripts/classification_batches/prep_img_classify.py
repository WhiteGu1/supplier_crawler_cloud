"""准备467条无分类商品的图片路径，分批输出供subagent识图分类"""
import pymysql, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}

conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("""SELECT id, name, sku, image_local, supplier_id
               FROM products 
               WHERE (category IS NULL OR category='')
               ORDER BY id""")
rows = cur.fetchall()
conn.close()

# 检查图片是否存在
base_dir = r"D:\projects\supplier_crawler"
missing = 0
valid = []
for r in rows:
    img_path = os.path.join(base_dir, r['image_local']) if r['image_local'] else None
    if img_path and os.path.exists(img_path):
        valid.append({
            'id': r['id'],
            'name': r['name'],
            'sku': r['sku'] or '',
            'image_path': img_path.replace('\\', '/')
        })
    else:
        missing += 1
        valid.append({
            'id': r['id'],
            'name': r['name'],
            'sku': r['sku'] or '',
            'image_path': None
        })

print(f"总商品: {len(rows)}")
print(f"图片存在: {len(valid) - missing}")
print(f"图片缺失: {missing}")

# 分批，每批10条（图片识别每批10张，和之前一样）
batch_size = 10
out_dir = r"D:\projects\supplier_crawler\classify_cache\new_products"
os.makedirs(out_dir, exist_ok=True)

batches = []
for i in range(0, len(valid), batch_size):
    batches.append(valid[i:i+batch_size])

for i, batch in enumerate(batches):
    with open(os.path.join(out_dir, f"img_batch_{i}.json"), "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)

print(f"分批: {len(batches)}批, 每批{batch_size}条")
for i, b in enumerate(batches):
    has_img = sum(1 for x in b if x['image_path'])
    print(f"  Batch {i}: {len(b)}条 (有图{has_img}) id {b[0]['id']}~{b[-1]['id']}")
