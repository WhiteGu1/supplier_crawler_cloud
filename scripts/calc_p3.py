# Page 3 items
p3_items = [
    # L00-L03: PRESS GEL LIQUIDO CHERIMOYA, CH030, $6000, 18, $83160
    {"page": 3, "line": "L00-L03", "name": "PRESS GEL LIQUIDO CHERIMOYA", "sku": "CH030", "price": 6000, "qty": 18, "subtotal": 83160},
    # L04-L05: ULTRABOND CHERIMOYA, CH045, $6000, *24, $110880
    {"page": 3, "line": "L04-L05", "name": "ULTRABOND CHERIMOYA", "sku": "CH045", "price": 6000, "qty": 24, "subtotal": 110880},
    # L06-L08: CG-1091 GJ-3013, $1800, 60, $83160
    {"page": 3, "line": "L06-L08", "name": "CG-1091 GJ-3013", "sku": "GJ-3013", "price": 1800, "qty": 60, "subtotal": 83160},
    # L09-L10: RQ-ES01-08-09, $2800, *24, $51744
    {"page": 3, "line": "L09-L10", "name": "RQ-ES01-08-09", "sku": "RQ-ES01-08-09", "price": 2800, "qty": 24, "subtotal": 51744},
    # L11-L13: ULTRABOND PRIMER 10ML, PX2438, $2800, *12, $25872
    {"page": 3, "line": "L11-L13", "name": "ULTRABOND PRIMER 10ML", "sku": "PX2438", "price": 2800, "qty": 12, "subtotal": 25872},
    # L14-L16: ESMALTE SEMI MELY, MY860000, $2500, 5, $9625
    {"page": 3, "line": "L14-L16", "name": "ESMALTE SEMI MELY", "sku": "MY860000", "price": 2500, "qty": 5, "subtotal": 9625},
    # L17-L19: KIT DE PERFUME+ CREMA CORRORAL, YT2574, $10000, *2, $15400
    {"page": 3, "line": "L17-L19", "name": "KIT DE PERFUME+ CREMA CORRORAL", "sku": "YT2574", "price": 10000, "qty": 2, "subtotal": 15400},
    # L20-L22: PRIMER CON ACIDO CHERIMOYA, CH046, $3300, *16, $40656
    {"page": 3, "line": "L20-L22", "name": "PRIMER CON ACIDO CHERIMOYA", "sku": "CH046", "price": 3300, "qty": 16, "subtotal": 40656},
    # L23-L25: SEMI VIA LACTEA CHARM LIMIT, DH86044, $1300, *14, $14014
    {"page": 3, "line": "L23-L25", "name": "SEMI VIA LACTEA CHARM LIMIT", "sku": "DH86044", "price": 1300, "qty": 14, "subtotal": 14014},
    # L26-L28: SEMI NEGRO CHARM LIMIT, DH86043/NEGRO, $1300, *14, $14014
    {"page": 3, "line": "L26-L28", "name": "SEMI NEGRO CHARM LIMIT", "sku": "DH86043", "price": 1300, "qty": 14, "subtotal": 14014},
    # L29-L31: SEMI ROJO NAVINAD, DH89013, $1700, *24, $31416
    {"page": 3, "line": "L29-L31", "name": "SEMI ROJO NAVINAD", "sku": "DH89013", "price": 1700, "qty": 24, "subtotal": 31416},
    # L32-L34: REMOVEDORPARA UNAS 100ML, FC-RA10075776, $2600, *12, $24024
    {"page": 3, "line": "L32-L34", "name": "REMOVEDORPARA UNAS 100ML", "sku": "FC-RA10075776", "price": 2600, "qty": 12, "subtotal": 24024},
]

sum_p3 = sum(x['subtotal'] for x in p3_items)
print(f"Page 3 items count: {len(p3_items)}, sum: {sum_p3}")
