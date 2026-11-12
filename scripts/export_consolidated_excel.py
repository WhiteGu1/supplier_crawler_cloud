import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from consolidate_invoices import all_items
import os

# Merge identical items
merged = {}
for it in all_items:
    # key by SKU and Price (or normalized code)
    key = (it['sku'].strip(), it['price'])
    if key not in merged:
        merged[key] = {
            'sku': it['sku'],
            'barcode': it['barcode'],
            'name': it['name'],
            'price': it['price'],
            'disc_price': it['price'] * 0.77,
            'qty': 0,
            'subtotal': 0.0,
            'sources': []
        }
    merged[key]['qty'] += it['qty']
    merged[key]['subtotal'] += it['subtotal']
    merged[key]['sources'].append(f"{it['source']}({it['qty']})")
    # preserve longest name/barcode
    if len(it['name']) > len(merged[key]['name']):
        merged[key]['name'] = it['name']
    if it['barcode'] and len(it['barcode']) > len(merged[key]['barcode']):
        merged[key]['barcode'] = it['barcode']

merged_list = list(merged.values())
# Sort by name
merged_list.sort(key=lambda x: x['name'])

print(f"Merged into {len(merged_list)} distinct products.")
grand_total = sum(x['subtotal'] for x in merged_list)
print(f"Grand Total: ${grand_total:,.2f}")

# Create Excel workbook
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Bella Central 合并发票清单"

# Title header
ws.merge_cells('A1:H1')
ws['A1'] = "Bella Central 采购合并发票清单 (Presupuesto Consolidado)"
ws['A1'].font = Font(name='微软雅黑', size=16, bold=True, color='FFFFFF')
ws['A1'].fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws.row_dimensions[1].height = 40

# Subtitle / Info
ws.merge_cells('A2:H2')
ws['A2'] = f"客户名称: CHEN MINHUANG | 供应商: Bella Central (Mitre 2629 - CABA) | 折扣: 全单77折 (-23.0%) | 商品总款数: {len(merged_list)} 款 | 折后总额: ${grand_total:,.2f} ARS"
ws['A2'].font = Font(name='微软雅黑', size=10, italic=True, color='333333')
ws['A2'].alignment = Alignment(horizontal='center', vertical='center')
ws.row_dimensions[2].height = 24

headers = ['序号', '商品编码 / SKU', '条形码', '商品描述 / 品名', '数量', '网站原单价 (ARS)', '77折后单价 (ARS)', '折后总小计 (ARS)', '出货来源 (批次与数量)']
ws.row_dimensions[3].height = 28

thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

for col_idx, h in enumerate(headers, start=1):
    cell = ws.cell(row=3, column=col_idx, value=h)
    cell.font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
    cell.fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# Write rows
for i, item in enumerate(merged_list, start=1):
    row_num = i + 3
    ws.row_dimensions[row_num].height = 22
    
    r_vals = [
        i,
        item['sku'],
        item['barcode'],
        item['name'],
        item['qty'],
        item['price'],
        item['disc_price'],
        item['subtotal'],
        ", ".join(item['sources'])
    ]
    
    for c_idx, val in enumerate(r_vals, start=1):
        cell = ws.cell(row=row_num, column=c_idx, value=val)
        cell.font = Font(name='微软雅黑', size=10)
        cell.border = thin_border
        
        # Alignments & formats
        if c_idx == 1:
            cell.alignment = Alignment(horizontal='center', vertical='center')
        elif c_idx in (2, 3):
            cell.alignment = Alignment(horizontal='left', vertical='center')
        elif c_idx == 4:
            cell.alignment = Alignment(horizontal='left', vertical='center')
        elif c_idx == 5:
            cell.alignment = Alignment(horizontal='right', vertical='center')
            cell.number_format = '#,##0'
        elif c_idx in (6, 7, 8):
            cell.alignment = Alignment(horizontal='right', vertical='center')
            cell.number_format = '$#,##0.00'
        else:
            cell.alignment = Alignment(horizontal='left', vertical='center')

# Summary row
total_row = len(merged_list) + 4
ws.row_dimensions[total_row].height = 28
ws.cell(row=total_row, column=1, value="合计").alignment = Alignment(horizontal='center', vertical='center')
ws.cell(row=total_row, column=1).font = Font(name='微软雅黑', size=11, bold=True)
ws.cell(row=total_row, column=1).fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')

for c in range(2, 5):
    ws.cell(row=total_row, column=c, value="").fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')

# Sum qty
total_qty = sum(x['qty'] for x in merged_list)
cell_tq = ws.cell(row=total_row, column=5, value=total_qty)
cell_tq.font = Font(name='微软雅黑', size=11, bold=True)
cell_tq.alignment = Alignment(horizontal='right', vertical='center')
cell_tq.fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
cell_tq.number_format = '#,##0'

for c in (6, 7):
    ws.cell(row=total_row, column=c, value="").fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')

cell_ts = ws.cell(row=total_row, column=8, value=grand_total)
cell_ts.font = Font(name='微软雅黑', size=11, bold=True, color='C00000')
cell_ts.alignment = Alignment(horizontal='right', vertical='center')
cell_ts.fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
cell_ts.number_format = '$#,##0.00'

ws.cell(row=total_row, column=9, value="").fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')

# Auto-adjust column widths
col_widths = {1: 8, 2: 18, 3: 22, 4: 40, 5: 10, 6: 18, 7: 18, 8: 20, 9: 35}
for col, width in col_widths.items():
    ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = width

out_excel = r"C:\Users\Administrator\Downloads\Bella_Central_合并发票清单_20261105.xlsx"
wb.save(out_excel)
print(f"Successfully generated Excel: {out_excel}")
