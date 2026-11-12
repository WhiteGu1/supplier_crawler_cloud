import json
import re

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

for p in pages:
    idx = p['page_index']
    boxes = sorted(p['boxes'], key=lambda b: (b['box'][0][1], b['box'][0][0]))
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

    subtotals = []
    for l in lines:
        for b in l:
            t = b['text'].strip()
            # find dollar amounts that are subtotals or prices
            # subtotal is usually integer or ends in .5, e.g. $27720, $43890, $16632
            # or preceded by *qty
            pass

    # Let's inspect all boxes with '$' in each page
    dollar_boxes = []
    for b in p['boxes']:
        t = b['text'].strip()
        m = re.match(r'^\$?(\d+(?:\.\d+)?)$', t.replace('$', '').replace(',', ''))
        if '$' in t or (m and float(m.group(1)) > 100):
            # check if it's near *0.77
            pass

