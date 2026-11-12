# -*- coding: utf-8 -*-
"""sfpanda 第四轮 - 最终名称分类"""
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

def classify4(name):
    n = name.upper().strip()
    
    # 文具办公
    if any(k in n for k in ['PIZARRA', 'LAPIZ', 'LÁPIZ', 'BOLIGRA', 'BOLIGRFO', 'BOLIRAFO',
                              'BOLIGAFO', 'ESTILOGRAFO', 'ACUARELA', 'PINTURA', 'PINTAR',
                              'COLOREAR', 'LAPICES', 'LÁPICES', 'DIARIO INTIMO', 'PLANIFICADOR',
                              'CALCULADORA', 'CUTTER', 'SOBRE', 'CHINCHES', 'SEÑALADOR',
                              'TIZAS', 'SET DE OFICINA', 'SET DE ARTE', 'SET DE PINTURA',
                              'SET PARA COLOREAR', 'LIBRO', 'ANOTDOR', 'ANOTADOR',
                              'ROLO PARA COLOREAR', 'ROLLO PARA COLOREAR',
                              'SET DE LAPIZ', 'LAPIZ MECANICO', 'LAPIZ ETERNAL',
                              'LAPIZ INFINITO', 'SET DE GEOMETRIA', 'GEOMETRIA',
                              'PILOTO', 'SET DE LIBRERIA']):
        return '文具办公'
    
    # 美妆个护
    if any(k in n for k in ['MONEDERO', 'ALHAJERO', 'NESECER', 'NECESER',
                              'SET DE MANICUR', 'SET DE CORTAUÑAS', 'CORTAUÑAS',
                              'MANICURA', 'MANICURIA', 'SET DE BELLEZA',
                              'COLITAS DE PELO', 'HEBILLA', 'SET DE PELO',
                              'SET DE HEBILLAS', 'AFEITADORA', 'PELADOR',
                              'MAQUILLAJE', 'DECORACION PARA UNAS', 'PELUCA',
                              'PULSERA SANITIZANTE', 'MASAJEADOR',
                              'CALENTADOR PARA ABDOMEN', 'BODYSTOCK',
                              'BODYSTOCKING', 'BANDA ELASTICA', 'BANDAS ELASTICAS']):
        return '美妆个护'
    
    # 收纳整理
    if any(k in n for k in ['TAPER', 'CAJA', 'LATA', 'JAULA', 'CESTA',
                              'ALMOHADA', 'ZAPATERO', 'BROCHE DE MADERA',
                              'BROCHE METALICO', 'BROCHES', 'BROCHE',
                              'IMAN', 'IMÁN', 'SET DE MUEBLE', 'ORGANIZADOR',
                              'SET DE VIAJE', 'PRECINTOS', 'TAPON',
                              'TAPÓN', 'MOSQUITERO']):
        return '收纳整理'
    
    # 厨房餐具
    if any(k in n for k in ['SERVILLETERO', 'CUCHARON', 'POSA PAVA', 'CARAMELERA',
                              'MANTEL', 'SET DE COCINA', 'SET DE UTENSILLOS',
                              'AGARRADERA', 'REJILLA', 'TETERA', 'CUBETERA',
                              'TRITURADOR']):
        return '厨房餐具'
    
    # 清洁用品
    if any(k in n for k in ['SET DE LIMPIEZA', 'DESTAPADOR', 'LIMPIA',
                              'ASIENTO DE INODORO']):
        return '清洁用品'
    
    # 装饰品
    if any(k in n for k in ['CAMPANA', 'ANGEL', 'ANGEL DE CERAMICA', 'PATOS CERAMICA',
                              'MOLINO DE VIENTO', 'ARBOL DE NAVIDAD', 'ÁRBOL DE NAVIDAD',
                              'SOUVENIR', 'FLOR', 'DECORACION', 'MARCO DE FOTO',
                              'BICICLETA DE METAL', 'IMAN BUHO', 'IMAN DE CERAMICA',
                              'IMAN NAVIDEÑO', 'IMAN BROCHE', 'CASCADA DE HUMO',
                              'SAHUMERIO', 'AROMATIZADOR', 'MOVIL PARA CUNA',
                              'MOÑO', 'BRUJA', 'SOMBRERO', 'MASCARA',
                              'TELARAÑA', 'TELA DE ARAÑA', 'PIN FLOR',
                              'PIN DE EMOJI', 'PIN ANIMALES', 'TARJETAS FLORES',
                              'SOBRE CON ESTRELLA', 'BANDERA', 'CORNETA',
                              'VUVUZELA', 'SPINER', 'BIG CLIP',
                              'BROCHE', 'LLAVERO']):
        return '装饰品'
    
    # 派对用品
    if any(k in n for k in ['MASCARA', 'SOMBRERO', 'CAPA', 'DISFRAZ',
                              'BANDERA', 'CORNETA', 'VUVUZELA', 'SOUVENIR',
                              'BABY SHOWER', 'CARPA', 'PISCINA', 'SURF',
                              'ARBOL DE NAVIDAD']):
        return '派对用品'
    
    # 电器电子
    if any(k in n for k in ['PLAFON', 'PLAFÓN', 'BARRA DE SONIDO',
                              'MINI IMPRESORA', 'IMPRESORA']):
        return '电器电子'
    
    # 运动户外
    if any(k in n for k in ['PESA RUSA', 'BARRA DE ENTRENAMIENTO', 'SOGA DE SALTAR',
                              'ACCESORIO PARA DEPORTE']):
        return '运动户外'
    
    # 季节商品
    if any(k in n for k in ['PASAMONTAÑA', 'MANTA', 'FRAZADA']):
        return '季节商品'
    
    # 日用百货
    if any(k in n for k in ['CARRO DE COMPRAS', 'SILLA PLEGABLE', 'BANQUETA',
                              'SET DE SILLA', 'MESA', 'VALIJA',
                              'TRAJETERO', 'TENDER']):
        return '日用百货'
    
    # 个人防护
    if any(k in n for k in ['ANTEOJOS', 'LENTES', 'MASCARA DE TELA',
                              'MASCARA FANTASMA']):
        return '个人防护'
    
    # 婴幼儿
    if any(k in n for k in ['MOVIL PARA CUNA', 'SET PARA NIÑAS']):
        return '婴幼儿用品'
    
    # 宠物
    if any(k in n for k in ['HERRAMIENTA PARA JARDIN', 'HERRAMIENTAS PARA JARDIN']):
        return '宠物用品'
    
    # 厨房炊具
    if any(k in n for k in ['TRITURADOR', 'MASAJEADOR']):
        return '厨房炊具'
    
    return None

classified = {}
still = []
for pid, name in rows:
    cat = classify4(name)
    if cat:
        classified[pid] = cat
    else:
        still.append((pid, name))

print(f"第四轮分类: {len(classified)} 条")
print(f"仍需看图: {len(still)} 条")

from collections import Counter
stats = Counter(classified.values())
print("\n分类统计:")
for cat, cnt in stats.most_common():
    print(f"  {cat}: {cnt}")

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

if still:
    print(f"\n最终未分类 ({len(still)} 条):")
    for pid, name in still:
        print(f"  {pid}\t{name}")

conn.close()
