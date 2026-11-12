import json

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

for p in pages:
    idx = p['page_index']
    texts = [b['text'] for b in p['boxes']]
    print(f"\n=================== PAGE {idx} ({p['filename']}) ===================")
    print("TOP 6:")
    for t in texts[:6]:
        print("  ", t)
    print("BOTTOM 8:")
    for t in texts[-8:]:
        print("  ", t)
