# -*- coding: utf-8 -*-
"""sfpanda 第三轮名称分类"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT id, name FROM products
    WHERE supplier_id=1 AND (category IS NULL OR category='')
    AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
""")
rows = cur.fetchall()
print(f"剩余 {len(rows)} 条")

def classify3(name):
    n = name.upper().strip()
    
    # 玩具游戏
    if any(k in n for k in ['MUÑECA', 'MUÑECO', 'PELUCHE', 'JUGUETE', 'PELOTA',
                              'ROMPECABEZA', 'DADO', 'JUEGO', 'PUZZLE', 'BOLICHE',
                              'CASINO', 'NAIPE', 'CARTAS', 'DADOS', 'AJEDREZ',
                              'BINGO', 'PLAYA', 'ARENA', 'CASTILLO', 'TELE', 'TENTEMPIE',
                              'YOYO', 'YOMYO', 'COMETA', 'BARRILETE', 'TROMPO',
                              'BALERO', 'DIABOLO', 'TUTO', 'CUCO', 'PIOLA']):
        return '玩具游戏'
    
    # 文具办公
    if any(k in n for k in ['LIENZO', 'LIBRO', 'BLOCK', 'NOTAS', 'NOTA', 'CUADERNO',
                              'LIBRETA', 'AGENDA', 'PLANNER', 'PLANCHETA', 'ESCRITORIO',
                              'SET DE LIBRERIA', 'SET DE NOTAS', 'PINTAR',
                              'PINCEL', 'ACRILICO', 'TINTA', 'PAPEL', 'HOJA',
                              'CARTULINA', 'FOLDER', 'CARPETA', 'LAMINA', 'LÁMINA',
                              'ESTAMP', 'STAMP', 'SELLO', 'PLASTIFICAR', 'TAG',
                              'ETIQUETA', 'MARCADOR', 'ROTULADOR', 'CRAYON',
                              'TEMPERA', 'PLASTILINA', 'MODELAR', 'ARCILLA',
                              'Tijera', 'TIJERA', 'REGLA', 'COMPAS', 'COMPÁS',
                              'ESCUADRA', 'TRANSPORTADOR']):
        return '文具办公'
    
    # 厨房餐具/炊具
    if any(k in n for k in ['CUBIERTO', 'BROCHETA', 'SORBETE', 'CUCHARA',
                              'TENEDOR', 'CUCHILLO', 'UTENSILIO', 'TABLA',
                              'SARTEN', 'SARTÉN', 'OLLA', 'MOLDE', 'BATIDOR',
                              'COLADOR', 'ESCURRIDOR', 'PINZA', 'ABRELATAS',
                              'SACACORCHO', 'RALLADOR', 'ESPATULA', 'ESPÁTULA',
                              'CUCHARA', 'CUENCO', 'TAZA', 'VASO', 'COPA',
                              'PLATO', 'BOWL', 'BANDEJA']):
        return '厨房餐具'
    
    # 餐饮用品
    if any(k in n for k in ['SORBETE', 'BOMBILLA', 'TERMO', 'MATE', 'JARRA',
                              'BOTELLA', 'CANTIMPLORA', 'CHOPP', 'CHOP',
                              'SET DE SORBETES']):
        return '餐饮用品'
    
    # 装饰品
    if any(k in n for k in ['FLOR', 'FLORERO', 'MACETA', 'CUADRO', 'RELOJ',
                              'BOLA DE CRISTAL', 'VELA', 'PORTAVELA', 'ADORNO',
                              'DECORATIVO', 'FIGURA', 'ESFERA', 'LAMPARA',
                              'LÁMPARA', 'GUIRNALDA', 'COLGANTE', 'MOBIL',
                              'MÓVIL', 'PORTARETRATO', 'PLACA', 'POSTER',
                              'PÓSTER', 'VINILO', 'STICKER', 'PEGATINA',
                              'PIEDRA', 'CRISTAL', 'GEMA', 'MINERAL',
                              'CUADRO', 'TELA DECORATIVA', 'MANDALA',
                              'DREAMCATCHER', 'ATRAPASUEÑO', 'COLGANTE',
                              'MURAL', 'VINILO DECORATIVO']):
        return '装饰品'
    
    # 日用百货
    if any(k in n for k in ['SELLADOR', 'BOLSA', 'ORGANZA', 'BANDEJA',
                              'LLAVERO', 'BILLETERA', 'TARJETERO',
                              'BANDOLERA', 'BOLSO', 'CARTERA', 'MOCHILA',
                              'RIÑONERA', 'PORTA', 'FUNDA', 'CUBRE',
                              'ALFOMBRA', 'CORTINA', 'FUNDAS', 'NECESER']):
        return '日用百货'
    
    # 电器电子
    if any(k in n for k in ['HUMIDIFICADOR', 'DIFUSOR', 'PURIFICADOR',
                              'CARGADOR', 'CABLE', 'AURICULAR', 'PARLANTE',
                              'ALTAVOZ', 'LINTERNA', 'LED', 'ALUMBRADO',
                              'LUZ', 'FOCO', 'BATERIA', 'BATERÍA',
                              'ABROCHADORA', 'PERFORADORA', 'MICROFONO',
                              'MICRÓFONO', 'CAMARA', 'CÁMARA', 'TECLADO',
                              'MOUSE', 'RATÓN', 'VENTILADOR', 'ABANICO',
                              'ESTUFITA', 'CALEFACTOR']):
        return '电器电子'
    
    # 个人防护
    if any(k in n for k in ['LENTE', 'LENTES', 'GAFAS', 'ANTIPARRAS',
                              'BARBIJO', 'TAPABOCA', 'MASCARILLA',
                              'PROTECTOR', 'REDELILLA', 'COFIA',
                              'GORRO', 'GUANTE']):
        return '个人防护'
    
    # 派对用品
    if any(k in n for k in ['CAPA', 'VAMPIRO', 'DISFRAZ', 'CUMPLEAÑO',
                              'GLOBO', 'BANNER', 'GIRANDOLA', 'SERPIENTINA',
                              'CONFETI', 'CAJA SORPRESA', 'FIESTA',
                              'COTILLON', 'COTILÓN', 'PIÑATA']):
        return '派对用品'
    
    # 收纳整理
    if any(k in n for k in ['ORGANIZADOR', 'CAJA', 'CAJITA', 'CANASTO',
                              'CANASTA', 'CESTO', 'PERCHERO', 'COLGADOR',
                              'SOPORTE', 'ESTANTE', 'ZAPATILLERO',
                              'GANCHOS', 'GANCHO']):
        return '收纳整理'
    
    # 季节商品
    if any(k in n for k in ['OREJERA', 'MEDIAS', 'CALENTADORA', 'INVIERNO',
                              'ABRIGO', 'MANTA', 'FRAZADA', 'IMPERMEABLE',
                              'PARAGUA', 'PARAGUAS', 'SOMBRILLA', 'PONCHO']):
        return '季节商品'
    
    # 美妆个护
    if any(k in n for k in ['ESPONJA', 'MAQUILLAJE', 'ESPEJO', 'BOLSA DE AGUA',
                              'COSMETICO', 'COSMÉTICO', 'LABIAL', 'RIMEL',
                              'SOMBRA', 'BASE', 'CREMA', 'LOCION', 'JABON',
                              'JABÓN', 'CHAMPÚ', 'CHAMPU', 'PEINETA',
                              'LIMA', 'PINZA', 'RIZADOR', 'CEPILLO',
                              'DISCO', 'ALGODÓN', 'ALGODON', 'JABONERA',
                              'TOALLA', 'PAÑO', 'PANO']):
        return '美妆个护'
    
    # 清洁用品
    if any(k in n for k in ['ESCOBA', 'RECOGEDOR', 'TRAPEADOR', 'MOPA',
                              'LIMPION', 'CEPILLO', 'PLUMERO', 'ATRAPAPOLVO',
                              'LIMPIA', 'SECADOR', 'FREGONA', 'LAVA',
                              'PALA']):
        return '清洁用品'
    
    # 卫浴用品
    if any(k in n for k in ['CORTINA DE BAÑO', 'ALFOMBRA BAÑO', 'PORTA PAPEL',
                              'PORTAPAPEL', 'PAPEL HIGIENICO', 'CEPILLO BAÑO',
                              'PORTA CEPILLO', 'PORTACEPILLO']):
        return '卫浴用品'
    
    # 婴幼儿
    if any(k in n for k in ['BEBE', 'BEBÉ', 'INFANTIL', 'CHUPETE', 'BABERO',
                              'MORDILLO', 'SONAJERO']):
        return '婴幼儿用品'
    
    # 宠物
    if any(k in n for k in ['MASCOTA', 'PERRO', 'GATO', 'COMEDERO', 'BEBEDERO']):
        return '宠物用品'
    
    return None

classified = {}
still_unclassified = []
for pid, name in rows:
    cat = classify3(name)
    if cat:
        classified[pid] = cat
    else:
        still_unclassified.append((pid, name))

print(f"第三轮分类: {len(classified)} 条")
print(f"仍需看图: {len(still_unclassified)} 条")

from collections import Counter
stats = Counter(classified.values())
print("\n分类统计:")
for cat, cnt in stats.most_common():
    print(f"  {cat}: {cnt}")

# Write to DB
updated = 0
for pid, cat in classified.items():
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
    updated += cur.rowcount
conn.commit()
print(f"\n数据库更新: {updated} 条")

cur.execute("""
    SELECT COUNT(*) FROM products
    WHERE supplier_id=1 AND (category IS NULL OR category='')
    AND image_local IS NOT NULL AND image_local != ''
""")
rem = cur.fetchone()[0]
print(f"剩余有图未分类: {rem} 条")

print(f"\n未分类全部:")
for pid, name in still_unclassified:
    print(f"  {pid}\t{name}")

conn.close()
