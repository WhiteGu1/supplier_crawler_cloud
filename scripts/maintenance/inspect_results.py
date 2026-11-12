import sys, json
sys.stdout.reconfigure(encoding='utf-8')
for n in [0,1,2,3,4]:
    try:
        d = json.load(open(f'D:/projects/supplier_crawler/uncat_batches_v2/result_{n}.json','r',encoding='utf-8'))
        if isinstance(d, dict):
            d = d.get('results', d.get('items', d.get('data', [])))
        ln = len(d) if hasattr(d,'__len__') else 0
        print('result_{}: type={} len={}'.format(n, type(d).__name__, ln))
        if d and len(d) > 0:
            print(f'  first: {d[0]}')
    except Exception as e:
        print(f'result_{n} ERROR: {e}')