import json
import re

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

for p in pages:
    idx = p['page_index']
    boxes = sorted(p['boxes'], key=lambda b: (b['box'][0][1], b['box'][0][0]))
    texts = [b['text'] for b in boxes]
    for i, t in enumerate(texts):
        if 'TOTAL' in t.upper() or 'PAGAR' in t.upper() or 'CHEN' in t.upper():
            print(f"Page {idx} line {i}: {t}")
            # print adjacent boxes
            for j in range(max(0, i-2), min(len(texts), i+5)):
                print(f"   [{j}] {texts[j]}")
