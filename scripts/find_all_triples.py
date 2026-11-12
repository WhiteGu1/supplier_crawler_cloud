import json
import re

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

for p in pages:
    idx = p['page_index']
    boxes = sorted(p['boxes'], key=lambda b: (b['box'][0][1], b['box'][0][0]))
    
    # Extract all numbers from text
    texts = [b['text'] for b in boxes]
    
    # Let's inspect the clustered lines
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

    print(f"\n=================== PAGE {idx} ===================")
    page_subtotals = []
    for i, l in enumerate(lines):
        txts = [b['text'] for b in l]
        line_str = " | ".join(txts)
        # Find all numbers with optional $
        for t in txts:
            # find $XXXX
            m = re.findall(r'\$(\d+(?:\.\d+)?)', t)
            # or *N
            # print line if contains $ or *
        print(f"L{i:02d}: {line_str}")
