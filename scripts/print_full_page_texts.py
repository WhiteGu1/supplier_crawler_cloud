import json

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

for p in pages:
    idx = p['page_index']
    boxes = sorted(p['boxes'], key=lambda b: (b['box'][0][1], b['box'][0][0]))
    texts = [b['text'] for b in boxes]
    print(f"\n=================== PAGE {idx} ===================")
    print(" | ".join(texts))
