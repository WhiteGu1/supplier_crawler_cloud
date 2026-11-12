import pymysql, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# Get all 105 remaining toys needing sub-classification
cur.execute("""
    SELECT id, name, supplier_id, image_local
    FROM products
    WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%')
    AND category NOT LIKE '%>%>%'
    AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
""")
rows = cur.fetchall()
print(f"Total remaining: {len(rows)}")

# Build absolute image paths
items = []
for r in rows:
    pid, name, sid, img = r[0], r[1], r[2], r[3]
    # Normalize path
    if img.startswith('/'):
        img_path = 'D:\\projects\\supplier_crawler' + img.replace('/', '\\')
    elif img.startswith('images/'):
        img_path = 'D:\\projects\\supplier_crawler\\' + img.replace('/', '\\')
    else:
        img_path = img
    items.append({"id": pid, "name": name, "supplier_id": sid, "image": img_path})

# Split into batches of 10
batch_dir = 'D:\\projects\\supplier_crawler\\toy_batches2'
os.makedirs(batch_dir, exist_ok=True)

for i in range(0, len(items), 10):
    batch_num = i // 10
    batch = items[i:i+10]
    fname = os.path.join(batch_dir, f'toy_batch_{batch_num}.json')
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f"Batch {batch_num}: {len(batch)} items (ids {batch[0]['id']}-{batch[-1]['id']})")

print(f"\nTotal batches: {(len(items)+9)//10}")
conn.close()
