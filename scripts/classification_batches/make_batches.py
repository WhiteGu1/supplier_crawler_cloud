import json

with open('diego_all_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 分成54批，每批10张（最后一批11张）
batches = []
for i in range(0, len(data), 10):
    batches.append(data[i:i+10])

print(f"Total: {len(data)}, Batches: {len(batches)}")
for i, b in enumerate(batches[:3]):
    print(f"Batch {i}: {len(b)} items, IDs: {[x['id'] for x in b]}")
print("...")

# 保存批次信息
with open('diego_batches.json', 'w', encoding='utf-8') as f:
    json.dump(batches, f, ensure_ascii=False)
