# -*- coding: utf-8 -*-
"""
Trapoman 剩余2919条商品自动分类脚本 - MySQL版本
"""
import re
import sys
import io
import pymysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'admin123',
    'database': 'supplier_crawler',
    'charset': 'utf8mb4',
}

def classify(name):
    """根据商品名称判断分类"""
    n = name.upper().strip()
    
    # === 马黛茶具/保温瓶 → 餐饮用品 ===
    if any(k in n for k in ['MATE', 'BOMBILLA', 'TERMO', 'MATERO', 'SORBETE', 'BOMBI ', 'AUTOCERBANTE', 'AUTOCEBANTE']):
        return '餐饮用品'
    
    # NOTE: 婴儿/儿童用品规则已移到后面，让具体品类规则优先
    # 但先处理 BACINILLA, SILLON INFANTIL, CHUPETE 等明确非餐具的婴儿用品
    if any(k in n for k in ['BACINILLA', 'REDUCTOR TAPA INODORO', 'SILLON INFANTIL',
                              'VALIJITA INFANTIL', 'CHUPETE BABYS']):
        return '其他'
    # 儿童餐具杯瓶 → 餐饮用品
    if any(k in n for k in ['MAMADERA', 'MAMADERAS']):
        return '餐饮用品'
    
    # === 杯/壶/瓶 → 餐饮用品 ===
    if any(k in n for k in ['VASO ', 'COPA', 'JARRA', 'JARRO', 'BOTELLA', 'TAZA', 'CHOP', 'CHOPP',
                              'PACK X3 VASOS', 'PACK VASO', 'DECANTER', 'HIELERA', 'FRAPERA',
                              'TACITA', 'TAZON', 'JARRITO', 'TETERA', 'MUG ',
                              'BOTELLON', 'CANTIMPLORA', 'CHIQUITA DEPORTIVA',
                              'REVOLVEDOR TRAGO', 'SET ESPRESSO', 'LATTE',
                              'IRISH', 'HIELERITAS', 'BOTELLITA', 'VASITO',
                              'SET DE VASOS']):
        return '餐饮用品'
    if n.startswith('VASO') or n.startswith('COPA') or n.startswith('JARRA') or n.startswith('JARRO'):
        return '餐饮用品'
    if n.startswith('TAZA') or n.startswith('CHOP') or n.startswith('TACITA') or n.startswith('TAZON'):
        return '餐饮用品'
    if 'BOTELLA' in n and 'MASCOTA' not in n:
        return '餐饮用品'
    
    # === 厨房炊具（锅、模具、烤盘、炊具工具） ===
    if any(k in n for k in ['CACEROLA', 'OLLA', 'SARTEN', 'BIFERA', 'PANQUEQUERA', 'WAFFLERA', 
                              'CARLITERA', 'PAVA', 'HERVIDOR', 'PIZZERA', 'TARTERA', 'MOLDE',
                              'ASADERA', 'BUDINERA', 'PASTAFROLA', 'TORTERA', 'SAVARIN',
                              'PLACA BROWNIE', 'BATERIA', 'FREIDORA', 'CAFETERA',
                              'PROVOLETERA', 'PARRILLA', 'BRASERO', 'CHURRERA',
                              'MOLINILLO', 'MANDOLINA', 'MANDOLIN ',
                              'RALLADOR', 'EXPRIMIDOR', 'CORTADOR', 'PICADOR',
                              'EMBUDO', 'COLADOR', 'COLAPASTA', 'COLACALDO',
                              'BATIDOR', 'ESPUMADERA', 'CUCHARON',
                              'ESPATULA', 'PALA ', 'PINZA', 'ABRELATA', 'SACACORCHO',
                              'PELAPAP', 'PISAPAPA', 'AFILADOR', 'AFILA',
                              'SOPAPA', 'DESTAPADOR', 'PICADORA', 'PRENSA',
                              'BATE ', 'BATEBIFE', 'MARTILLO', 'PALO DE AMASAR',
                              'TABLA ', 'TABLITA', 'CORTA PIZZA', 'CORTA QUESO',
                              'CORTA HUEVO', 'AHUECA',
                              'REPULGADORA', 'MOLDE ', 'TOSTADOR', 'POCHOCLERA',
                              'DIFUSOR DE CALOR', 'MANOPLA SILICONA', 'MANOPLA +',
                              'AGARRADERA SILICONA', 'SET CAROL SILICONA',
                              'UTENSILLO', 'UTENSILIOS', 'PALITOS BROCHETE',
                              'CUCHARA ', 'SEPARADOR CLARA', 'SEPARADOR HUEVO',
                              'DISPENSADORA DE HUEVOS', 'CONTENEDOR DE HUEVOS',
                              'TUPPER PARA QUESO', 'ÑOQUERA',
                              'WOK', 'CONJUNTO FREIDOR', 'ASADOR',
                              'PIZZETAS', 'CORTANTE', 'ESPAGUETERO',
                              'JUEGO TABLAS', 'JUEGO CHURRASCO',
                              'TAPA SILICONA', 'MORTERO', 'SERVILLETERO',
                              'PINCEL', 'FILTRO CAFE', 'KIN KIN',
                              'MARCA VASOS', 'PINCHE', 'DESPOLVILLADOR',
                              'SILICONE UTENSILLS', 'REDONDO RECTO', 'FLAUTA']):
        return '厨房炊具'
    if n.startswith('MOLDE') or n.startswith('TOSTADOR') or n.startswith('RALLADOR'):
        return '厨房炊具'
    if n.startswith('CUCHARA') and 'MEDIDOR' not in n:
        return '厨房炊具'
    if 'PAPEL FREIDORA' in n or 'PAPEL GASTRONOMICO' in n:
        return '厨房炊具'
    if 'CUCHILLA' in n or 'CUCHILLO' in n or 'HACHUELA' in n:
        return '厨房炊具'
    if 'SET TABLAS' in n or 'SET 3 TABLAS' in n:
        return '厨房炊具'
    
    # === 厨房餐具（碗盘刀叉勺） ===
    if any(k in n for k in ['PLATO', 'BOWL ', 'CUCHARITA', 'TENEDOR', 'CUCHARA DE', 'CUBIERTO',
                              'CUBIERTOS', 'ENSALADERA', 'COMPOTERA', 'COMPOTERITA',
                              'FUENTE', 'CAZUELA', 'BANDEJA',
                              'SET VAJILLA', 'VAJILLA', 'MELAMINA',
                              'PLATITO', 'LUMINARC', 'DURAX',
                              'NADIR', 'MARINEX', 'OPALINE', 'BOL ',
                              'JARRA VIDRIO', 'SET 5 PIEZAS', 'BOWLS',
                              'PUTINA', 'DURALEX', 'CRISA',
                              'FUENTON', 'COPETINERO', 'FRUTERA', 'PANERA',
                              'CEREALERO', 'BOLS ', 'SALAD', 'ACEITERA',
                              'BANDEJITA', 'PARTY SET', 'SALSA DIP',
                              'FRUIT BASKET', 'PALILLERO']):
        return '厨房餐具'
    if n.startswith('PLATO') or n.startswith('BOWL') or n.startswith('TENEDOR'):
        return '厨房餐具'
    if n.startswith('CUCHARITA') or n.startswith('CUBIERTO') or n.startswith('ENSALADERA'):
        return '厨房餐具'
    if n.startswith('BANDEJA') or n.startswith('FUENTE') or n.startswith('COMPOTERA'):
        return '厨房餐具'
    if n.startswith('BOL '):
        return '厨房餐具'
    
    # === 厨房储物（保鲜盒、密封罐、储物容器） ===
    if any(k in n for k in ['TUPPER', 'HERMETICO', 'CONTENEDOR', 'RECIPIENTE',
                              'FIAMBRERA', 'TAPER', 'LUNCH BOX',
                              'TARRO', 'FRASCO', 'POTE ', 'AZUCARERA',
                              'YERBERA', 'STORAGE', 'FUNBOX', 'STYLE BOX',
                              'COZZONI BOX', 'TRENDY BOX', 'TUFFEX',
                              'KEEPING', 'FOOD STORAGE', 'ORGANIZADOR HERMETICO',
                              'KIT ORGANIZADOR', 'ESPECIERO', 'SALSERO',
                              'MOSTACERO', 'ACEITERO', 'PIMENTERO', 'SALERO',
                              'ADEREZO', 'QUESERA', 'MANTEQUERA', 'CARAMELERA',
                              'CONTENEDORCITO', 'SET X 2 ACRILICO', 'SET SAN REMO',
                              'SET X 3 CUADRADO', 'SET X 3 RECTANGULAR',
                              'SET X 5 CUADRADO', 'SET X 5 RECTANGULAR',
                              'VERTEDOR', 'YERBERO', 'YERBERITOS', 'AZUCARERO',
                              'CUBETERA', 'HELADOS', 'CONGELANTE', 'FLANERITA',
                              'ENVASE SILUETA', 'JUEGO YERBA', 'CUBITO',
                              'SET REDONDO VIDRIO PASTEL', 'SAL FINA']):
        return '厨房储物'
    if n.startswith('HERMETICO') or n.startswith('CONTENEDOR') or n.startswith('RECIPIENTE'):
        return '厨房储物'
    if n.startswith('TUPPER') or n.startswith('TAPER') or n.startswith('FIAMBRERA'):
        return '厨房储物'
    if n.startswith('FRASCO') or n.startswith('TARRO') or n.startswith('POTE'):
        return '厨房储物'
    if n.startswith('LUNCH') or n.startswith('VIANDA') or n.startswith('LONCHERA') or n.startswith('MARMITA'):
        return '餐饮用品'
    if 'TUPPER SANDWICH' in n:
        return '厨房储物'
    if 'SET INICIO' in n or 'BLISTER FRIEND' in n:
        return '餐饮用品'
    
    # === 清洁用品 ===
    if any(k in n for k in ['BALDE', 'TRAPO', 'MOPA', 'FRANELA', 'PAÑO', 'PANO ',
                              'ESCOBILLA', 'ESCOBITA', 'ESCOBILLON', 'CEPILLO',
                              'ESPONJA', 'FIBRA', 'ESTROPAJO', 'ROLLITO LANA',
                              'GUANTE', 'LIMPIA', 'PLUMERO', 'CABO EXTENSIBLE',
                              'CABO MADERA', 'PALA ', 'LAMPAZO', 'SECADOR',
                              'SECAMAX', 'SECAPILI', 'REJILLA', 'SOPAPA',
                              'BOLSA VERDE', 'BOLSA RESIDUO', 'BOLSA CONSORCIO',
                              'BOLSA EN ROLLITO', 'BOLSA LAVARROPAS',
                              'ROCIADOR', 'PULVERIZADOR', 'ENVASE SPRAY',
                              'CAJA ANTIPOLILLA', 'GUANTES', 'TOALLITA',
                              'REPASADOR', 'CEPILLITO']):
        return '清洁用品'
    if n.startswith('BALDE') or n.startswith('ESCOBILL') or n.startswith('CEPILLO'):
        return '清洁用品'
    if n.startswith('ESPONJA') or n.startswith('TRAPO') or n.startswith('PAÑO'):
        return '清洁用品'
    if n.startswith('MOPA') or n.startswith('FRANELA') or n.startswith('PALA'):
        return '清洁用品'
    if n.startswith('LIMPIA') or n.startswith('PLUMERO') or n.startswith('GUANTE'):
        return '清洁用品'
    if n.startswith('REJILLA') or n.startswith('ROCIADOR') or n.startswith('PULVERIZADOR'):
        return '清洁用品'
    if n.startswith('REPASADOR') or n.startswith('TOALLITA'):
        return '清洁用品'
    
    # === 收纳整理 ===
    if any(k in n for k in ['TACHO', 'CESTO', 'PAPELERO', 'VAIVEN', 'BIN ',
                              'TRASH', 'BOLSO', 'ORGANIZADOR', 'PERCHA', 'PERCHERO',
                              'PERCHITA', 'ESTANTE', 'ZAPATERO', 'CHANGO',
                              'CARRO ', 'CANASTO', 'CAJONCITO', 'BAUL',
                              'CAJA DE HERRAMIENTAS', 'ALFAJERO', 'ESCURRIDOR',
                              'SECAPLATO', 'ESCURRE', 'PORTA', 'COLGADOR',
                              'BANQUITO', 'BANQUETA', 'SILLA', 'MESA ',
                              'ESQUINERO', 'MULTIESTANTE', 'CASITA ALAMBRE',
                              'DUCHERO', 'TACHO ', 'BOLSA GRANDE FERIA',
                              'MORRAL', 'REDUCTOR TAPA',
                              'PERCHERO', 'GANCHITO', 'PERCHERITO', 'GANCHO',
                              'TABLA DE LAVAR', 'CHANGO DE COMPRAS',
                              'CONSERVADORA', 'ORGANIZADOR DE', 'STORAGE BASKET',
                              'HANGING BASKET', 'CANASTO DE TELA', 'CANASTITA',
                              'CAJITA', 'SET BAÑO',
                              'BATH SET', 'DISPENSER', 'JABONERA', 'PORTA ROLLO',
                              'PORTA CEPILLO', 'PORTA CUBIERTOS', 'TAPON BACHA',
                              'TAPON REJILLA', 'TAPON CIEGO', 'TAPON UNIVERSAL',
                              'BARRAL', 'TOPE ', 'TOPES ', 'TRABA PUERTA',
                              'NECESER', 'TACHITO', 'CAJA MODENA', 'CAJA BROAD',
                              'CAJA LOVE', 'CAJA CON RUEDAS', 'CAJA CERRI',
                              'CAJA GIGANTE RATAN', 'CAJA SIMIL', 'CAJON YUTE',
                              'CAJONERA', 'BATEA', 'CAJA ', 'CANASTA ',
                              'CANASTITO', 'PEN HOLDER']):
        return '收纳整理'
    if n.startswith('TACHO') or n.startswith('CESTO') or n.startswith('PAPELERO'):
        return '收纳整理'
    if n.startswith('PERCHA') or n.startswith('ESTANTE') or n.startswith('ZAPATERO'):
        return '收纳整理'
    if n.startswith('ORGANIZADOR') or n.startswith('CANASTO') or n.startswith('CANASTITA'):
        return '收纳整理'
    if n.startswith('PORTA') or n.startswith('SECAPLATO') or n.startswith('ESCURRE'):
        return '收纳整理'
    if n.startswith('BARRAL') or n.startswith('JABONERA'):
        return '卫浴用品'
    if n.startswith('TACHITO'):
        return '收纳整理'
    
    # === 卫浴用品 ===
    if any(k in n for k in ['CORTINA', 'DUCHA', 'JABONERA', 'TOALLA',
                              'ESPEJO', 'ALFOMBRA BAÑO', 'ALFOMBRA GOMA BAÑO',
                              'ALFOMBRA PATITAS', 'ALFOMBRA PIEDRAS',
                              'ANTIDESLIZANTE', 'ANTI SAPOS', 'SOPORTE CELULAR',
                              'TIRA PARA BAÑERAS', 'TIRAS PARA ESCALERA',
                              'BURLETE', 'SET BAÑO', 'BATH SET',
                              'DISPENSER DETERGENTE', 'CORTINA CORTISAN',
                              'CORTINA SIMPLE', 'CORTINA NYLON', 'PROTECTOR 40',
                              'GANCHO P/ CORTINA', 'COFIA',
                              'PORTA CEPILLO', 'ESPONJA BAÑO', 'MINI ESPONJITA DE BAÑO',
                              'CEPILLO BOL SANITARIO', 'CEPILLO BAÑO',
                              'WC BRUSH', 'BOL SANITARIO', 'POSA JABON',
                              'SET X4 BAÑO']):
        return '卫浴用品'
    
    # === 装饰品 ===
    if any(k in n for k in ['VELA', 'VELON', 'VELITA', 'MACETA', 'FLORERO',
                              'ALFOMBRA', 'MANTEL', 'INDIVIDUAL', 'TABLE COVER',
                              'APOYA VASO', 'POSA FUENTE', 'CUADRO',
                              'DECORATORTA', 'DECOC', 'ADORN', 'ANTORCHA',
                              'BENGALAS', 'ANTORCHITAS', 'DIFUSOR AROMATIZANTE',
                              'SAHUMERIO', 'ESENCIAS HORNILLOS', 'ESPEJO REDONDO',
                              'ESPEJO EN CAJITA', 'MIRROR', 'CAMPANA',
                              'ALFOMBRA SHAGGY',
                              'ALFOMBRA ECO', 'ALFOMBRA HOME', 'ALFOMBRA LANA',
                              'ALFOMBRA DECO', 'ALFOMBRA KIDS', 'ALFOMBRA NAVIDAD',
                              'ALFOMBRA MASCOTA', 'ALFOMBRA ANIMAL', 'ALFOMBRA GOMA',
                              'ALFOMBRA PELUCHE', 'ALFOMBRA BATH', 'ALFOMBRA ',
                              'POSAPLATO', 'POSATAPA', 'MACETITA']):
        return '装饰品'
    if n.startswith('ALFOMBRA') or n.startswith('VELA') or n.startswith('VELON') or n.startswith('VELITA'):
        return '装饰品'
    if n.startswith('MACETA') or n.startswith('MANTEL') or n.startswith('INDIVIDUAL'):
        return '装饰品'
    if n.startswith('ESPEJO') and 'LUZ LED' not in n:
        return '装饰品'
    
    # === 美妆个护 ===
    if any(k in n for k in ['MAKEUP', 'COSMETIC', 'ORGANIZADOR MAQUILLAJE',
                              'ESPONJA CORPORAL', 'MAQUILLAJE', 'PEINE',
                              'GOMITAS', 'ALHAJERO', 'PARASOL']):
        return '美妆个护'
    
    # === 玩具游戏 ===
    if any(k in n for k in ['BLOQUE MAGNETICO', 'SET POKE', 'JUGUETE',
                              'PELOTA', 'DADO', 'ROMPECABEZA', 'PUZZLE']):
        return '玩具游戏'
    
    # === 宠物用品 ===
    if any(k in n for k in ['MASCOTA', 'COMEDERO', 'BEBEDERO', 'CORREA',
                              'BOLSITA PARA MASCOTA', 'CEPILLO PELO MASCOTA',
                              'CEPILLO MASAJEADOR', 'CEPILLO DIENTES MASCOTA',
                              'JUGUETE AVOCADO', 'PALITA SANITARIA',
                              'BANDEJA SANITARIA', 'GALLINA CON', 'DISPENSER PARA BOLSITA',
                              'COMEDERO DOBLE', 'COMEDERO OVAL', 'COMEDERO METAL',
                              'COMEDERO GATO', 'COMEDERO HUESO', 'COMEDERO TRANSPORTABLE',
                              'BOTELLA MASCOTA', 'TERMINATOR CEPILLO']):
        return '宠物用品'
    if 'BEBEDERO MASCOTA' in n:
        return '宠物用品'
    
    # === 电器电子 ===
    if any(k in n for k in ['HUMIDIFICADOR', 'FREIDORA AIRE', 'ESTUFA',
                              'VENTILADOR', 'BATIDOR CAFE A PILA', 'PIMENTERO ELECTRICO',
                              'AFILACUCHILLOS', 'AFILADOR 3 EN 1',
                              'LINTERNA', 'LED ', 'LUZ LED', 'ENCENDEDOR CHISPERO USB',
                              'STEREO']):
        return '电器电子'
    
    # === 文具办公 ===
    if any(k in n for k in ['SET ESCOLAR', 'LAPIZ', 'GOMA', 'CUADERNO', 'LIBRETA',
                              'MARCAT', 'RESALTADOR', 'BOLIGRAFO', 'FIBRON',
                              'PEGAMENTO', 'TIJERA', 'COMPAS', 'REGLA',
                              'CARPETA', 'ARCHIVADOR']):
        return '文具办公'
    
    # === 派对用品 ===
    if any(k in n for k in ['GLOBOS', 'GLOBO', 'SERPENTINA', 'CONFETI',
                              'VELA CUMPLEAÑOS', 'DECORACION', 'GIRANDOLA',
                              'PICARDIC', 'COTILLON', 'COTILLÓN']):
        return '派对用品'
    
    # === 个人防护 ===
    if any(k in n for k in ['BOLSA DE AGUA CALIENTE', 'PROTECTOR ', 'TAPON PARA EL OIDO',
                              'BARBIJO', 'TAPABOCA', 'GUANTE ANTICORTE']):
        return '个人防护'
    
    # === 日用百货 ===
    if any(k in n for k in ['PASTILLERO', 'CIERRA BOLSA', 'CINTA EMBALAR',
                              'CURITA', 'HISOPOS', 'ESCARBADIENTE',
                              'PAPEL ALUMINIO', 'PAPEL MANTECA', 'PAPEL FILM',
                              'FILM ', 'ALUMINIO ', 'GUANTES POLIETILENO',
                              'COMEDERO METAL',
                              'BANQUITO PLEGABLE', 'BANQUETA DESESPLAST',
                              'BANQUETA RATAN', 'BANQUETA NEGRA', 'BANQUETA BLANCA',
                              'MESA RATAN', 'SILLA RATAN', 'VERDULERO',
                              'ALMOHADON', 'CUBRE SILLAS', 'BANQUITO TINY',
                              'PARASOL', 'CAJA DE HERRAMIENTAS',
                              'JUEGO DE HERRAMIENTAS', 'SET CHICO DE HERRAMIENTAS',
                              'BANQUETA CERRI', 'CAJA RECT', 'TUBO GUARDA',
                              'CHANGO DE COMPRAS',
                              'SOLDADOR', 'RECARGA GAS', 'PERFUMERO',
                              'GATILLO', 'REGADERA', 'FUMIGADOR', 'BARRE HOJAS',
                              'MAQUINA DE FLIT', 'CERCO JARDIN', 'PORTA BOLS',
                              'CALDERO', 'MENSULA', 'GANCHO CULTIVO',
                              'REPUESTO', 'TAPON STANLEY', 'TAPON MATE',
                              'TAPON TERMO', 'TAPON CON PICO', 'FILTRO BOMBILLA',
                              'LIMPIA BOMBILLA', 'TAPON ', 'TAPITA',
                              'TAPA CON NOMBRES', 'TORNILLO CLIKER',
                              'TAPON VERTEDOR', 'TAPON SILICONA',
                              'TAPON BOTELLA', 'TAPON CORONA', 'TAPON FIGURAS',
                              'TAPON PARA VINO', 'TAPA CONDIMENTOS',
                              'CIERRA BOLSAS', 'BROCHE HARAGAN',
                              'BOLSA DE AGUA CALIENTE',
                              'ALFOMBRA GOMA BENABI', 'PEINE RASTRILLO',
                              'ENCENDEDOR CHISPERO USB']):
        return '日用百货'
    
    # === 其他（防虫网、打火机等） ===
    if any(k in n for k in ['BICHO RED', 'MOSQUITERO', 'CORTINA ANTIMOSCA',
                              'APARATO P/ MOSQUITOS', 'PALMETA MATA',
                              'CHISPERO', 'ENCENDEDOR', 'TORCH', 'MEGA ',
                              'MAGIC BOX', 'LAUNDRY', 'TOMAS DE',
                              'AUTOADHESIVO', 'TOPETINA', 'PROTECTORES AUTOADHESIVOS',
                              'GANCHO GRANDE DORADO', 'GANCHITOS PLATEADOS',
                              'PERCHERITO METALIZADO', 'BROCHE HARAGAN',
                              'FILTRO UNIVERSAL', 'TAPON UNIVERSAL',
                              'BLOQUE MAGNETICO', 'PELATODO', 'NEO PISA',
                              'PISA PURE', 'DESCAROZADOR', 'ROMPE NUEZ',
                              'PELA NARANJAS', 'ENRULADOR', 'CORTA RAVIOL',
                              'UNTADOR', 'PISTOLA DECORADORA',
                              'FERNETROMETRO', 'CENTRIFUGADOR', 'CENTRIFUGA',
                              'LAVA VERDURAS', 'OMELETERA', 'TOMA LLUVIA',
                              'FILTRO PILETA', 'TAPA P/ PILETA',
                              'HILO SISAL', 'HILO YUTE', 'HILO ATA-ME',
                              'SOAP VOCE', 'BIDON', 'AUTOMATICO DESESPLAST',
                              'RODILLO QUITA PELUSAS', 'TENDER', 'PACK PVC',
                              'Modifica Descripcion', 'MANTECA 5MTS',
                              'BARRE HOJA', 'ECOBOLSA',
                              'ACEITE PARA HORNILLO', 'CHUPETE BABYS',
                              'BAÑERA', 'SEPARADOR MULTIUSO', 'REPASAD']):
        return '其他'
    # BACINILLA, REDUCTOR TAPA INODORO, SILLON INFANTIL → 其他
    if any(k in n for k in ['BACINILLA', 'REDUCTOR TAPA INODORO', 'SILLON INFANTIL',
                              'VALIJITA INFANTIL']):
        return '其他'
    
    # === 工具 → 其他 ===
    if any(k in n for k in ['HERRAMIENTAS', 'SOPORTE CELULAR']):
        return '其他'
    
    # 默认
    return '其他'


