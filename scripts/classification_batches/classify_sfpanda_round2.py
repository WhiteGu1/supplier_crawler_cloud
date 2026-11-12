# -*- coding: utf-8 -*-
"""sfpanda 第二轮名称分类 - 补充规则"""
import pymysql, sys, json
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

def classify2(name):
    n = name.upper().strip()
    
    # 季节商品
    if any(k in n for k in ['MEDIAS', 'OREJERAS', 'CALENTADORA', 'INVIERNO', 'GUANTE',
                              'ABRIGO', 'BUFANDA', 'GORRO LANA', 'PONCHO']):
        return '季节商品'
    
    # 美妆个护
    if any(k in n for k in ['ESPONJA', 'MAQUILLAJE', 'ESPEJO', 'NECESER', 'BOLSA DE AGUA',
                          'PORTACOSMETICO', 'COSMETICO', 'COSMÉTICO', 'LABIAL', 'RIMEL',
                          'SOMBRA', 'BASE', 'CREMA', 'LOCION', 'LOCION', 'JABON',
                          'JABÓN', 'CHAMPÚ', 'CHAMPU', 'ACONDICIONADOR', 'PEINETA',
                          'TIJERA DE UÑA', 'LIMA', 'PINZA', 'RIZADOR', 'CEPILLO FACIAL',
                          'DISCO', 'ALGODÓN', 'ALGODON', 'PORTA SOAP', 'JABONERA']):
        return '美妆个护'
    
    # 日用百货（箱包配件）
    if any(k in n for k in ['BANDOLERA', 'BOLSO', 'CARTERA', 'MOCHILA', 'RIÑONERA',
                              'LLAVERO', 'PORTA', 'PORTAFO', 'FUNDAS', 'FUNDA',
                              'BILLETERA', 'TARJETERO', 'PASSPORT', 'PORTADINERO']):
        return '日用百货'
    
    # 文具办公
    if any(k in n for k in ['UTILES', 'ÚTILES', 'LAPICERA', 'LÁPIZ', 'BOLIGRAFO',
                              'CUADERNO', 'LIBRETA', 'GOMA', 'SACAPUNTA', 'REGLA',
                              'TIJERA', 'CLIPS', 'GRAPA', 'ESTUCHE', 'CARTUCHERA',
                              'MARCA', 'RESALTADOR', 'CORRECTOR', 'FOLDER', 'CARPETA',
                              'AGENDA', 'PLANNER', 'PLANCHETA', 'ESCRITORIO']):
        return '文具办公'
    
    # 装饰品
    if any(k in n for k in ['FLORERO', 'MACETA', 'CUADRO', 'RELOJ', 'BOLA DE CRISTAL',
                              'VELA', 'PORTAVELA', 'ADORNO', 'DECORATIVO', 'FIGURA',
                              'ESFERA', 'LAMPARA', 'LÁMPARA', 'GUIRNALDA', 'COLGANTE',
                              'MOBIL', 'MÓVIL', 'PORTARETRATO', 'PLACA', 'CUADRO',
                              'POSTER', 'PÓSTER', 'VINILO', 'STICKER', 'PEGATINA',
                              'LLAMADOR', 'TIMBRE', 'CARTEL', 'CARTEL', 'TELA DECORATIVA']):
        return '装饰品'
    
    # 收纳整理
    if any(k in n for k in ['ORGANIZADOR', 'CAJA', 'CAJITA', 'CANASTO', 'CANASTA',
                              'CESTO', 'PERCHERO', 'COLGADOR', 'SOPORTE', 'ESTANTE',
                              'ZAPATILLERO', 'GANCHOS', 'GANCHO', 'BANDEJA ORGANIZADORA']):
        return '收纳整理'
    
    # 电器电子
    if any(k in n for k in ['CARGADOR', 'CABLE', 'AURICULAR', 'PARLANTE', 'ALTAVOZ',
                              'LINTERNA', 'LED', 'ALUMBRADO', 'FLEXO', 'LAMPARA',
                              'LÁMPARA', 'LUZ', 'FOCO', 'BATERIA', 'BATERÍA',
                              'ABROCHADORA', 'PERFORADORA', 'CELULAR', 'TABLET',
                              'TECLADO', 'MOUSE', 'RATÓN', 'CÁMARA', 'CAMARA']):
        return '电器电子'
    
    # 玩具游戏
    if any(k in n for k in ['JUGUETE', 'PELOTA', 'ROMPECABEZA', 'DADO', 'JUEGO',
                              'PUZZLE', 'AROS', 'BOLICHE', 'CASINO', 'NAIPE',
                              'CARTAS', 'DADOS', 'AJEDREZ', 'BINGO']):
        return '玩具游戏'
    
    # 婴幼儿用品
    if any(k in n for k in ['BEBE', 'BEBÉ', 'INFANTIL', 'CHUPETE', 'BABERO',
                              'MORDILLO', 'SONAJERO', 'PELOTE', 'ANDADOR']):
        return '婴幼儿用品'
    
    # 宠物用品
    if any(k in n for k in ['MASCOTA', 'PERRO', 'GATO', 'COMEDERO', 'BEBEDERO']):
        return '宠物用品'
    
    # 清洁用品
    if any(k in n for k in ['ESCOBA', 'RECOGEDOR', 'TRAPEADOR', 'MOPA', 'LIMPION',
                              'CEPILLO', 'PLUMERO', 'ATRAPAPOLVO', 'LIMPIA',
                              'SECADOR', 'FREGONA']):
        return '清洁用品'
    
    # 厨房
    if any(k in n for k in ['SARTEN', 'SARTÉN', 'OLLA', 'CUENCO', 'TAZA', 'VASO',
                              'COPA', 'PLATO', 'BOWL', 'CUCHARA', 'TENEDOR',
                              'UTENSILIO', 'BANDEJA', 'TABLA', 'BATIDOR',
                              'COLADOR', 'ESCURRIDOR']):
        return '厨房餐具'
    
    # 派对用品
    if any(k in n for k in ['GLOBO', 'CUMPLEAÑO', 'BANNER', 'GIRANDOLA',
                              'SERPIENTINA', 'CONFETI', 'CAJA SORPRESA', 'FIESTA']):
        return '派对用品'
    
    # 个人防护
    if any(k in n for k in ['BARBIJO', 'TAPABOCA', 'MASCARILLA', 'GAFAS', 'ANTIPARRAS',
                              'PROTECTOR', 'REDELILLA', 'COFIA']):
        return '个人防护'
    
    # 鞋履护理
    if any(k in n for k in ['PLANTILLA', 'CORDON', 'CORDÓN', 'CREMA CALZADO',
                              'CEPILLO CALZADO', 'ESCABRIDA']):
        return '鞋履护理'
    
    return None

classified = {}
unclassified = []
for pid, name in rows:
    cat = classify2(name)
    if cat:
        classified[pid] = cat
    else:
        unclassified.append((pid, name))

print(f"第二轮分类: {len(classified)} 条")
print(f"仍需看图: {len(unclassified)} 条")

from collections import Counter
stats = Counter(classified.values())
print("\n分类统计:")
for cat, cnt in stats.most_common():
    print(f"  {cat}: {cnt}")

print(f"\n未分类前30条:")
for pid, name in unclassified[:30]:
    print(f"  {pid}\t{name}")

# Write to DB
updated = 0
for pid, cat in classified.items():
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
    updated += cur.rowcount
conn.commit()
print(f"\n数据库更新: {updated} 条")

# Check remaining
cur.execute("""
    SELECT COUNT(*) FROM products
    WHERE supplier_id=1 AND (category IS NULL OR category='')
    AND image_local IS NOT NULL AND image_local != ''
""")
rem = cur.fetchone()[0]
print(f"剩余有图未分类: {rem} 条")

conn.close()
