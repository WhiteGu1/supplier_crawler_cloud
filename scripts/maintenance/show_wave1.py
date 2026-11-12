import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('D:/projects/supplier_crawler/diego_batches.json', 'r', encoding='utf-8') as f:
    batches = json.load(f)

# 输出第0-7批的task
for i in range(8):
    batch = batches[i]
    lines = []
    for j, item in enumerate(batch):
        lines.append(f"{j+1}. ID:{item['id']}, 路径: {item['img']}")
    img_list = "\n".join(lines)
    print(f"=== BATCH {i} (IDs: {[x['id'] for x in batch]}) ===")
    print(img_list)
    print()
