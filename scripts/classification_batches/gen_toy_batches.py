import pymysql, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

# Get all items with category = '玩具 > 玩具游戏' that have images
cur.execute("SELECT id, supplier_id, sku, name, image_local FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != '' ORDER BY supplier_id, id")
items = cur.fetchall()
print(f'Total toys items with image: {len(items)}')

# Generate batch files (10 items per batch)
batch_size = 10
batch_dir = r'D:\projects\supplier_crawler\toy_batches'
os.makedirs(batch_dir, exist_ok=True)

# Remove old batch files
for f in os.listdir(batch_dir):
    if f.startswith('toy_batch_') and f.endswith('.json'):
        os.remove(os.path.join(batch_dir, f))

num_batches = (len(items) + batch_size - 1) // batch_size
for i in range(num_batches):
    batch = items[i*batch_size : (i+1)*batch_size]
    batch_data = []
    for item in batch:
        # Fix image path - ensure full path
        img = item['image_local']
        if img and not os.path.isabs(img):
            img = os.path.join(r'D:\projects\supplier_crawler', img.replace('/', os.sep))
        batch_data.append({
            'id': item['id'],
            'supplier_id': item['supplier_id'],
            'sku': item['sku'] or '',
            'name': item['name'],
            'image': img
        })
    with open(os.path.join(batch_dir, f'toy_batch_{i}.json'), 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, ensure_ascii=False, indent=2)

print(f'Generated {num_batches} batch files in {batch_dir}')

# Also get no-image items for name-based classification
cur.execute("SELECT id, supplier_id, sku, name FROM products WHERE category = '玩具 > 玩具游戏' AND (image_local IS NULL OR image_local = '') ORDER BY supplier_id, id")
no_img = cur.fetchall()
print(f'\nNo-image items: {len(no_img)}')
# These can be classified by name only
for item in no_img[:20]:
    print(f"  id={item['id']} sid={item['supplier_id']} name={item['name']}")

conn.close()
