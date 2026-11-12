import openpyxl
from parse_all_5_xls import all_tickets

wb = openpyxl.load_workbook(r'C:\Users\Administrator\Downloads\Bella_Central_合并发票清单_20261105.xlsx', data_only=True)
ws = wb.active

old_items = []
for r in range(4, ws.max_row):
    old_items.append({
        'seq': ws.cell(r, 1).value,
        'sku': ws.cell(r, 2).value,
        'barcode': ws.cell(r, 3).value,
        'name': ws.cell(r, 4).value,
        'qty': ws.cell(r, 5).value,
        'price': ws.cell(r, 6).value,
        'disc_price': ws.cell(r, 7).value,
        'subtotal': ws.cell(r, 8).value,
        'source': ws.cell(r, 9).value
    })

# Raw items in old consolidate_invoices.py were 73 items in exact order:
# t1 (Page 2: 14, Page 6: 15, Page 1: 6) = 35 items -> 11111.xls has 35 items in the EXACT SAME ORDER!
# t2 (18 items) -> 2222222.xls has 18 items in the EXACT SAME ORDER!
# p4 (14 items) -> 444444.xls has 14 items in the EXACT SAME ORDER!
# p5 (6 items) -> 33333.xls has 6 items in the EXACT SAME ORDER!

from consolidate_invoices import t1, t2, p4, p5
old_raw_ordered = t1 + t2 + p4 + p5
new_raw_ordered = (
    all_tickets[0]['items'] + # 11111.xls (35)
    all_tickets[1]['items'] + # 2222222.xls (18)
    all_tickets[3]['items'] + # 444444.xls (14)
    all_tickets[2]['items']   # 33333.xls (6)
)

print(f"Old raw count: {len(old_raw_ordered)}, New raw count (1-4): {len(new_raw_ordered)}")
for idx, (o, n) in enumerate(zip(old_raw_ordered, new_raw_ordered)):
    if o['sku'] != n['sku'] or o['qty'] != n['qty'] or o['price'] != n['price']:
        print(f"Diff at raw index {idx}:")
        print(f"  OLD: SKU={o['sku']} | BC={o['barcode']} | Name={o['name']} | P={o['price']} | Q={o['qty']}")
        print(f"  NEW: SKU={n['sku']} | BC={n['barcode_or_line2']} | Name={n['name_line1']} | P={n['price']} | Q={n['qty']}")
