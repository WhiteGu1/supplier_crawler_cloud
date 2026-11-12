import json

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

for p in pages:
    idx = p['page_index']
    boxes = p['boxes']
    # Sort boxes vertically (by top y coordinate)
    # box format: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    sorted_boxes = sorted(boxes, key=lambda b: (b['box'][0][1], b['box'][0][0]))
    print(f"\n=================== PAGE {idx} (Sorted by Y) ===================")
    for b in sorted_boxes:
        y = b['box'][0][1]
        x = b['box'][0][0]
        text = b['text']
        print(f"y={y:4.0f}, x={x:4.0f}: {text}")
