import sys, io, pymysql, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT id, sku, name, image_local FROM products WHERE supplier_id=11 AND image_local IS NOT NULL AND image_local != '' AND category = '玩具 > 玩具游戏' ORDER BY id")
rows = cur.fetchall()
print(f'Pending with image: {len(rows)}')

base = r'D:\projects\supplier_crawler'
valid = []
for r in rows:
    img_path = r['image_local']
    full_path = os.path.join(base, img_path.lstrip('/').replace('/', os.sep))
    if os.path.exists(full_path):
        valid.append(r)

print(f'Valid: {len(valid)}')

# Generate batch files 13-19 (or as many as needed)
batch_num = 13
batch_size = 10
for start in range(0, len(valid), batch_size):
    if batch_num > 19:
        break
    batch = valid[start:start+batch_size]
    if not batch:
        break
    with open(rf'D:\projects\supplier_crawler\panda_batch_{batch_num}.json', 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False)
    print(f'batch-{batch_num}: {len(batch)} items')
    for item in batch:
        img_file = item['image_local'].split('/')[-1]
        print(f'  id={item["id"]} sku={item["sku"]} name={item["name"][:40]} img={img_file}')
    batch_num += 1

print(f'\nTotal remaining batches: {batch_num - 1 - 13 + 1} = {batch_num - 13}')
print(f'Remaining after these: {len(valid) - (batch_num - 13) * 10}')

conn.close()
