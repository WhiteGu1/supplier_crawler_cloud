import json

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

# Inspect Page 1 in detail
p1 = pages[0]
boxes = sorted(p1['boxes'], key=lambda b: (b['box'][0][1], b['box'][0][0]))

# Cluster boxes into lines if y difference < 25
lines = []
curr_line = []
curr_y = None

for b in boxes:
    y = b['box'][0][1]
    if curr_y is None or abs(y - curr_y) < 30:
        curr_line.append(b)
        curr_y = y if curr_y is None else (curr_y + y) / 2
    else:
        lines.append(sorted(curr_line, key=lambda x: x['box'][0][0]))
        curr_line = [b]
        curr_y = y

if curr_line:
    lines.append(sorted(curr_line, key=lambda x: x['box'][0][0]))

print(f"Page 1 has {len(lines)} clustered lines:")
for i, l in enumerate(lines):
    line_str = "  |  ".join([b['text'] for b in l])
    y_avg = sum(b['box'][0][1] for b in l) / len(l)
    print(f"Line {i:2d} (y={y_avg:4.0f}): {line_str}")
