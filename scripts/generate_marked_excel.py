import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from parse_all_5_xls import all_tickets

orig_path = r'C:\Users\Administrator\Downloads\Bella_Central_合并发票清单_20261105.xlsx'
new_path = r'C:\Users\Administrator\Downloads\Bella_Central_合并发票清单_20261106_最新完整版.xlsx'

wb_orig = openpyxl.load_workbook(new_path)
ws_orig = wb_orig["原发票68项(仅标记淡蓝)"]

# Read original 68 items from the 10-column sheet
orig_rows = []
for r in range(4, 72):  # rows 4 to 71 are 序号 1 to 68
    seq = int(ws_orig.cell(r, 1).value)
    sku = ws_orig.cell(r, 3).value
    bc = ws_orig.cell(r, 4).value
    name = ws_orig.cell(r, 5).value
    qty = int(ws_orig.cell(r, 6).value)
    price = float(ws_orig.cell(r, 7).value)
    disc_p = float(ws_orig.cell(r, 8).value)
    sub = float(ws_orig.cell(r, 9).value)
    src = ws_orig.cell(r, 10).value

    orig_rows.append({
        'seq': seq,
        'sku': sku,
        'barcode': bc,
        'name': name,
        'qty': qty,
        'price': price,
        'disc_price': disc_p,
        'subtotal': sub,
        'source': src,
        'completed': (seq not in (2, 17))
    })

# Parse 55555.xls (all_tickets[4]) and merge internal duplicates within 55555.xls
t5_merged = {}
for it in all_tickets[4]['items']:
    key = (it['sku'].strip(), it['price'])
    n1 = it['name_line1']
    b2 = it['barcode_or_line2']
    if key not in t5_merged:
        t5_merged[key] = {
            'sku': it['sku'],
            'barcode': b2,
            'name': n1,
            'price': float(it['price']),
            'disc_price': float(it['price']) * 0.77,
            'qty': 0,
            'subtotal': 0.0,
            'sources': []
        }
    t5_merged[key]['qty'] += it['qty']
    t5_merged[key]['subtotal'] += float(it['subtotal'])
    t5_merged[key]['sources'].append(f"55555.xls/子单4({it['qty']})")

# Newly verified SKUs in 55555.xls:
# 90: R120/LASVARANO (30)
# 91: DH86030 (24)
# 94: CML-060C LIMA MINI (12)
# 97: DH70539 JSZYJ (12)
# 107: SFD017 (12)
# 108: BC1121 (24)
# 109: SFD012MBFD / 6932024017716 (12)
# 110: SFD010XJWOFD (12)
# 111: BC1116 (12)
# 114: DD3079 (5 packs * 12 = 60 pcs)
newly_completed_seqs = {90, 91, 94, 97, 107, 108, 109, 110, 111, 114}

new_rows = []
next_seq = 69
for k, v in t5_merged.items():
    note_src = ", ".join(v['sources'])
    if v['sku'] == 'RL-F6608':
        note_src += " [注:序号7已有36件,加上本单12件共48件]"
    elif v['sku'] == 'K3086/K3082K/3080':
        note_src += " [注:序号43已有30件,加上本单30件共60件]"
    elif v['sku'] == 'DD3079':
        note_src += " [5包×12个=60个,已核对一致]"
    elif v['sku'] == 'DD3080':
        note_src += " [⚠️实收6包(72个),小票扫了6+1=7包(84个),多收1包]"
    elif v['sku'] == 'BC1127':
        note_src += " [⚠️待核对:您报了19247(12个),小票开的是BC1127(12个)]"
    new_rows.append({
        'seq': next_seq,
        'sku': v['sku'],
        'barcode': v['barcode'],
        'name': v['name'],
        'qty': v['qty'],
        'price': v['price'],
        'disc_price': v['disc_price'],
        'subtotal': v['subtotal'],
        'source': note_src,
        'completed': (next_seq in newly_completed_seqs)
    })
    next_seq += 1

all_combined = orig_rows + new_rows

