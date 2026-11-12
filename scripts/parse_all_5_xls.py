import os
import pandas as pd
import re

folder = r'C:\Users\Administrator\Downloads\xls'

def parse_xls_ticket(fpath, fname):
    df = pd.read_excel(fpath, header=None)
    items = []
    ticket_name = ""
    compra_id = ""
    total_pagar = 0.0
    
    # scan rows
    i = 0
    n = len(df)
    while i < n:
        c0 = str(df.iloc[i, 0]).strip() if pd.notna(df.iloc[i, 0]) else ""
        c2 = str(df.iloc[i, 2]).strip() if pd.notna(df.iloc[i, 2]) else ""
        c4 = str(df.iloc[i, 4]).strip() if pd.notna(df.iloc[i, 4]) else ""
        c5 = str(df.iloc[i, 5]).strip() if pd.notna(df.iloc[i, 5]) else ""
        c6 = str(df.iloc[i, 6]).strip() if pd.notna(df.iloc[i, 6]) else ""
        
        if c0.startswith("COMPRA"):
            compra_id = c0
        if c0.startswith("<") and c0.endswith(">"):
            ticket_name = c0
        if "TOTAL PAGAR" in c2:
            m = re.search(r'收款合计([\d\.]+)', c2)
            if m:
                total_pagar = float(m.group(1))
                
        # Check if this row is the barcode/discount/price row of an item (c4 == '0.77')
        if c4 == '0.77' and i >= 2 and i + 1 < n:
            name_row = str(df.iloc[i-2, 0]).strip() if pd.notna(df.iloc[i-2, 0]) else ""
            barcode = c0
            price_str = c6.replace('$', '').strip()
            price = float(price_str)
            
            sku = str(df.iloc[i+1, 0]).strip() if pd.notna(df.iloc[i+1, 0]) else ""
            qty_str = str(df.iloc[i+1, 5]).replace('*', '').strip() if pd.notna(df.iloc[i+1, 5]) else "0"
            qty = int(float(qty_str))
            sub_str = str(df.iloc[i+1, 6]).replace('$', '').strip() if pd.notna(df.iloc[i+1, 6]) else "0"
            subtotal = float(sub_str)
            
            # Wait: in 2222222.xls, some items have 3 lines of description/name/sku!
            # e.g., R36: MELY COLOR, R38: ESMALTE SEMI MELY | 0.77 | $2500, R39: MY860000 | *5 | $9625
            # Let's check if name_row is brand and barcode is actually sub-name!
            items.append({
                'file': fname,
                'row': i,
                'name_line1': name_row,
                'barcode_or_line2': barcode,
                'sku': sku,
                'price': price,
                'qty': qty,
                'subtotal': subtotal
            })
            i += 2
            continue
        i += 1
        
    return {
        'file': fname,
        'compra_id': compra_id,
        'ticket_name': ticket_name,
        'total_pagar': total_pagar,
        'items': items,
        'calc_sum': sum(x['subtotal'] for x in items)
    }

all_tickets = []
for fname in sorted(os.listdir(folder)):
    if fname.endswith('.xls'):
        res = parse_xls_ticket(os.path.join(folder, fname), fname)
        all_tickets.append(res)
        print(f"{fname}: {res['ticket_name']} | {res['compra_id']} | items={len(res['items'])} | stated={res['total_pagar']} | calc={res['calc_sum']}")

# Check overlaps between 55555.xls and 11111..444444.xls
t1_to_4_skus = set()
for t in all_tickets[:4]:
    for it in t['items']:
        t1_to_4_skus.add((it['sku'], it['price']))

print("\nChecking 55555.xls items against 11111-444444:")
for idx, it in enumerate(all_tickets[4]['items'], 1):
    overlap = (it['sku'], it['price']) in t1_to_4_skus
    mark = " [OVERLAP!]" if overlap else ""
    print(f"  {idx:02d}. SKU:{it['sku']} | BC:{it['barcode_or_line2']} | P:{it['price']} | Q:{it['qty']} | Sub:{it['subtotal']} | {it['name_line1']}{mark}")
