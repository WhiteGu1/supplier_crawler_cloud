# -*- coding: utf-8 -*-
"""sfpanda 按名称分类 - 名称短但有特征"""
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
print(f"总计 {len(rows)} 条")

def classify(name):
    n = name.upper().strip()
    
    # 个人防护
    if any(k in n for k in ['GORRO', 'BUFANDA', 'GUANTES', 'GUANTE ', 'BARBIJO', 'TAPABOCA',
                              'MASCARILLA', 'GAFAS', 'ANTIPARRAS', 'PROTECTOR', 'Cofia']):
        return '个人防护'
    
    # 美妆个护
    if any(k in n for k in ['PEINE', 'CEPILLO CABELLO', 'ESPEJO', 'NECESER', 'BOLSA DE AGUA',
                              'PORTACOSMETICO', 'PORTA COSETICO', 'COSMETICO', 'COSMÉTICO',
                              'Tijera Uña', 'TIJERA DE UÑA', 'LIMA DE UÑA', 'CORTAÚÑAS',
                              'PINZA DEPESTAR', 'PINZA DE PESTAÑA', 'RIZADOR', 'PESTAÑA',
                              'PORTA SOAP', 'JABONERA', 'CEPILLO FACIAL']):
        return '美妆个护'
    
    # 卫浴用品
    if any(k in n for k in ['TOALLA', 'CORTINA DE BAÑO', 'ALFOMBRA BAÑO', 'PORTA PAPEL',
                              'PORTAPAPEL', 'PAPEL HIGIENICO', 'PERCHA DE BAÑO',
                              'CEPILLO BAÑO', 'PORTA CEPILLO', 'PORTACEPILLO',
                              ' jabón', 'JABON LIQUIDO', 'GANCHO TOALLA']):
        return '卫浴用品'
    
    # 清洁用品
    if any(k in n for k in ['ESCOBA', 'RECOGEDOR', 'TRAPEADOR', 'MOPA', 'LIMPION', 'CEPILLO PISO',
                              'FREGONA', 'BALDE', 'PALA', 'SECADOR DE PISO', 'LAVAPiso',
                              'CEPILLO LIMPIA', 'LIMPIADOR', 'PLUMERO', 'ATRAPAPOLVO',
                              'RALLADOR DE', 'ESTRIBO']):
        return '清洁用品'
    
    # 厨房餐具
    if any(k in n for k in ['PLATO', 'BOWL', 'CUENCO', 'TAZA', 'VASO', 'COPA', 'BANDEJA',
                              'FUENTE', 'BANDEJITA', 'CUCHARA', 'TENEDOR', 'CUCHILLO',
                              'UTENSILIO', 'PALILLERO', 'SALERO', 'AZUCARERO',
                              'POSAPLATO', 'POSA PLATO', 'PORTAVASO', 'PORTA VASO']):
        return '厨房餐具'
    
    # 厨房炊具
    if any(k in n for k in ['SARTEN', 'SARTÉN', 'OLLA', 'CACEROLA', 'BIFERA', 'PAELLERA',
                              'MOLDE', 'FLANERA', 'BATIDOR', 'ESCURRIDOR', 'COLADOR',
                              'ESPUMADERA', 'CUCHARA DE MADERA', 'TABLA', 'PINZA',
                              'ABRELATAS', ' sacacorchos', 'SACACORCHO', 'RALLADOR',
                              'PROBETA', 'REPASADOR', 'REPOSTERO']):
        return '厨房炊具'
    
    # 餐饮用品
    if any(k in n for k in ['TERMICO', 'TÉRMICO', 'TARRO', 'TERMICO', 'VIAJERA', 'VIANDA',
                              'LONCHERA', 'MATE', 'BOMBILLA', 'TERMO', 'JARRA',
                              'BOTELLA', 'CANTIMPLORA', 'CHOPP', 'CHOP']):
        return '餐饮用品'
    
    # 厨房储物
    if any(k in n for k in ['TUPPER', 'RECIPIENTE', 'CONTENEDOR', 'HERMETICO', 'FRASCO',
                              'POTE', 'TARRO', 'ENVASE', 'CONSERVADORA']):
        return '厨房储物'
    
    # 收纳整理
    if any(k in n for k in ['CAJA', 'CAJITA', 'CANASTO', 'CANASTA', 'CESTO', 'ORGANIZADOR',
                              'PERCHERO', 'CABALLETE', 'GANCHOS', 'GANCHO', 'COLGADOR',
                              'SOPORTE', 'BANDEJA ORGANIZADORA', 'ESTANTE', 'REPISA',
                              'ZAPATILLERO', 'COLGAR', 'TENDEDORE', 'TENDEDOR']):
        return '收纳整理'
    
    # 装饰品
    if any(k in n for k in ['FLORERO', 'MACETA', 'CUADRO', 'RELOJ', 'BOLA DE CRISTAL',
                              'VELA', 'PORTAVELA', 'ADORNO', 'DECORATIVO', 'FIGURA',
                              'ESFERA', 'LAMPARA', 'LÁMPARA', 'GUIRNALDA', 'COLGANTE',
                              'MOBIL', 'MÓVIL', 'PLANTA', 'SUCCULENTO', 'CACTUS',
                              'PORTARETRATO', 'PORTA RETRATO', 'MURALLA', 'PLACA']):
        return '装饰品'
    
    # 派对用品
    if any(k in n for k in ['GLOBOS', 'GLOBO', 'CUMPLEAÑO', 'BANNER', 'GIRANDOLA',
                              'SERPIENTINA', 'CONFETI', 'POP', 'CAJA SORPRESA']):
        return '派对用品'
    
    # 玩具游戏
    if any(k in n for k in ['JUGUETE', 'PELOTA', 'ROMPECABEZA', 'PELOTA', 'DADO',
                              'JUEGO', 'PUZZLE', 'AROS', 'BOLICHE']):
        return '玩具游戏'
    
    # 文具办公
    if any(k in n for k in ['LAPICERA', 'LÁPIZ', 'BOLIGRAFO', 'CUADERNO', 'LIBRETA',
                              'GOMA', 'SACAPUNTA', 'REGLA', 'Tijera', 'TIJERA',
                              'CLIPS', 'GRAPA', 'PORTALAPIZ', 'PORTA LAPIZ',
                              'ESTUCHE', 'CARTUCHERA']):
        return '文具办公'
    
    # 电器电子
    if any(k in n for k in ['CARGADOR', 'CABLE', 'AURICULAR', 'PARLANTE', 'ALTAVOZ',
                              'LINTERNA', 'LED', 'FLEXO', 'ABROCHADORA']):
        return '电器电子'
    
    # 宠物用品
    if any(k in n for k in ['MASCOTA', 'PERRO', 'GATO', 'CHIGUITO', 'COMEDERO', 'BEBEDERO',
                              'JUGUETE PERRO', 'JUGUETE GATO']):
        return '宠物用品'
    
    # 日用百货
    if any(k in n for k in ['PERCHA', 'GANCHO', 'Tendedor', 'PINZA COLGAR', 'CUERDA',
                              'CINTA', 'AGUJA', 'HILO', 'BOTON', 'BOTÓN', 'CREMALLERA',
                              'ALFILER', 'GANCHO ROPA', 'PERCHA METAL', 'TENDEDOR',
                              'Tendedera', 'TENDEDERA', 'ESTACA', 'ESTANTE METAL',
                              'CUBRE', 'FUNDA', 'COVER']):
        return '日用百货'
    
    # 季节商品
    if any(k in n for k in ['VENTILADOR', 'ABANICO', 'ESTUFITA', 'CALEFACTOR', 'PONCHO',
                              'MANTA', 'FRAZADA', 'IMPERMEABLE', 'PARAGUA', 'PARAGUAS',
                              'SOMBRILLA']):
        return '季节商品'
    
    # 婴幼儿用品
    if any(k in n for k in ['BEBE', 'BEBÉ', 'INFANTIL', 'NIÑO', 'CHUPETE', 'BABERO',
                              'MORDILLO', 'SONAJERO']):
        return '婴幼儿用品'
    
    # 鞋履护理
    if any(k in n for k in ['CREMA CALZADO', 'ZAPATO', 'PLANTILLA', 'CORDON', 'CORDÓN',
                              'ESCABRIDA', 'CEPILLO CALZADO']):
        return '鞋履护理'
    
    return None

