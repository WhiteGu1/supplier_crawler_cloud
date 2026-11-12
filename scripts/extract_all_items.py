import json
import re

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

all_extracted_items = []

for p in pages:
    idx = p['page_index']
    boxes = sorted(p['boxes'], key=lambda b: (b['box'][0][1], b['box'][0][0]))
    
    # Cluster into lines
    lines = []
    curr_line = []
    curr_y = None
    for b in boxes:
        y = b['box'][0][1]
        if curr_y is None or abs(y - curr_y) < 28:
            curr_line.append(b)
            curr_y = y if curr_y is None else (curr_y + y) / 2
        else:
            lines.append(sorted(curr_line, key=lambda x: x['box'][0][0]))
            curr_line = [b]
            curr_y = y
    if curr_line:
        lines.append(sorted(curr_line, key=lambda x: x['box'][0][0]))

    # Now let's scan lines for items
    # An item typically has:
    # 1. An identifier / name / barcode line
    # 2. A price line with *0.77
    # 3. A qty line with subtotal
    # Or variations
    page_items = []
    
    # Let's find every occurrence of subtotal / price
    # Look at the tokens in lines
    for i, l in enumerate(lines):
        line_txt = " | ".join([b['text'] for b in l])
        
        # Check if line contains a subtotal: e.g. $27720, $43890, $9817.5
        # In this receipt format, subtotals are usually the largest dollar amount in the item group
        pass

