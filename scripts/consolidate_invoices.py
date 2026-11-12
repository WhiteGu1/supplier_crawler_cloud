import json

# Ticket 1 (Page 2 + Page 6 + Page 1) -> Stated Total: 1,111,302.50
t1 = [
    {"name": "C*24 ILUMINADOR EN PELOTA", "sku": "DH80145", "barcode": "6972545512963", "price": 1300.0, "qty": 24, "subtotal": 24024.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*12 RUBOR EN POLVO MISSLARA", "sku": "MS-503", "barcode": "6973267331825", "price": 2500.0, "qty": 12, "subtotal": 23100.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*12 MASCARA RIMEL", "sku": "AR1174", "barcode": "6952938488372", "price": 1650.0, "qty": 6, "subtotal": 7623.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*24 ILUMILADOR MISSLARA", "sku": "DH78564", "barcode": "6971680902240", "price": 1100.0, "qty": 24, "subtotal": 20328.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*48 LABIAL ALOE VERA", "sku": "DH76066", "barcode": "6960037160105", "price": 1200.0, "qty": 24, "subtotal": 22176.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*24 Rubor liquido PINKTOUCH", "sku": "CS5580", "barcode": "6952938484626", "price": 1200.0, "qty": 48, "subtotal": 44352.0, "source": "Ticket 1 (Page 2)"},
    {"name": "LABIAL KISS ME MISS BETTY", "sku": "DH75043", "barcode": "6980201723370", "price": 1250.0, "qty": 24, "subtotal": 23100.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*12 RUBOR MAGICO", "sku": "DH80102", "barcode": "6971633381290", "price": 700.0, "qty": 24, "subtotal": 12936.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*12 MASCARA PARA PESTAÑAS", "sku": "CS6754", "barcode": "6952938501613", "price": 1900.0, "qty": 24, "subtotal": 35112.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*24 BASE DE MAQUILLAJE", "sku": "CS3403", "barcode": "6952938456029", "price": 2300.0, "qty": 24, "subtotal": 42504.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*24 CORRECTOR MINI TANGO", "sku": "DH-L272", "barcode": "6902721620724", "price": 1400.0, "qty": 24, "subtotal": 25872.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*24 LABIAL", "sku": "TE18364", "barcode": "6971968516763", "price": 1500.0, "qty": 24, "subtotal": 27720.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*6 SOMBRA PALETA", "sku": "TE18383", "barcode": "6971968516978", "price": 8300.0, "qty": 12, "subtotal": 76692.0, "source": "Ticket 1 (Page 2)"},
    {"name": "C*36 MASCARA MINI TANGO", "sku": "DH80058", "barcode": "6902721681152", "price": 1100.0, "qty": 36, "subtotal": 30492.0, "source": "Ticket 1 (Page 2)"},
    {"name": "BASE DE MAQUILLAJE PINK 21", "sku": "969955", "barcode": "6952938501767", "price": 1900.0, "qty": 24, "subtotal": 35112.0, "source": "Ticket 1 (Page 6)"},
    {"name": "DELINEADOR LIQUIDO", "sku": "DH75114", "barcode": "", "price": 1150.0, "qty": 24, "subtotal": 21252.0, "source": "Ticket 1 (Page 6)"},
    {"name": "BRONZER / CONTORNO", "sku": "DH-GF-GC012-2", "barcode": "6973911280127", "price": 1750.0, "qty": 24, "subtotal": 32340.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*12 LIP GLOSS", "sku": "DH81035", "barcode": "6960660622513", "price": 500.0, "qty": 24, "subtotal": 9240.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*24 LABIAL BARRA 4ANGELS", "sku": "AR1085", "barcode": "6952938485197", "price": 1200.0, "qty": 48, "subtotal": 44352.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*24 LABIAL EN BARRA MISS BETTY", "sku": "DH-K5930", "barcode": "6985948559305", "price": 1100.0, "qty": 24, "subtotal": 20328.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*24 LABIAL EN BARRA MISS BETTY", "sku": "DH-K5927", "barcode": "6985948559275", "price": 1100.0, "qty": 24, "subtotal": 20328.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*24 MASCARA DE PESTANA ARABE", "sku": "DH509-232", "barcode": "6976082022053", "price": 1300.0, "qty": 24, "subtotal": 24024.0, "source": "Ticket 1 (Page 6)"},
    {"name": "SOMBRA KAPEINE 9COLORES", "sku": "DD-KPE-YY009030", "barcode": "6979246740510", "price": 2800.0, "qty": 24, "subtotal": 51744.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*24 CORRECTOR LIQUIDO", "sku": "DD-MIB-F6431", "barcode": "6985948564316", "price": 1600.0, "qty": 24, "subtotal": 29568.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*24 MASCARA RIMEL VOLUMEN TEI8320", "sku": "TE18320", "barcode": "6971968516008", "price": 2150.0, "qty": 24, "subtotal": 39732.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*24 MASCARA DE PESTANIA", "sku": "AR1152", "barcode": "6952938486569", "price": 1450.0, "qty": 72, "subtotal": 80388.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*24 MASCARA DE PESTANA MISS BETTY", "sku": "DH-M6610", "barcode": "6921582105331", "price": 1400.0, "qty": 48, "subtotal": 51744.0, "source": "Ticket 1 (Page 6)"},
    {"name": "AGUA MICELAR CITY", "sku": "RL-F6658", "barcode": "6928609066583", "price": 3500.0, "qty": 8, "subtotal": 21560.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*24 RUBOR LABIO 2IN1 GEGEBEAR", "sku": "GGBE-550", "barcode": "GX1236", "price": 1600.0, "qty": 12, "subtotal": 14784.0, "source": "Ticket 1 (Page 6)"},
    {"name": "C*24 DELINEADOR LIQUIDO", "sku": "DD-MIB-E1381", "barcode": "6985948513819", "price": 1500.0, "qty": 24, "subtotal": 27720.0, "source": "Ticket 1 (Page 1)"},
    {"name": "PALETA DE MAQUILLAJE", "sku": "DH-YDM-LK29691", "barcode": "6973162296915", "price": 19000.0, "qty": 3, "subtotal": 43890.0, "source": "Ticket 1 (Page 1)"},
    {"name": "PALETA SOMBRA 9COLORES", "sku": "DH-JZD-EYE-0927", "barcode": "6920250809274", "price": 2900.0, "qty": 12, "subtotal": 26796.0, "source": "Ticket 1 (Page 1)"},
    {"name": "MASCARILLA FACIAL", "sku": "DH-BQY42576", "barcode": "6942349742576", "price": 600.0, "qty": 36, "subtotal": 16632.0, "source": "Ticket 1 (Page 1)"},
    {"name": "PACK*15 ACEITE CUTICULA NAEZ", "sku": "BC1322ACEITE", "barcode": "6982604313226/ACEITE", "price": 12750.0, "qty": 1, "subtotal": 9817.5, "source": "Ticket 1 (Page 1)"},
    {"name": "PEGAMENTO PARA TIPS 5PCS NAEZ", "sku": "DD2977", "barcode": "6982604329777", "price": 1600.0, "qty": 60, "subtotal": 73920.0, "source": "Ticket 1 (Page 1)"},
]

# Ticket 2 (Image 2 + Image 1) -> Stated Total: 583,814.00
t2 = [
    {"name": "PRESS GEL LÍQUIDO CHERIMOYA", "sku": "CH030", "barcode": "7805250300008", "price": 6000.0, "qty": 18, "subtotal": 83160.0, "source": "Ticket 2"},
    {"name": "ULTRABOND CHERIMOYA", "sku": "CH045", "barcode": "7805250450017", "price": 6000.0, "qty": 24, "subtotal": 110880.0, "source": "Ticket 2"},
    {"name": "SEMI CITY GIRL 10ML 甲油胶", "sku": "GJ-3013", "barcode": "6935810010915", "price": 1800.0, "qty": 60, "subtotal": 83160.0, "source": "Ticket 2"},
    {"name": "Colección de 8 Colores Efecto Aurora", "sku": "RQ-ES01-08-09", "barcode": "6907654108097", "price": 2800.0, "qty": 24, "subtotal": 51744.0, "source": "Ticket 2"},
    {"name": "ULTRABOND PRIMER 10ML", "sku": "PX2438", "barcode": "6931240613092", "price": 2800.0, "qty": 12, "subtotal": 25872.0, "source": "Ticket 2"},
    {"name": "MELY COLOR (ESMALTE SEMI MELY)", "sku": "MY860000", "barcode": "", "price": 2500.0, "qty": 5, "subtotal": 9625.0, "source": "Ticket 2"},
    {"name": "KIT DE PERFUME + CREMA CORPORAL", "sku": "YT2574", "barcode": "6930107010494", "price": 10000.0, "qty": 2, "subtotal": 15400.0, "source": "Ticket 2"},
    {"name": "PRIMER CON ACIDO CHERIMOYA", "sku": "CH046", "barcode": "", "price": 3300.0, "qty": 16, "subtotal": 40656.0, "source": "Ticket 2"},
    {"name": "SEMI VIA LACTEA CHARM LIMIT", "sku": "DH86044", "barcode": "7772686885082/VIA LACTE", "price": 1300.0, "qty": 14, "subtotal": 14014.0, "source": "Ticket 2"},
    {"name": "SEMI NEGRO CHARM LIMIT", "sku": "DH86043", "barcode": "7772686885082/NEGRO", "price": 1300.0, "qty": 14, "subtotal": 14014.0, "source": "Ticket 2"},
    {"name": "SEMI ROJO NAVIDAD", "sku": "DH89013", "barcode": "7772686790133", "price": 1700.0, "qty": 24, "subtotal": 31416.0, "source": "Ticket 2"},
    {"name": "REMOVEDOR PARA UÑAS 100ML", "sku": "FC-RA100 75776", "barcode": "656750775776", "price": 2600.0, "qty": 12, "subtotal": 24024.0, "source": "Ticket 2"},
    {"name": "MELY COLOR (ESMALTE SEMI MELY)", "sku": "MY860000", "barcode": "", "price": 2500.0, "qty": 7, "subtotal": 13475.0, "source": "Ticket 2"},
    {"name": "营养油 NAVI (91518-ACEITE CUTICULAR)", "sku": "91518", "barcode": "", "price": 2050.0, "qty": 6, "subtotal": 9471.0, "source": "Ticket 2"},
    {"name": "CHERIMOYA (REMOVEDOR DEL CUTICUL)", "sku": "CH014", "barcode": "", "price": 1900.0, "qty": 6, "subtotal": 8778.0, "source": "Ticket 2"},
    {"name": "PEGAMENTO PARA TIPS 5PCS NAEZ", "sku": "DD2977", "barcode": "6982604329777", "price": 1600.0, "qty": 12, "subtotal": 14784.0, "source": "Ticket 2"},
    {"name": "PEGAMENTO DE UÑA NAEZ", "sku": "DD2913", "barcode": "6982604329135", "price": 1050.0, "qty": 36, "subtotal": 29106.0, "source": "Ticket 2"},
    {"name": "MASCARILLA TEI MMTEI", "sku": "K3086/K3082K/3080", "barcode": "6978882330161", "price": 550.0, "qty": 10, "subtotal": 4235.0, "source": "Ticket 2"},
]

# Page 4 (Ticket 3)
p4 = [
    {"name": "SKALA MAYONESA 1000GR", "sku": "14625", "barcode": "897042012329", "price": 4600.0, "qty": 8, "subtotal": 28336.0, "source": "Page 4 (Ticket 3)"},
    {"name": "MASCARA CAPILAR KERATINA 270G FIDELITE", "sku": "ART/403", "barcode": "7798135961190", "price": 4400.0, "qty": 4, "subtotal": 13552.0, "source": "Page 4 (Ticket 3)"},
    {"name": "MASCARA CAPILAR ALMENDRAS 270G FIDELITE", "sku": "ART/405", "barcode": "7798135961213", "price": 4350.0, "qty": 4, "subtotal": 13398.0, "source": "Page 4 (Ticket 3)"},
    {"name": "C*24 RUBOR EN BARRA RIMERA QUINCE", "sku": "RQ15", "barcode": "6930249995079", "price": 2200.0, "qty": 48, "subtotal": 81312.0, "source": "Page 4 (Ticket 3)"},
    {"name": "C*24 LABIAL EN BARRA MISS BETTY", "sku": "DD-MIB-K6120", "barcode": "6985948561209", "price": 1250.0, "qty": 72, "subtotal": 69300.0, "source": "Page 4 (Ticket 3)"},
    {"name": "C*12 POLVO TRASLUCIDO MINERAL", "sku": "RL-F6608", "barcode": "6928609066088", "price": 3000.0, "qty": 36, "subtotal": 83160.0, "source": "Page 4 (Ticket 3)"},
    {"name": "C*24 MASCARA RIMEL VOLUMEN TEI8320", "sku": "TE18320", "barcode": "6971968516008", "price": 2150.0, "qty": 24, "subtotal": 39732.0, "source": "Page 4 (Ticket 3)"},
    {"name": "C*21 SWEETHEART Paleta de sombras City", "sku": "RL-12270", "barcode": "6930110405614", "price": 4500.0, "qty": 21, "subtotal": 72765.0, "source": "Page 4 (Ticket 3)"},
    {"name": "PRIMER S/ACIDO 11ML", "sku": "PSA1", "barcode": "", "price": 2400.0, "qty": 10, "subtotal": 18480.0, "source": "Page 4 (Ticket 3)"},
    {"name": "CAJA 12PCS DELINEADOR EN FIBRA", "sku": "DH-LSO5", "barcode": "8972423632101", "price": 5000.0, "qty": 2, "subtotal": 7700.0, "source": "Page 4 (Ticket 3)"},
    {"name": "SOMBRA 9COLORES KAPEINE", "sku": "DD-KPE-YY009028", "barcode": "6979246740367", "price": 2800.0, "qty": 24, "subtotal": 51744.0, "source": "Page 4 (Ticket 3)"},
    {"name": "REPUESTO DE AQRUEADOR CHARM LIMIT", "sku": "CML-802D", "barcode": "6959598488025", "price": 600.0, "qty": 24, "subtotal": 11088.0, "source": "Page 4 (Ticket 3)"},
    {"name": "MASCARILLA FACIAL KAKAZIYAN", "sku": "DH509-222", "barcode": "KTMMDH509-222", "price": 500.0, "qty": 60, "subtotal": 23100.0, "source": "Page 4 (Ticket 3)"},
    {"name": "MASCARILLA FACIAL", "sku": "DH-BQY40602", "barcode": "6942349740602", "price": 600.0, "qty": 30, "subtotal": 13860.0, "source": "Page 4 (Ticket 3)"},
]

# Page 5 items
p5 = [
    {"name": "PEGAMENTO PARA UNAS NAEZ", "sku": "DD2913", "barcode": "6982604329135", "price": 1050.0, "qty": 36, "subtotal": 29106.0, "source": "Page 5"},
    {"name": "PERFILADOR*3 CITY GIRL", "sku": "MD-003NUEVO", "barcode": "6931240715048", "price": 800.0, "qty": 60, "subtotal": 36960.0, "source": "Page 5"},
    {"name": "POLVO ESPEJO*6", "sku": "SP6245", "barcode": "6932024016245", "price": 2200.0, "qty": 12, "subtotal": 20328.0, "source": "Page 5"},
    {"name": "U?as Postizas Press On Decoradas", "sku": "BC1795", "barcode": "6982604317958", "price": 1900.0, "qty": 24, "subtotal": 35112.0, "source": "Page 5"},
    {"name": "TOALLA MELY", "sku": "MY891005", "barcode": "6974488910059", "price": 1700.0, "qty": 24, "subtotal": 31416.0, "source": "Page 5"},
    {"name": "MASCARILLA TEI MMTEI", "sku": "K3086/K3082K/3080", "barcode": "6978882330161", "price": 550.0, "qty": 20, "subtotal": 8470.0, "source": "Page 5"},
]

all_items = t1 + t2 + p4 + p5
print(f"Total raw items: {len(all_items)}")
total_subtotal = sum(x['subtotal'] for x in all_items)
print(f"Total subtotal: {total_subtotal:,.2f}")
print(f"Total list price: {total_subtotal / 0.77:,.2f}")
