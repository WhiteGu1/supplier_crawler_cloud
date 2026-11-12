"""
三级分类重构：基于商品名称关键词，将二级分类细分为三级
格式: 一级 > 二级 > 三级

策略:
1. 用商品名称关键词匹配，将每个二级分类下的商品分到更细的三级
2. 匹配不到的保留在二级（不加三级）
"""
import pymysql, sys, re
sys.stdout.reconfigure(encoding='utf-8')

# 三级分类规则: (关键词正则列表, 三级分类名)
# 按二级分类分组，每个二级分类下定义三级规则
RULES = {
    # ===== 厨房用品 =====
    "厨房用品 > 餐具": [
        (r"TAZA|TAZAS|SET DE TAZA", "茶杯杯子"),
        (r"VASO|VASOS|VASO TERMICO|VASO TERM", "玻璃杯/保温杯"),
        (r"PLATO|PLATOS|SET DE PLATO", "盘子"),
        (r"CUBIERTO|CUCHARA|CUCHARAS|TENEDOR|TENEDORES|CUCHILLO|CUCHILLOS|PELADOR", "刀叉勺"),
        (r"BANDEJA|BANDEJAS", "托盘"),
        (r"MANTEL|CAMINO DE MESA|INDIVIDUAL", "桌布餐垫"),
        (r"BROCHE|PINZA", "夹子"),
        (r"ESCURRIDOR|ESCURRIDORA", "沥水架"),
        (r"PRECINTO|PRECINTOS", "封口夹"),
    ],
    "厨房用品 > 炊具": [
        (r"MOLDE|MOLDES|SILICONA|CUBETERA", "模具/烤模"),
        (r"RALLADOR|RALLADORA|EXPRIMIDOR", "刨丝器/榨汁器"),
        (r"COLADOR|COLADORA", "滤网/漏勺"),
        (r"SARTEN|BIFERA|PANQUEQUERA|PAELLERA|OLEO", "平底锅/煎锅"),
        (r"Olla|OLLA|Cacerola|CACEROLA|CAZO|CASSEROLE", "汤锅/炖锅"),
        (r"TAPA|TAPAS", "锅盖"),
        (r"TABLA|TABLAS", "砧板"),
        (r"ABRIRLATAS|ABRELATAS|SACACORCHO|DESCORCHADOR", "开瓶器/开罐器"),
        (r"BATIDOR|BATIDORA|MEZCLADOR|CUCHARON|CUCHARONES|ESPATULA|ESPÁTULA|ESCURIDOR", "烹饪工具"),
        (r"TERMOMETRO|TERMÓMETRO", "厨房温度计"),
        (r"Gas|Encendedor|Anafe|Brochete|Cepillo neumatico", "炉具配件"),
    ],
    "厨房用品 > 储物保鲜": [
        (r"TAPER|TUPPER|CONTENEDOR|FRASCO|LATA|YERBERA|MANTEQUERA|CARAMELERA|HUEVERA", "保鲜盒/储物罐"),
        (r"BOLSA|BOLSAS|ALIMENTOS", "食品袋"),
        (r"CUBETERA", "冰格"),
        (r"LUNCHERA|LONCHERA", "便当盒/午餐盒"),
    ],
    "厨房用品 > 餐饮水具": [
        (r"BOTELLA|BOTELLAS|DEPORTIVA", "水瓶/水壶"),
        (r"TERMO|TERMICA|TÉRMICO|TÉRMICA", "保温壶/保温杯"),
        (r"CAFETERA|CAFETERO|CAFÉ", "咖啡器具"),
        (r"BOMBILLA|CEBADOR|SACACORCHO|TAPON|CEBADOR", "茶饮配件"),
        (r"Encendedor|Cocina|Palito|Brochete|Cepillo dental|Jabali", "厨房工具"),
    ],
    "厨房用品 > 食品饮料": [
        (r"Alcohol", "酒精"),
        (r"TAZA|Taza", "杯子"),
    ],

    # ===== 文具 =====
    "文具 > 文具办公": [
        (r"BOLIGRAFO|BOLÍGRAFO|LAPIZ|LÁPIZ|LAPIcera|PLUMA|ESFERO", "笔类"),
        (r"MARCADOR|MARCADORES|TEXTMARKER|RESALTADOR|HIGHLIGHTER", "马克笔/荧光笔"),
        (r"CUADERNO|ANOTADOR|LIBRO|PLANIFICADOR|AGENDA|FOLDER|CARPETA|ARCHIVADOR", "本册/文件夹"),
        (r"GOMA|GOMA DE BORRAR|BORRADOR", "橡皮擦"),
        (r"SACAPUNTAS|SACA PUNTAS|AFILADOR", "卷笔刀"),
        (r"CORRECTOR|CORRECCION", "修正工具"),
        (r"PORTALAPICES|PORTALÁPICES|LAPICERO|ESTUCHE|CARTUCHERA", "笔筒/笔袋"),
        (r"REGLA|REGLAS|ESCUADRA|COMPAS|COMPÁS|TRANSPORTADOR", "尺规"),
        (r"TIJERA|TIJERAS", "剪刀"),
        (r"STICKERS|STICKER|HOJAS ATRAPA|ETIQUETA|ETIQUETAS", "贴纸/标签"),
        (r"PEGAMENTO|ADHESIVO|GLUE|CINTA ADHESIVA|TAPE", "胶水/胶带"),
        (r"COLOREAR|CRAYON|LAPICES DE COLOR|COLORES", "绘画用品"),
    ],

    # ===== 玩具 =====
    "玩具 > 玩具游戏": [
        (r"PELUCHE|PELUCHES|PELUCHE", "毛绒玩具"),
        (r"ROMPECABEZA|ROMPECABEZAS|PUZZLE|PUZZLE", "拼图"),
        (r"JUEGO DE MESA|JUEGO DE TABLERO|AJEDREZ|DAMAS|DOMINO|DOMINÓ", "桌游"),
        (r"ENCASTRE|BLOQUE|BLOQUES|PIEZA|PIEZAS|CONSTRUCCION|CONSTRUCCIÓN|ARMAR|ARMADO", "积木/拼装"),
        (r"EDUCATIVO|DIDACTICO|DIDÁCTICO|TABLERO DE JUEGO|APRENDER", "益智玩具"),
        (r"POP.?IT|SPINER|SPINNER|FIDGET", "解压玩具"),
        (r"STICKERS?|STICKER|LIBRO DE STICKERS", "贴纸书"),
        (r"VEHICULO|VEHÍCULO|COCHE|CARRITO|AUTOMOVIL|AUTOMÓVIL|MOTOCICLETA|MOTO|AVION|AVIÓN", "玩具车"),
        (r"PELOTA|BALON|PELOTAS", "玩具球"),
        (r"DISFRAZ|DISFRAZAR|CASA DE JUEGO|COCINITA|COCINA DE JUGUETE|JUGUETE DE", "角色扮演"),
        (r"INSTRUMENTO|GUITARRA|PIANO|TAMBOR|BATERIA|BATERÍA|MUSICAL", "音乐玩具"),
        (r"JUGUETE|JUGUETES|DOLL|MUÑECA|MUÑECAS|BEBE|BEBÉ", "其他玩具"),
    ],

    # ===== 摆件礼品 =====
    "摆件礼品 > 装饰摆件": [
        (r"MACETA|MACETAS|PLANTA|PLANTAS|FLOR|FLORES", "花盆/植物"),
        (r"ADORNO|ADORNOS|DECORATIVO|COLGANTE|DECORACION|DECORACIÓN", "装饰摆件"),
        (r"MARCO|FOTOS|FOTO|PORTARETRATO", "相框"),
        (r"ALFOMBRA|ALFOMBRAS", "地毯/地垫"),
        (r"CESTO|CESTA|CESTAS|CANASTO|CANASTA", "收纳篮"),
        (r"DESPERTADOR|RELOJ|RELOJES", "时钟"),
        (r"HUMIDIFICADOR|DIFUSOR|AROMA", "香薰/加湿器"),
        (r"ORGANIZADOR|ORGANIZADORA", "收纳整理"),
        (r"MANTA|COJIN|COJÍN|ALMOHADON|ALMOHADÓN", "毯子/抱枕"),
        (r"ESPEJO|ESPEJOS", "镜子"),
    ],
    "摆件礼品 > 派对节庆": [
        (r"ARBOL|ÁRBOL|NAVIDAD|NAVIDEÑ|NAVIDEÑO|PAPA NOEL|SANTA|RENO|GUIRNALDA", "圣诞装饰"),
        (r"HALLOWEEN|BRUJA|MURCIELAGO|MURCIÉLAGO|ARAÑA|CALABAZA|ESQUELETO|DISFRAZ", "万圣节"),
        (r"LED|TIRA LED|LUZ|LUCES|LAMPARA|LÁMPARA", "节庆灯饰"),
        (r"VELA|VELAS|GIRANDOLA|PIÑATA|GLOBOS|GLOBO", "派对用品"),
    ],
    "摆件礼品 > 季节商品": [
        (r"PISCINA|PILETA|INFLABLE|SURF|AGUA|PLAYA|PELOTA DE PLAYA", "夏季/水上"),
        (r"GORRO|BUFANDA|CUELLO|GUANTES|GORRO CON|OREJERAS|AGUA CALIENTE|CALENTADOR|INVIERNO", "冬季保暖"),
        (r"VELA AROMATICA|AROMA", "香薰"),
    ],

    # ===== 家居生活 =====
    "家居生活 > 收纳整理": [
        (r"CESTO|CESTA|CANASTO|CANASTA", "收纳篮"),
        (r"ORGANIZADOR|ORGANIZADORA|SET DE ORGANIZADOR", "收纳工具"),
        (r"BOLSA DE COMPRESION|BOLSA AL VACIO|BOLSA DE ALMACENAMIENTO", "压缩袋"),
        (r"PERCHERO|PERCHA|GANCHO|COLGADOR|ZAPATERO|TENDER", "挂钩/衣架"),
    ],
    "家居生活 > 卫浴用品": [
        (r"CEPILLO DE BAÑO|CEPILLO DE INODORO|CEPILLO PARA BAÑO|ASIENTO DE INODORO", "马桶用品"),
        (r"ESPONJA|ESPONJAS|GUANTE|GUANTES DE BAÑO|CEPILLO CORPORAL", "沐浴工具"),
        (r"CORTINA|CORTINA DE BAÑO", "浴帘"),
        (r"ESTANTE|ESTANTES|REPISA|REPOSERA", "浴室置物架"),
        (r"SET DE BAÑO|DISPENSER|JABONERA|VASO|TOALLERO|PERCHERO", "浴室套装"),
        (r"GANCHO|GANCHOS|ADHESIVO|SOPAPA", "浴室挂钩"),
        (r"CAJA DE PAÑUELOS|PAÑUELOS|TIMBRE|ESPEJO|CABEZAL|LIMPIA VIDRIOS|CLIP", "其他卫浴"),
    ],
    "家居生活 > 清洁用品": [
        (r"CEPILLO|CEPILLOS|CEPILLO DE LIMPIEZA|CEPILLO LIMPIADOR|CEPILLO DE ALAMBRE|CEPILLO DE PELUSAS|CEPILLO QUITA POLVO|PLUMERO", "清洁刷"),
        (r"ESPONJA|ESPONJAS|REPASADOR|PAÑO|PAÑOS|PAÑO DE LIMPIEZA|VIRULANA", "清洁布/海绵"),
        (r"BOLSAS DE BASURA|BOLSAS SANITARIAS|BOLSA PARA RESIDUOS|BOLSA PARA ESCOMBROS|TACHO DE BASURA|TACHO", "垃圾袋/垃圾桶"),
        (r"GUANTES|GUANTE DE LIMPIEZA", "清洁手套"),
        (r"BALDE|BALDES|REJILLA|PAPEL TAPIZ", "其他清洁"),
    ],
    "家居生活 > 家纺毛巾": [
        (r"TOALLA|TOALLAS", "毛巾"),
        (r"ALMOHADA|ALMOHADAS|FUNDA|FUNDAS", "枕头/枕套"),
        (r"MANTA|MANTAS|ALCOLCHADO", "毯子/床品"),
        (r"ALFOMBRA|ALFOMBRAS", "地毯"),
        (r"LONA|CAMBIADOR|SET DE MANTAS", "其他家纺"),
    ],
    "家居生活 > 家具": [
        (r"MESA|MESAS|MESA RATONA", "桌子"),
        (r"ESTANTE|ESTANTES|REPISA|REPOSERA", "置物架"),
        (r"CARRO|CARRO ORGANIZADOR|ORGANIZADOR MOVIL", "推车/收纳车"),
        (r"SILLA|SILLAS|SET DE SILLA|SET DE MUEBLE", "椅子"),
        (r"ESCALERA|ESCALERAS", "梯子/凳梯"),
        (r"BALANZA|CANASTO|CARRO DE COMPRAS|Estante De Alumunio", "其他家具"),
    ],
    "家居生活 > 日用杂货": [
        (r"Encendedor|Encendedores|Fosforo|Fósforo|Bencina|Gas|Llamita", "火机/火柴/燃料"),
        (r"CINTA|CINTA ADHESIVA|CINTA DE PAPEL|CINTA EMBALAR|CINTA AISLADORA|Bervitt|Bervit|Cinta Metrica|CINTA METRICA", "胶带"),
        (r"Adhesivo|Adhesivos|Silicona|Pegamento|Adhesivo T/Plasti|Voligoma|Pomada liquida|Barra silicona", "胶水/粘合剂"),
        (r"BROCHE|BROCHES|Broche ropa|Broche", "晾衣夹"),
        (r"RAQUETA MATA|MOSQUITO|MOSQUITOS|Matamoscas", "驱蚊用品"),
        (r"Manteca cacao|Pañuelo|Elite|Bolsas.*perro|Huesito", "日用小百货"),
        (r"Piñata|Timbre|Escarapela|Cordel|Encordado|Guitarra|Alcohol", "其他杂货"),
    ],
    "家居生活 > 园艺户外": [
        (r"MOLINO|MOLINOS", "风车装饰"),
        (r"MANGUERA|MANGUERAS", "水管"),
        (r"HERRAMIENTA|HERRAMIENTAS|JARDIN|JARDÍN", "园艺工具"),
        (r"TUTOR|TUTORES|MACETA", "花盆支架"),
        (r"PLANTA|PLANTAS|COLGANTE", "人造植物"),
    ],
    "家居生活 > 个人防护": [
        (r"Curita|Curitas|Gasa|GASAS|VENDA|VENDAS|CURETA", "创可贴/纱布"),
        (r"GORRO|GORROS|BUFANDA|BUFANDAS|CUELLO|OREJERAS", "保暖帽巾"),
        (r"GUANTES|GUANTE", "手套"),
        (r"BOLSA DE AGUA CALIENTE|CALENTADOR|HERWAL|CRYSTAL", "暖水袋"),
        (r"LENTES|LENTES ARGENTINA|OFF|OFF AERO|Cepillo Lustre|Protector", "防护用品"),
    ],

    # ===== 电子电器 =====
    "电子电器 > 小家电": [
        (r"VENTILADOR|VENTILADORES|FOCO VENTILADOR", "风扇"),
        (r"Pila|Pilas|Bateria|Batería|Battery|DURACELL|ENERGIZER|RAYOVAC|Maxell|Everready|EVEREADY", "电池"),
        (r"HUMIDIFICADOR|DIFUSOR|DIFUSORA", "加湿器"),
        (r"PAVA ELECTRICA|PAVA|ELECTRICA|CALENTADOR|Hervidor|Hervir", "电热水壶"),
        (r"PANEL LED|FOCO LED|LAMPARA LED|LÁMPARA LED|LUZ|SPOT", "LED灯"),
        (r"ENCENDEDOR|CHISPERO|USB|STEREO|ORGANISER|REPRODUCTOR", "其他小家电"),
    ],
    "电子电器 > 照明灯具": [
        (r"LAMPARA|LÁMPARA|LAMPARAS|LÁMPARAS", "台灯/落地灯"),
        (r"VELADOR|VELADORES", "床头灯"),
        (r"LINTERNA|LINTERNAS|FLASHLIGHT", "手电筒"),
        (r"BOLA DE CRISTAL|BOLA DE CRISTAL", "水晶球灯"),
        (r"LUZ DE EMERGENCIA|LUZ EMERGENCIA|EMERGENCIA", "应急灯"),
    ],
    "电子电器 > 数码配件": [
        (r"AURICULARES|AURICULAR|AURICULAR|BARIONA|FONE|HEADPHONE|EARPHONE|EARBUDS", "耳机"),
        (r"BARRA DE SONIDO|SOUND BAR|SOUND BAR|PARLANTE|SPEAKER", "音箱"),
        (r"SOPORTE|SOPORTES|PORTACELULAR|PORTA CELULAR|STAND|STAND", "手机支架"),
        (r"FUNDA|FUNDA POP|FUNDAS|CASE|CASES|CARCASE", "手机壳"),
        (r"Pila|Pilas|Bateria|Batería|DURACELL|ENERGIZER|RAYOVAC|Maxell|Everready|EVEREADY|Pila Candela", "电池"),
    ],

    # ===== 化妆品饰品 =====
    "化妆品饰品 > 美妆个护": [
        (r"ESPONJA DE MAQUILLAJE|ESPONJA|BORLAS|BROCHA|BROCHAS|SET DE BELLEZA|SET DE MAQUILLAJE|CEPILLO FACIAL|ARQUEADOR|PERFILADOR", "化妆工具"),
        (r"CEPILLO DE PELO|CEPILLO PARA EL PELO|PEINE|PEINES|CEPILLO PARA PELO", "梳子/发刷"),
        (r"LIMA|LIMA DE UÑAS|LIMAS|SET DE MANICURIA|PINZA|PINZAS|CEPILLO PARA UÑAS|TIJERA", "美甲工具"),
        (r"ORGANIZADOR|ORGANIZADORA|ALHAJERO|ALHAJEROS|CAJA", "化妆收纳"),
        (r"MASAJEADOR|MASAJEADORA|ROLLO|PIEDRA|PIEDRA DEPILADORA|EXFOLIADOR|DEPILADORA", "按摩/脱毛"),
        (r"SET PARA BEBE|SET PARA BEBES|GORRO DE BAÑO|BABERO", "婴儿护理"),
        (r"PERFUME|COLONIA|CREMA|LOCION|LABIAL|BRILLO", "护肤/化妆品"),
    ],
    "化妆品饰品 > 时尚配饰": [
        (r"LLAVERO|LLAVEROS|Llavero", "钥匙扣"),
        (r"ALHAJERO|ALHAJEROS|JOYERO|CAJA DE JOYAS", "首饰盒"),
        (r"ESPEJO|ESPEJOS|ESPEJO DE CARTERA|ESPEJO CON PEINE", "镜子"),
        (r"PILOTO|PILOTOS|PARAGUAS|PARAGUAS|CAMPERA|GUANTES", "雨伞/衣物"),
        (r"MASAJEADOR|MASAJEADORA|FACIAL", "按摩仪"),
    ],

    # ===== 箱包皮具 =====
    "箱包皮具 > 箱包配件": [
        (r"NECESER|NECESERES", "洗漱包"),
        (r"MOCHILA|MOCHILAS", "背包"),
        (r"BOLSO|BOLSOS|BOLSO TERMICO|BOLSO TÉRMICO|BANDOLERA|BANDOLERA", "手提包/斜挎包"),
        (r"PORTACOSMETICOS|PORTACOSMETICO|COSMETIQUERA", "化妆品包"),
        (r"MONEDERO|MONEDEROS|RIÑONERA|RIÑONERAS", "零钱包/腰包"),
        (r"CARRITO|CARRITO DE COMPRA|VALIJA|VALIJAS|BOLSA", "购物车/行李箱"),
    ],
    "箱包皮具 > 旅行用品": [
        (r"ALMOHADA DE VIAJE|ALMOHADA|ALMOHADAS", "旅行枕"),
        (r"ORGANIZADOR DE VIAJE|ORGANIZADORES|SET DE VIAJE|NECESER DE VIAJE|BOLSA DE ALMACENAMIENTO|BOLSA AL VACIO", "旅行收纳"),
        (r"BOLSO DE VIAJE|BOLSO VIAJE|BOLSO TIPO PLAYERO|SET DE VIAJE", "旅行包"),
        (r"ANTIFAZ|ANTIFACES", "眼罩"),
        (r"Set de Regalo|Herramientas|Mano Decorativas", "旅行套装/其他"),
    ],

    # ===== 五金 =====
    "五金 > 五金工具": [
        (r"CINTA|CINTA DE PAPEL|CINTA METRICA|CINTA MÉTRICA|CINTA AISLADORA|CINTA COMERCIAL|CINTA BERVIT|Fijapel|Cinta embalar", "胶带"),
        (r"CANDADO|CANDADOS|LINGA|CADENA|TRABA", "锁具"),
        (r"ACEITE|ACEITES|LUBRICANTE|LUBRIND|SILICONA LUBRICANTE", "润滑/保养"),
        (r"BARRA DE SILICONA|BARRA SILICONA|SILICONA|BARRA", "硅胶条"),
        (r"PIEDRA|PIEDRA AFILAR|AFILADOR|AFILADORES", "磨刀石"),
        (r"VELA|VELAS|FOCORO|FOSFORO|FÓSFORO|Gas|Encendedor|Piedra afilar", "其他五金"),
    ],
    "五金 > 缝纫针线": [
        (r"HILO|HILOS|HILO ALGODÓN|HILO COSER|HILO ENCERADO|HILO SISAL|HILO YUTE|HILO CHORICERO|HILO BAMBIN|Tanza|TANZA", "缝纫线"),
        (r"AGUJA|AGUJAS|ALFILER|ALFILERES", "针/别针"),
        (r"CUCHILLA|CORTA HILO|CUTTER|TIJERA", "裁剪工具"),
        (r"SET DE BROCHES|BROCHES|SET HILO CON AGUJA", "缝纫套装"),
    ],

    # ===== 服装鞋帽 =====
    "服装鞋帽 > 服装服饰": [
        (r"GORRO|GORROS|SOMBRERO|SOMBREROS|GORRA|GORRAS", "帽子"),
        (r"GUANTES|GUANTE|GUANTES INVIERNO|GUANTES NIEVE|GUANTE INVIERNO", "手套"),
        (r"MEDIAS|MEDIA|SOQUETE|MEDIAS INVISIBLE", "袜子"),
        (r"PONCHO|PONCHO LLUVIA|CAMPERA|CAMPERA DE LLUVIA|TOALLA", "雨衣/外套"),
    ],
    "服装鞋帽 > 鞋履护理": [
        (r"CORDON|CORDONES|Cordon", "鞋带"),
        (r"POMADA|POMADA LATA|POMADA LIQUIDA|TINTA|TINTA FIX|CREMA|CREMAS", "鞋油/鞋蜡"),
        (r"FUNDA|FUNDA PARA CALZADO|CEPILLO|ALMOHADILLA|PLANTILLA", "鞋配件"),
    ],

    # ===== 运动户外 =====
    "运动户外 > 运动健身": [
        (r"COLCHONETA|COLCHONETAS|YOGA|TOALLA DE YOGA|PELOTA DE YOGA", "瑜伽用品"),
        (r"SOGA|SOGA DE SALTAR|SOGA PARA SALTAR|CUERDA", "跳绳"),
        (r"BANDEJA|BANQUETA|BANQUETAS|BARRA|BARRA DE ENTRENAMIENTO|BANDA|BANDAS|TOBILLERA|PESAS|MANCUERNA", "健身器材"),
        (r"PELOTA|PELOTAS|VOLEY|PALETAS|PALETA", "球类"),
        (r"CARPA|CAMPING|CAMPAMENTO|COLCHON INFLABLE|INFLABLE|INFLADOR|ALMOHADA INFLABLE", "户外露营"),
        (r"BICICLETA|BICI|CADENA|TRABA|BALINES|SILBATO|ULA|ULA ULA|CAMARA", "骑行/其他"),
    ],

    # ===== 母婴用品 =====
    "母婴用品 > 婴幼儿用品": [
        (r"MAMADERA|MAMADERAS|TETINA|TETINAS|BIBERON|BIBERONES|SORBITO|LIMPIA MAMADERA|BOTELLA INFANTIL", "奶瓶/奶嘴"),
        (r"CHUPETE|CHUPETES|MORDILLO|MORDILLOS", "奶嘴/牙胶"),
        (r"JUEGO DE BEBE|SET PARA BEBE|BABERO|BABEROS|COCHE DE BEBE|BOLSA DE DORMIR|MOVIL|MÓVIL", "婴儿用品"),
        (r"MOCHILA INFANTIL|MOCHILA|LUNCHERA INFANTIL|LUNCHERA|SILLA PLEGABLE|LIBRO INFANTIL|PILOTO INFANTIL|SET PARA NIÑAS|SET DE VASOS", "儿童用品"),
    ],

    # ===== 宠物 =====
    "宠物 > 宠物用品": [
        (r"CAMA|CAMA DE MASCOTA|CAMA PARA MASCOTA|CAMAS", "宠物床"),
        (r"CORREA|COLLAR|ARNES|ARNÉS|SET DE CORREA|TRABA", "牵引绳/项圈"),
        (r"PLATO|PLATOS|COMEDERO|COMEDEROS|BOL|FUENTE DE AGUA|DISPENSER", "宠物食具"),
        (r"CEPILLO|CEPILLOS|CEPILLO DE MASCOTA|KIT CORTAUÑAS|JUGUETE|JUGUETES|BOLSO|BOLSOS|MOCHILA|DISPENSER DE BOLSAS", "宠物护理/玩具"),
    ],
}

