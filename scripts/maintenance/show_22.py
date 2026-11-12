import sys, json
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('D:/projects/supplier_crawler/uncat_batches_v2/result_22.json','r',encoding='utf-8'))
for x in d:
    print(x)