import json
from match_full_details import invoice_items
from build_full_comparison_table import assigned_inv

print("Unassigned invoice items:")
for i, inv in enumerate(invoice_items):
    if i not in assigned_inv:
        clean_name = inv['name'].encode('ascii', 'replace').decode('ascii')
        print(f"  [{i}] P{inv['p']} | Code:{inv['sku']} | BC:{inv['barcode']} | Price:{inv['price']} | Qty:{inv['qty']} | {clean_name}")
