import json
import re

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

# Let's inspect all boxes on all pages
for p in pages:
    idx = p['page_index']
    filename = p['filename']
    boxes = sorted(p['boxes'], key=lambda b: (b['box'][0][1], b['box'][0][0]))
    
    print(f"\n========================================================")
    print(f"PAGE {idx}: {filename}")
    print(f"========================================================")
    for b in boxes:
        y = b['box'][0][1]
        x = b['box'][0][0]
        text = b['text']
        print(f"[{y:4.0f}, {x:4.0f}] {text}")
