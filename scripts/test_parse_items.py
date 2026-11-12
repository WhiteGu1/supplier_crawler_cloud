import json
import re

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

# Let's inspect how items are laid out on each page
# Each item typically has:
# - A description line and a barcode/code line
# - A unit price ($...)
# - A quantity (*...)
# - A line total ($...)

all_parsed_items = []

for p in pages:
    idx = p['page_index']
    filename = p['filename']
    boxes = sorted(p['boxes'], key=lambda b: (b['box'][0][1], b['box'][0][0]))
    
    # Let's find all line totals ($...) and quantities (*...)
    # Group boxes that have close Y coordinates
    # Let's see the texts on this page
    texts = [b['text'] for b in boxes]
    print(f"Page {idx} has {len(texts)} text elements")

    # Let's look for numbers preceded by $ or *
    prices = [t for t in texts if '$' in t]
    qtys = [t for t in texts if '*' in t and not any(k in t for k in ['0.77', 'WWW', 'INS'])]
    print(f"  Prices/Totals count: {len(prices)}, Qtys count: {len(qtys)}")
