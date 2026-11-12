# Ticket 1 items
t1_items = [
    # Page 6
    {"line": "L00", "sku": "969955", "barcode": "6952938501767", "price": 1900, "qty": 24, "subtotal": 35112},
    {"line": "L02", "sku": "DH75114", "barcode": "", "price": 1150, "qty": 24, "subtotal": 21252},
    {"line": "L04", "sku": "DH-GF-GC012-2", "barcode": "6973911280127", "price": 1750, "qty": 24, "subtotal": 32340},
    {"line": "L05", "sku": "DH81035", "barcode": "6960660622513", "name": "C*12 LIP GLOSS", "price": 500, "qty": 24, "subtotal": 9240},
    {"line": "L07", "sku": "AR1085", "barcode": "6952938485197", "name": "C*24LABIALBARRA 4ANGELS", "price": 1200, "qty": 48, "subtotal": 44352},
    {"line": "L08", "sku": "DH-K5930", "barcode": "6985948559305", "name": "C*24LABIALEN BARRA MISS BETTY", "price": 1100, "qty": 24, "subtotal": 20328},
    {"line": "L10", "sku": "DH-K5927", "barcode": "6985948559275", "name": "C*24LABIALEN BARRA", "price": 1100, "qty": 24, "subtotal": 20328},
    {"line": "L12", "sku": "DH509-232", "barcode": "6976082022053", "name": "C*24 MASCARA DEPESTANAARABE", "price": 1300, "qty": 24, "subtotal": 24024},
    {"line": "L14", "sku": "DD-KPE-YY009030", "barcode": "6979246740510", "name": "SOMBRA KAPEINE9COLORES", "price": 2800, "qty": 24, "subtotal": 51744},
    {"line": "L16", "sku": "DD-MIB-F6431", "barcode": "6985948564316", "name": "C*24CORRECTORLIQUIDO", "price": 1600, "qty": 24, "subtotal": 29568},
    {"line": "L19", "sku": "TE18320", "barcode": "6971968516008", "name": "C*24MASCARA RIMELVOLUMEN TEI8320", "price": 2150, "qty": 24, "subtotal": 39732},
    {"line": "L22", "sku": "AR1152", "barcode": "6952938486569", "name": "C*24 MASCARA DEPESTANIA", "price": 1450, "qty": 72, "subtotal": 80388},
    {"line": "L25", "sku": "DH-M6610", "barcode": "6921582105331", "name": "C*24MASCARA DEPESTANA MISS BETTY", "price": 1400, "qty": 48, "subtotal": 51744},
    {"line": "L28", "sku": "RL-F6658", "barcode": "6928609066583", "name": "AGUA MICELAR CITY", "price": 3500, "qty": 8, "subtotal": 21560},
    {"line": "L31", "sku": "GX1236 / GGBE-550", "barcode": "", "name": "C*24RUBORLABIO 2IN1 GEGEBEAR", "price": 1600, "qty": 12, "subtotal": 14784},
    # Page 1
    {"line": "L01", "sku": "DD-MIB-E1381", "barcode": "6985948513819", "name": "C*24DELINEADORLIQUIDO", "price": 1500, "qty": 24, "subtotal": 27720},
    {"line": "L04", "sku": "DH-YDM-LK29691", "barcode": "6973162296915", "name": "PALETA DEMAQUILLAJE", "price": 19000, "qty": 3, "subtotal": 43890},
    {"line": "L07", "sku": "DH-JZD-EYE-0927", "barcode": "6920250809274", "name": "PALETA SOMBRA 9COLORES", "price": 2900, "qty": 12, "subtotal": 26796},
    {"line": "L10", "sku": "DH-BQY42576", "barcode": "6942349742576", "name": "MASCARILLA FACIAL", "price": 600, "qty": 36, "subtotal": 16632},
    {"line": "L13", "sku": "BC1322ACEITE", "barcode": "6982604313226/ACEITE", "name": "PACK*15 ACEITE CUTICULA NAEZ", "price": 12750, "qty": 1, "subtotal": 9817.5},
    {"line": "L16", "sku": "DD2977", "barcode": "6982604329777", "name": "PEGAMENTO PARA TIPS SPCS NAEZ", "price": 1600, "qty": 60, "subtotal": 73920},
]

total = sum(x['subtotal'] for x in t1_items)
print(f"Ticket 1 calculated subtotal sum: {total}")
print(f"Ticket 1 stated total on receipt: 1111302.50")
print(f"Difference: {1111302.50 - total}")
