import sys, json
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('D:/projects/supplier_crawler/uncat_batches_v2/batch_21.json','r',encoding='utf-8'))
print(json.dumps(d, ensure_ascii=False, indent=2)[:2000])