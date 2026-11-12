import sys, json
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('D:/projects/supplier_crawler/uncat_batches/result_28.json', 'r', encoding='utf-8'))
if isinstance(d, dict):
    print(f"result_28是dict格式, keys={list(d.keys())}")
    if 'results' in d:
        d = d['results']
print(f"result_28条数: {len(d)}")
for item in d:
    print(f"  id={item['id']} cats={item['categories']}")
