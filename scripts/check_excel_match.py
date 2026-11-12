import openpyxl
import os

folder = r'C:\Users\Administrator\Downloads'
target_file = None
for f in os.listdir(folder):
    if f.endswith('.xlsx') and '121234' in f:
        target_file = os.path.join(folder, f)
        break

print("Target file:", target_file)
wb = openpyxl.load_workbook(target_file, data_only=True)
sheet = wb.active

excel_items = []
for r in range(2, sheet.max_row + 1):
    sku = str(sheet.cell(r, 2).value or '')
    name = str(sheet.cell(r, 3).value or '')
    qty = sheet.cell(r, 5).value or 0
    orig_p = str(sheet.cell(r, 6).value or '')
    disc_p = str(sheet.cell(r, 7).value or '')
    subtotal = str(sheet.cell(r, 8).value or '')
    excel_items.append({
        'row': r, 'sku': sku, 'name': name, 'qty': qty,
        'orig_p': orig_p, 'disc_p': disc_p, 'subtotal': subtotal
    })

print(f"Total rows in 采购清单 Excel: {len(excel_items)}")

# Search for the unassigned items in the Excel file
from show_unassigned import invoice_items
from build_full_comparison_table import assigned_inv
unassigned_indices = [i for i in range(len(invoice_items)) if i not in assigned_inv]

for idx in unassigned_indices:
    inv = invoice_items[idx]
    inv_code = inv['sku'].upper()
    hits = []
    for it in excel_items:
        it_str = (it['name'] + ' ' + it['sku']).upper()
        if inv_code and inv_code in it_str:
            hits.append(it)
    clean_name = inv['name'].encode('ascii', 'replace').decode('ascii')
    print(f"\nInv [{idx}] P{inv['p']} {inv['sku']} (P:{inv['price']}, Q:{inv['qty']}): {clean_name}")
    if hits:
        for h in hits:
            h_name = h['name'].encode('ascii', 'replace').decode('ascii')
            print(f"   -> Found in 采购清单 Row {h['row']}: Qty={h['qty']}, Price={h['orig_p']} | {h_name[:50]}")
    else:
        print("   -> Not in 采购清单 Excel")
