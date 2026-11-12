import json

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

for p in pages:
    idx = p['page_index']
    boxes = sorted(p['boxes'], key=lambda b: (b['box'][0][1], b['box'][0][0]))
    print(f"\n=================== PAGE {idx} ===================")
    for b in boxes:
        t = b['text']
        y = b['box'][0][1]
        x = b['box'][0][0]
        # print if it looks like header info or date or numbers
        if y < 400 or any(k in t.lower() for k in ['2026', '2024', 'oct', 'nov', 'hora', 'fecha', 'nro', 'orden', 'remito', 'mitre', 'bella', 'total', 'pagar']):
            print(f"  y={y:4.0f}, x={x:4.0f}: {t}")
