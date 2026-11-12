import json
import re

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

# Let's extract line totals for every line item on every page!
# In the OCR output, line totals are numbers with $ or without $ at the right side (x > 650)
# And each line item has a subtotal.
# Let's write a parser that detects every line item:
# - Description
# - Unit price
# - Quantity
# - Line subtotal

for p in pages:
    idx = p['page_index']
    boxes = sorted(p['boxes'], key=lambda b: (b['box'][0][1], b['box'][0][0]))
    
    # Cluster into lines
    lines = []
    curr = []
    curr_y = None
    for b in boxes:
        y = b['box'][0][1]
        if curr_y is None or abs(y - curr_y) < 28:
            curr.append(b)
            curr_y = y if curr_y is None else (curr_y + y) / 2
        else:
            lines.append(sorted(curr, key=lambda x: x['box'][0][0]))
            curr = [b]
            curr_y = y
    if curr:
        lines.append(sorted(curr, key=lambda x: x['box'][0][0]))

    print(f"\n=================== PAGE {idx} LINES ({len(lines)}) ===================")
    for i, l in enumerate(lines):
        txt = " | ".join(b['text'] for b in l)
        clean_txt = txt.encode('ascii', 'replace').decode('ascii')
        print(f"L{i:02d}: {clean_txt}")
