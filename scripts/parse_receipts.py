import json
import re

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

# Let's inspect all items across all pages
# Each item has:
# 1. Description line(s)
# 2. Barcode or SKU
# 3. Unit Price ($...)
# 4. Quantity (*... or number)
# 5. Line Total ($...)

# Let's write a regex/state-machine to parse lines from each page
def parse_page_items(page_idx, page_boxes):
    boxes = sorted(page_boxes, key=lambda b: (b['box'][0][1], b['box'][0][0]))
    
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
    
    return lines

all_lines_by_page = {}
for p in pages:
    all_lines_by_page[p['page_index']] = parse_page_items(p['page_index'], p['boxes'])

print("Parsed lines for all 7 pages.")
