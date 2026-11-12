import json

with open('scripts/invoice_ocr_full.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

for p in pages:
    idx = p['page_index']
    texts = [b['text'] for b in p['boxes']]
    print(f"\n=================== PAGE {idx} ===================")
    # Search for keywords like TOTAL, PRESUPUESTO, REMITO, FECHA, NRO, CHEN, etc.
    for i, t in enumerate(texts):
        if any(k in t.upper() for k in ['TOTAL', 'PRESUPUESTO', 'FECHA', 'REMITO', 'CLIENTE', 'CHEN', 'FACTURA', 'ORDEN', 'PAGAR']):
            print(f"  Line {i}: {t}")
    # Also show full text joined
    full_str = " | ".join(texts)
    print("  Full text snippet:", full_str[:200])
