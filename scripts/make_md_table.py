import openpyxl

wb = openpyxl.load_workbook(r'C:\Users\Administrator\Downloads\Bella_Central_合并发票清单_20261105.xlsx', data_only=True)
ws = wb.active

lines = []
lines.append("| 序号 | 商品编码 / SKU | 商品名称 / 描述 | 数量 | 网站原单价 | 77折后单价 | 折后小计 (ARS) | 出货来源 (批次) |")
lines.append("| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |")

for r in range(4, ws.max_row):
    idx = ws.cell(r, 1).value
    sku = ws.cell(r, 2).value or '-'
    name = ws.cell(r, 4).value
    qty = ws.cell(r, 5).value
    orig_p = f"${ws.cell(r, 6).value:,.2f}"
    disc_p = f"${ws.cell(r, 7).value:,.2f}"
    subtotal = f"${ws.cell(r, 8).value:,.2f}"
    source = ws.cell(r, 9).value or '-'
    lines.append(f"| {idx} | `{sku}` | {name} | {qty} | {orig_p} | {disc_p} | **{subtotal}** | {source} |")

# total row
tot_qty = ws.cell(ws.max_row, 5).value
tot_sub = f"${ws.cell(ws.max_row, 8).value:,.2f}"
lines.append(f"| **合计** | - | **共 {ws.max_row-4} 款不同商品** | **{tot_qty}** | - | - | **{tot_sub}** | - |")

with open('scripts/merged_table.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"Generated markdown table with {len(lines)} lines.")