# Classify
classified = {}
unclassified = []
for pid, name in rows:
    cat = classify(name)
    if cat:
        classified[pid] = cat
    else:
        unclassified.append((pid, name))

print(f"\n名称分类成功: {len(classified)} 条")
print(f"未分类需看图: {len(unclassified)} 条")

# Stats
from collections import Counter
stats = Counter(classified.values())
print("\n分类统计:")
for cat, cnt in stats.most_common():
    print(f"  {cat}: {cnt}")

print(f"\n未分类前20条:")
for pid, name in unclassified[:20]:
    print(f"  {pid}\t{name}")

# Write to DB
updated = 0
for pid, cat in classified.items():
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
    updated += cur.rowcount
conn.commit()
print(f"\n数据库更新: {updated} 条")

# Save unclassified for image classification
import json
with open('sfpanda_need_image.json', 'w', encoding='utf-8') as f:
    json.dump([{"id": p, "name": n} for p, n in unclassified], f, ensure_ascii=False, indent=2)

# Get image paths for unclassified
cur.execute("""
    SELECT id, image_local FROM products
    WHERE supplier_id=1 AND (category IS NULL OR category='')
    AND image_local IS NOT NULL AND image_local != ''
    ORDER BY id
""")
remaining = cur.fetchall()
print(f"\n剩余有图未分类: {len(remaining)} 条")

conn.close()
