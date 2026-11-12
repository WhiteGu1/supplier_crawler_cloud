import sys, json
sys.stdout.reconfigure(encoding='utf-8')
for bn in [0,1,2,3,4]:
    try:
        d = json.load(open(f'D:/projects/supplier_crawler/uncat_batches_v2/batch_{bn}.json','r',encoding='utf-8'))
        print(f"\n=== batch_{bn} ===")
        for it in d['items']:
            print(f"  id={it['id']} sup={it['supplier_id']} {it['name'][:60]}")
    except Exception as e:
        print(f"batch_{bn}: {e}")