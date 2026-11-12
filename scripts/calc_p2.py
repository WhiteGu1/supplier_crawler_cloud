# Let's inspect Page 2, 3, 4 items from lines_clean.txt

# Page 2:
p2_items = [
    # L00-L02: C*24 ILUMINADOREN PELOTA, DH80145, $1300, *24, $24024
    {"page": 2, "line": "L00-L02", "name": "C*24 ILUMINADOREN PELOTA", "sku": "DH80145", "price": 1300, "qty": 24, "subtotal": 24024},
    # L03: MS-503 | 6973267331825 | *0.77 | *12 | $23100 | $2500
    {"page": 2, "line": "L03", "name": "C*12RUBOR EN POLVO MISSLARA", "sku": "MS-503", "price": 2500, "qty": 12, "subtotal": 23100},
    # L04-L06: C*12MASCARA RIMEL, AR1174, $1650, *6, $7623
    {"page": 2, "line": "L04-L06", "name": "C*12MASCARA RIMEL", "sku": "AR1174", "price": 1650, "qty": 6, "subtotal": 7623},
    # L07-L09: C*24ILUMILADORMISSLARA, DH78564, $1100, *24, $20328
    {"page": 2, "line": "L07-L09", "name": "C*24ILUMILADORMISSLARA", "sku": "DH78564", "price": 1100, "qty": 24, "subtotal": 20328},
    # L10-L12: C*48LABIALALOEVERA, DH76066QOIDENROSE, $1200, *24, $22176
    {"page": 2, "line": "L10-L12", "name": "C*48LABIALALOEVERA", "sku": "DH76066", "price": 1200, "qty": 24, "subtotal": 22176},
    # L13-L15: C*24Rubor liquido PINKTOUCH, CS5580, $1200, *48, $44352
    {"page": 2, "line": "L13-L15", "name": "C*24Rubor liquido PINKTOUCH", "sku": "CS5580", "price": 1200, "qty": 48, "subtotal": 44352},
    # L16-L18: LABIALKISS MEMISS BETTY, DH75043, $1250, *24, $23100
    {"page": 2, "line": "L16-L18", "name": "LABIALKISS MEMISS BETTY", "sku": "DH75043", "price": 1250, "qty": 24, "subtotal": 23100},
    # L19-L21: C*12RUBORMAGICO, DH80102, $700, *24, $12936
    {"page": 2, "line": "L19-L21", "name": "C*12RUBORMAGICO", "sku": "DH80102", "price": 700, "qty": 24, "subtotal": 12936},
    # L22-L24: C*12MASCARAPARAPESTANL, CS6754, $1900, *24, $35112
    {"page": 2, "line": "L22-L24", "name": "C*12MASCARAPARAPESTANL", "sku": "CS6754", "price": 1900, "qty": 24, "subtotal": 35112},
    # L25-L27: C*24BASE DE MAQUILLAJE, CS3403, $2300, *24, $42504
    {"page": 2, "line": "L25-L27", "name": "C*24BASE DE MAQUILLAJE", "sku": "CS3403", "price": 2300, "qty": 24, "subtotal": 42504},
    # L28-L30: C*24 CORRECTOR MINI TANGO, DH-L272, $1400, *24, $25872
    {"page": 2, "line": "L28-L30", "name": "C*24 CORRECTOR MINI TANGO", "sku": "DH-L272", "price": 1400, "qty": 24, "subtotal": 25872},
    # L31-L33: C*24LABIAL, TE18364, $1500, *24, $27720
    {"page": 2, "line": "L31-L33", "name": "C*24LABIAL", "sku": "TE18364", "price": 1500, "qty": 24, "subtotal": 27720},
    # L34-L36: C*6 sombra paleta, TE18383, $8300, *12, $76692
    {"page": 2, "line": "L34-L36", "name": "C*6 sombra paleta", "sku": "TE18383", "price": 8300, "qty": 12, "subtotal": 76692},
    # L37-L39: C*36MASCARA MINI TANGO, DH80058, $1100, *36, $30492
    {"page": 2, "line": "L37-L39", "name": "C*36MASCARA MINI TANGO", "sku": "DH80058", "price": 1100, "qty": 36, "subtotal": 30492},
]

sum_p2 = sum(x['subtotal'] for x in p2_items)
print(f"Page 2 items count: {len(p2_items)}, sum: {sum_p2}")