def build_sheet(ws, rows_data, title_str):
    ws.merge_cells('A1:J1')
    grand_total = sum(x['subtotal'] for x in rows_data)
    done_cnt = sum(1 for x in rows_data if x['completed'])
    todo_cnt = len(rows_data) - done_cnt

    ws['A1'] = title_str
    ws['A1'].font = Font(name='微软雅黑', size=15, bold=True, color='FFFFFF')
    ws['A1'].fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 38

    ws.merge_cells('A2:J2')
    ws['A2'] = f"客户: CHEN MINHUANG | 总计: ${grand_total:,.2f} ARS | 淡蓝色(已完成): {done_cnt} 项 | 白色未填充(待处理): {todo_cnt} 项"
    ws['A2'].font = Font(name='微软雅黑', size=10, bold=True, color='1F4E78')
    ws['A2'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[2].height = 24

    headers = ['序号', '状态', '商品编码 / SKU', '条形码 / 规格', '商品描述 / 品名', '数量', '网站原单价 (ARS)', '77折后单价 (ARS)', '折后总小计 (ARS)', '出货来源与核对备注']
    ws.row_dimensions[3].height = 28

    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'),
        right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'),
        bottom=Side(style='thin', color='BFBFBF')
    )

    light_blue_fill = PatternFill(start_color='DDEBF7', end_color='DDEBF7', fill_type='solid')
    white_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')

    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.font = Font(name='微软雅黑', size=10, bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    for i, item in enumerate(rows_data, start=1):
        row_num = i + 3
        ws.row_dimensions[row_num].height = 22
        status_txt = "已完成" if item['completed'] else "待处理"
        r_vals = [
            item['seq'],
            status_txt,
            item['sku'],
            item['barcode'],
            item['name'],
            item['qty'],
            item['price'],
            item['disc_price'],
            item['subtotal'],
            item['source']
        ]
        row_fill = light_blue_fill if item['completed'] else white_fill
        for c_idx, val in enumerate(r_vals, start=1):
            cell = ws.cell(row=row_num, column=c_idx, value=val)
            cell.font = Font(name='微软雅黑', size=10, bold=(not item['completed'] and c_idx in (1, 2, 3)))
            cell.border = thin_border
            cell.fill = row_fill
            if c_idx in (1, 2):
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif c_idx in (3, 4, 5, 10):
                cell.alignment = Alignment(horizontal='left', vertical='center')
            elif c_idx == 6:
                cell.alignment = Alignment(horizontal='right', vertical='center')
                cell.number_format = '#,##0'
            elif c_idx in (7, 8, 9):
                cell.alignment = Alignment(horizontal='right', vertical='center')
                cell.number_format = '$#,##0.00'

    total_row = len(rows_data) + 4
    ws.row_dimensions[total_row].height = 28
    sum_fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')
    for c in range(1, 11):
        cell = ws.cell(row=total_row, column=c, value="")
        cell.fill = sum_fill
        cell.border = thin_border
        cell.font = Font(name='微软雅黑', size=11, bold=True)

    ws.cell(row=total_row, column=1, value="总计").alignment = Alignment(horizontal='center', vertical='center')

    tot_qty = sum(x['qty'] for x in rows_data)
    c_qty = ws.cell(row=total_row, column=6, value=tot_qty)
    c_qty.alignment = Alignment(horizontal='right', vertical='center')
    c_qty.number_format = '#,##0'

    c_sub = ws.cell(row=total_row, column=9, value=grand_total)
    c_sub.font = Font(name='微软雅黑', size=11, bold=True, color='C00000')
    c_sub.alignment = Alignment(horizontal='right', vertical='center')
    c_sub.number_format = '$#,##0.00'

    col_widths = {1: 8, 2: 10, 3: 24, 4: 24, 5: 42, 6: 10, 7: 16, 8: 16, 9: 18, 10: 48}
    for col, width in col_widths.items():
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = width

wb_out = openpyxl.Workbook()
ws1 = wb_out.active
ws1.title = "合并发票清单(含新单+淡蓝标记)"
build_sheet(ws1, all_combined, "Bella Central 采购合并发票清单 (已核对项标记淡蓝色)")

ws2 = wb_out.create_sheet(title="原发票68项(仅标记淡蓝)")
build_sheet(ws2, orig_rows, "Bella Central 原合并发票 (除序号2、17外均已填充淡蓝色)")

for p in [
    orig_path,
    new_path,
    r'C:\Users\Administrator\Downloads\Bella_Central_合并发票清单_20261106_核对更新版.xlsx'
]:
    try:
        wb_out.save(p)
        print(f"Saved: {p}")
    except PermissionError:
        print(f"Skipped (currently open in Excel): {p}")
print(f"Completed count: {sum(1 for x in all_combined if x['completed'])} / {len(all_combined)}")
