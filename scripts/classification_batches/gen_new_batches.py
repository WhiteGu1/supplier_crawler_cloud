import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')
import pymysql

# 读现有分类清单
category_list = []
if os.path.exists('uncat_batches/category_list.json'):
    with open('uncat_batches/category_list.json', 'r', encoding='utf-8') as f:
        category_list = json.load(f)
print(f"现有分类路径数: {len(category_list)}")

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# 查询所有无分类商品
cur.execute("""
    SELECT id, supplier_id, name, sku, brand, image_local
    FROM products 
    WHERE category IS NULL OR category = ''
    ORDER BY supplier_id, id
""")
rows = cur.fetchall()
print(f"无分类商品数: {len(rows)}")

# 按供应商分组记录
by_supplier = {}
for r in rows:
    by_supplier.setdefault(r['supplier_id'], []).append(r)
print("按供应商分布:")
for sup, items in sorted(by_supplier.items()):
    print(f"  sup={sup}: {len(items)}条")

# 生成批次文件（按供应商分组，每批10条，跨供应商填充）
out_dir = 'uncat_batches_v2'
os.makedirs(out_dir, exist_ok=True)

# 清空旧batch文件
for f in os.listdir(out_dir):
    if f.startswith('batch_') and f.endswith('.json'):
        os.remove(os.path.join(out_dir, f))
    elif f.startswith('result_') and f.endswith('.json'):
        os.remove(os.path.join(out_dir, f))

# 写入批次文件（每批10条）
batch_size = 10
batches = []
for i in range(0, len(rows), batch_size):
    chunk = rows[i:i+batch_size]
    batches.append(chunk)

for idx, chunk in enumerate(batches):
    items = []
    for r in chunk:
        items.append({
            "id": r['id'],
            "supplier_id": r['supplier_id'],
            "name": r['name'],
            "sku": r['sku'],
            "brand": r['brand'],
            "image_local": r['image_local']
        })
    with open(f'{out_dir}/batch_{idx}.json', 'w', encoding='utf-8') as f:
        json.dump({"batch_id": idx, "items": items}, f, ensure_ascii=False, indent=2)

print(f"\n生成 {len(batches)} 个批次文件到 {out_dir}/")

# 同时复制category_list.json
import shutil
if os.path.exists('uncat_batches/category_list.json'):
    shutil.copy('uncat_batches/category_list.json', f'{out_dir}/category_list.json')
    print(f"复制 category_list.json 到 {out_dir}/")

conn.close()