def main():
    # 读取文件
    products = []
    with open(r'D:\projects\supplier_crawler\trapoman_remaining.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t', 1)
            if len(parts) == 2:
                pid = int(parts[0])
                name = parts[1]
                products.append((pid, name))
    
    print(f"总计 {len(products)} 条商品待分类")
    
    # 分类
    results = []
    unclassified = []
    for pid, name in products:
        cat = classify(name)
        results.append((pid, name, cat))
        if cat == '其他':
            unclassified.append((pid, name))
    
    # 统计
    from collections import Counter
    counter = Counter(cat for _, _, cat in results)
    print("\n分类统计:")
    for cat, count in counter.most_common():
        print(f"  {cat}: {count}")
    
    print(f"\n未明确分类(其他): {len(unclassified)} 条")
    if unclassified:
        print("前30条未分类商品:")
        for pid, name in unclassified[:30]:
            print(f"  {pid}\t{name}")
    
    # 写入MySQL数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    updated = 0
    for pid, name, cat in results:
        cursor.execute(
            "UPDATE products SET category = %s WHERE id = %s AND supplier_id = 3",
            (cat, pid)
        )
        updated += cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"\n数据库更新完成: {updated}/{len(results)} 条记录已更新")
    
    # 输出结果文件
    with open(r'D:\projects\supplier_crawler\trapoman_classify_results.csv', 'w', encoding='utf-8') as f:
        f.write("id,name,category\n")
        for pid, name, cat in results:
            f.write(f'{pid},"{name}",{cat}\n')
    
    print(f"结果已保存到 trapoman_classify_results.csv")


if __name__ == '__main__':
    main()