def classify_product(name, current_category):
    """根据商品名称匹配三级分类"""
    rules = RULES.get(current_category)
    if not rules:
        return None
    name_upper = name.upper() if name else ""
    for pattern, level3 in rules:
        if re.search(pattern, name_upper, re.IGNORECASE):
            return f"{current_category} > {level3}"
    return None

def main():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
    cur = conn.cursor()

    # 统计
    cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1 AND category LIKE '% > %' AND category NOT LIKE '% > % > %'")
    total = cur.fetchone()[0]
    print(f"待细分商品数: {total}")

    # 取所有需要细分的商品
    cur.execute("SELECT id, name, category FROM products WHERE is_available=1 AND category LIKE '% > %' AND category NOT LIKE '% > % > %'")
    products = cur.fetchall()

    updates = {}
    unmatched = {}
    for pid, name, cat in products:
        new_cat = classify_product(name, cat)
        if new_cat and new_cat != cat:
            updates.setdefault(new_cat, []).append(pid)
        else:
            unmatched.setdefault(cat, 0)
            unmatched[cat] += 1

    # 执行更新
    total_updated = 0
    for new_cat, ids in sorted(updates.items(), key=lambda x: -len(x[1])):
        # 分批更新
        batch_size = 500
        for i in range(0, len(ids), batch_size):
            batch = ids[i:i+batch_size]
            placeholders = ",".join(["%s"] * len(batch))
            cur.execute(f"UPDATE products SET category=%s WHERE id IN ({placeholders})", [new_cat] + batch)
        print(f"  {new_cat:45s}  ({len(ids):5d} 条)")
        total_updated += len(ids)

    conn.commit()
    print(f"\n✅ 细分完成，共更新 {total_updated} 条")

    if unmatched:
        print(f"\n未匹配到三级分类（保留二级）:")
        for cat, cnt in sorted(unmatched.items(), key=lambda x: -x[1]):
            print(f"  {cnt:5d}  {cat}")

    # 最终统计
    print(f"\n{'='*60}")
    print("最终分类统计:")
    print(f"{'='*60}")
    cur.execute("""
        SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(category, ' > ', 1), ' > ', -1) as l1,
               SUBSTRING_INDEX(SUBSTRING_INDEX(category, ' > ', 2), ' > ', -1) as l2,
               COUNT(*) as cnt
        FROM products WHERE is_available=1 AND category!=''
        GROUP BY l1, l2 ORDER BY l1, cnt DESC
    """)
    current_l1 = None
    for r in cur.fetchall():
        l1, l2, cnt = r
        if l1 != current_l1:
            current_l1 = l1
            print(f"\n【{l1}】")
        print(f"  {cnt:5d}  {l2}")

    # 三级分类统计
    cur.execute("SELECT COUNT(DISTINCT category) FROM products WHERE is_available=1 AND category LIKE '% > % > %'")
    l3_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1 AND category LIKE '% > % > %'")
    l3_total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1 AND category LIKE '% > %' AND category NOT LIKE '% > % > %'")
    l2_only = cur.fetchone()[0]
    print(f"\n三级分类数: {l3_count}, 三级商品数: {l3_total}, 仅二级商品数: {l2_only}")

    conn.close()

if __name__ == "__main__":
    main()
