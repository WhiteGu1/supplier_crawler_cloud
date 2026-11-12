import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('D:/projects/supplier_crawler/diego_batches.json', 'r', encoding='utf-8') as f:
    batches = json.load(f)

# 输出 batch 8-15 的图片列表
for i in range(8, 16):
    if i >= len(batches):
        break
    batch = batches[i]
    print(f"=== BATCH {i} ===")
    for j, item in enumerate(batch):
        print(f"{j+1}. ID:{item['id']}, 路径: {item['img']}")
    print()
