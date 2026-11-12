"""读取待验证第一批，输出图片路径列表供识图"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\projects\supplier_crawler\classify_cache\verify_results\verify_batches.json", "r", encoding="utf-8") as f:
    batches = json.load(f)

batch0 = batches[0]
print(f"第一批: {len(batch0['items'])} 条\n")
for item in batch0['items']:
    print(f"id={item['id']}")
    print(f"  name: {item.get('name','')}")
    print(f"  old: {item['old_category']}")
    print(f"  new: {item['new_category']}")
    print(f"  img: {item['image_path']}")
    print()
