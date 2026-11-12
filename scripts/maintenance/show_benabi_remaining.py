import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('D:/projects/supplier_crawler/benabi_batches.json', 'r', encoding='utf-8') as f:
    batches = json.load(f)

print(f"总批次数: {len(batches)}")
print(f"已完成: batch-0~31 (缺 batch-16)")
print(f"剩余: batch-16, batch-32~{len(batches)-1}")
print()

# batch-16 数据
print("=== BATCH 16 (待补) ===")
for j, item in enumerate(batches[16]):
    print(f"{j+1}. ID:{item['id']}, 路径: {item['img']}")
print()

# batch-32+ 数据
for i in range(32, len(batches)):
    batch = batches[i]
    print(f"=== BATCH {i} ===")
    for j, item in enumerate(batch):
        print(f"{j+1}. ID:{item['id']}, 路径: {item['img']}")
    print()
