# Ticket 2 items: Page 5 + Page 7
t2_items = [
    # Page 5
    {"line": "L03", "sku": "DD2913", "barcode": "6982604329135", "price": 1050, "qty": 36, "subtotal": 29106},
    {"line": "L06", "sku": "MD-003NUEVO", "barcode": "6931240715048", "name": "PERFILADOR*3CITY GIRL", "price": 800, "qty": 60, "subtotal": 36960},
    {"line": "L08", "sku": "SP6245", "barcode": "6932024016245", "name": "POLVO ESPEJO*6", "price": 2200, "qty": 12, "subtotal": 20328},
    {"line": "L11", "sku": "BC1795", "barcode": "6982604317958", "name": "U?as Postizas Press On", "price": 1900, "qty": 24, "subtotal": 35112},
    {"line": "L14", "sku": "MY891005", "barcode": "6974488910059", "name": "TOALLA MELY", "price": 1700, "qty": 24, "subtotal": 31416},
    {"line": "L17", "sku": "K3086/K3082K/3080", "barcode": "6978882330161", "name": "MASCARILLA TEI MMTEI", "price": 550, "qty": 20, "subtotal": 8470},
    # Page 7
    {"line": "L01", "sku": "MY860000", "barcode": "", "name": "ESMALTE SEMI MELY", "price": 2500, "qty": 7, "subtotal": 13475},
    {"line": "L04", "sku": "91518", "barcode": "", "name": "ACEITE CUTICULAR NAVI", "price": 2050, "qty": 6, "subtotal": 9471},
    {"line": "L07", "sku": "CH014", "barcode": "", "name": "REMOVEDOR DE CUTICULA CHERIMOYA", "price": 1900, "qty": 6, "subtotal": 8778},
    {"line": "L09", "sku": "DD2977", "barcode": "6982604329777", "name": "PEGAMENTO PARA TIPS", "price": 1600, "qty": 12, "subtotal": 14784},
    {"line": "L12", "sku": "DD2913", "barcode": "6982604329135", "name": "PEGAMENTO DE UNA NAEZ", "price": 1050, "qty": 36, "subtotal": 29106},
    {"line": "L15", "sku": "K3086/K3082K/3080", "barcode": "6978882330161", "name": "MASCARILLA TEI", "price": 550, "qty": 10, "subtotal": 4235},
]

total = sum(x['subtotal'] for x in t2_items)
print(f"Ticket 2 calculated subtotal sum: {total}")
print(f"Ticket 2 stated total on receipt: 583814.00")
print(f"Difference: {583814.00 - total}")
