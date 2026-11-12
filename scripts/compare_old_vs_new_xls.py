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

print(f"Old Excel has {len(old_items)} rows.")
print("Seq 2 in Old Excel:", old_items[1])
print("Seq 17 in Old Excel:", old_items[16])

# Let's see what 11111..444444 have when merged
xls_1_to_4 = []
for t in all_tickets[:4]:
    for it in t['items']:
        xls_1_to_4.append(it)

print(f"Total raw items in 11111..444444: {len(xls_1_to_4)}")
