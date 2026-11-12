import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('D:/projects/supplier_crawler/diego_batches.json', 'r', encoding='utf-8') as f:
    batches = json.load(f)

for i in range(24, 32):
    if i >= len(batches):
        break
    batch = batches[i]
    print(f"=== BATCH {i} ===")
    for j, item in enumerate(batch):
        print(f"{j+1}. ID:{item['id']}, 路径: {item['img']}")
    print()

print(f"总批次数: {len(batches)}")
