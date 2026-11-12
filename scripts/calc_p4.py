# Page 4 items
p4_items = [
    # L00-L02: SKALA MAYONESA 1000GR, 14625, $4600, *8, $28336
    {"page": 4, "line": "L00-L02", "name": "SKALA MAYONESA 1000GR", "sku": "14625", "price": 4600, "qty": 8, "subtotal": 28336},
    # L03-L05: MaSCARA CAPILARKERATINA27OGFIDELITE, ART/403, $4400, *4, $13552
    {"page": 4, "line": "L03-L05", "name": "MaSCARA CAPILARKERATINA27OGFIDELITE", "sku": "ART/403", "price": 4400, "qty": 4, "subtotal": 13552},
    # L06-L07: MaSCARA CAPILARALMENDRAS27OGFIDELITE, ART/405, $4350, *4, $13398
    {"page": 4, "line": "L06-L07", "name": "MaSCARA CAPILARALMENDRAS27OGFIDELITE", "sku": "ART/405", "price": 4350, "qty": 4, "subtotal": 13398},
    # L08-L10: C*24RUBOREN BARRA RIMERA QUINCE, RQ15, $2200, 48, $81312
    {"page": 4, "line": "L08-L10", "name": "C*24RUBOREN BARRA RIMERA QUINCE", "sku": "RQ15", "price": 2200, "qty": 48, "subtotal": 81312},
    # L11-L13: C*24LABIALEN BARRA MISSBETTY, DD-MIB-K6120, $1250, *72, $69300
    {"page": 4, "line": "L11-L13", "name": "C*24LABIALEN BARRA MISSBETTY", "sku": "DD-MIB-K6120", "price": 1250, "qty": 72, "subtotal": 69300},
    # L14-L16: C*12POLVO TRASLUCIDO MINERAL, RL-F6608, $3000, *36, $83160
    {"page": 4, "line": "L14-L16", "name": "C*12POLVO TRASLUCIDO MINERAL", "sku": "RL-F6608", "price": 3000, "qty": 36, "subtotal": 83160},
    # L17-L19: C*24MASCARA RIMELVOLUMEN TEI8320, TE18320, $2150, *24, $39732
    {"page": 4, "line": "L17-L19", "name": "C*24MASCARA RIMELVOLUMEN TEI8320", "sku": "TE18320", "price": 2150, "qty": 24, "subtotal": 39732},
    # L20-L22: C*21 SWEETHEART Paleta de sombras 9GR City, RL-12270, $4500, *21, $72765
    {"page": 4, "line": "L20-L22", "name": "C*21 SWEETHEART Paleta de sombras 9GR City", "sku": "RL-12270", "price": 4500, "qty": 21, "subtotal": 72765},
    # L23-L25: PRIMERS/ACIDO 11ML, 11ML-PRIMES/ASIDOPSA1, $2400, *10, $18480
    {"page": 4, "line": "L23-L25", "name": "PRIMERS/ACIDO 11ML", "sku": "PSA1", "price": 2400, "qty": 10, "subtotal": 18480},
    # L26-L28: CAJA 12PCSDELINEADOREN FIBRA, DH-LSO5, $5000, *2, $7700
    {"page": 4, "line": "L26-L28", "name": "CAJA 12PCSDELINEADOREN FIBRA", "sku": "DH-LSO5", "price": 5000, "qty": 2, "subtotal": 7700},
    # L29-L31: SOMBRA9COLORESKAPEINE, DD-KPE-YY009028, $2800, *24, $51744
    {"page": 4, "line": "L29-L31", "name": "SOMBRA9COLORESKAPEINE", "sku": "DD-KPE-YY009028", "price": 2800, "qty": 24, "subtotal": 51744},
    # L32-L34: REPUESTO DE AQRUEADOR CHARM LIMIT, CML-802D, $600, *24, $11088
    {"page": 4, "line": "L32-L34", "name": "REPUESTO DE AQRUEADOR CHARM LIMIT", "sku": "CML-802D", "price": 600, "qty": 24, "subtotal": 11088},
    # L35-L37: MASCARILLAFACIAL KAKAZIYAN, KTMMDH509-222, $500, *60, $23100
    {"page": 4, "line": "L35-L37", "name": "MASCARILLAFACIAL KAKAZIYAN", "sku": "DH509-222", "price": 500, "qty": 60, "subtotal": 23100},
    # L38-L40: MASCARILLAFACIAL, DH-BQY40602, $600, *30, $13860
    {"page": 4, "line": "L38-L40", "name": "MASCARILLAFACIAL", "sku": "DH-BQY40602", "price": 600, "qty": 30, "subtotal": 13860},
]

sum_p4 = sum(x['subtotal'] for x in p4_items)
print(f"Page 4 items count: {len(p4_items)}, sum: {sum_p4}")
