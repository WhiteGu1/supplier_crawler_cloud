import json

with open('scripts/resolved_bella_cart.json', encoding='utf-8') as f:
    res = json.load(f)['resolved']

with open('scripts/missing_comparison.txt', encoding='utf-8') as f:
    missing_lines = f.readlines()

missing_skus = []
for line in missing_lines[4:]:
    if 'SKU: ' in line:
        sku = line.split('SKU: ')[1].split(' ')[0].strip()
        missing_skus.append(sku)

for r in res:
    p_id = str(r.get('parent_id') or r['id'])
    if p_id in missing_skus:
        name_clean = r['name'].encode('ascii', 'replace').decode('ascii')
        print(f"ID: {r['id']} | Parent: {p_id} | Qty: {r['qty']} | {name_clean[:35]} | Spec: {r.get('var_label')}")
