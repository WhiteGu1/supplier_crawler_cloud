import pymysql, sys, re
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 125个西班牙语分类 -> 34个标准中文分类映射
# 基于语义分析
category_map = {
    # 厨房餐具
    'CRISTALERIA': '厨房餐具',
    'VASOS': '厨房餐具',
    'VAJILLA': '厨房餐具',
    'BOTELLAS': '厨房餐具',
    'JARRAS Y DISPENSERS': '厨房餐具',
    'PAVAS YTETERAS': '厨房餐具',
    'ARTICULOS DE COCTELERIA': '厨房餐具',
    
    # 厨房炊具
    'OLLAS, SARTENES YFUENTES': '厨房炊具',
    'UTENSILIOS DE COCINA': '厨房炊具',
    'MOLDES': '厨房炊具',
    'SET COCINA': '厨房炊具',
    'BAZAR Y COCINA': '厨房炊具',
    'COCINA': '厨房炊具',
    'CONDIMENTEROS': '厨房炊具',
    
    # 厨房储物
    'CONTENEDORES,FRASCOS YLATAS': '厨房储物',
    'TERMICOS': '厨房储物',
    'TABLAS Y BANDEJAS': '厨房储物',
    
    # 餐饮用品 - 不太适用，归入其他
    
    # 清洁用品
    'LIMPIEZA': '家居清洁',
    'SETLIMPIEZA': '家居清洁',
    'TACHOS DE BASURA': '家居清洁',
    
    # 卫浴用品
    'BANO': '卫浴用品',
    'BAÑO': '卫浴用品',
    
    # 装饰品
    'DECORACION': '家居装饰',
    'VELADORES': '家居装饰',
    'PORTAVELAS': '家居装饰',
    'PORTARETRATOS': '家居装饰',
    'ALFOMBRAS': '家居装饰',
    'ALMOHADONES': '家居装饰',
    
    # 收纳整理
    'ORGANIZADORES': '家居收纳',
    'SET CAJAS': '家居收纳',
    'CANASTAS': '家居收纳',
    'CANASTOS': '家居收纳',
    
    # 日用百货
    'VARIOS': '日用百货',
    'VARIOS': '日用百货',
    'SOPORTES': '日用百货',
    'SOPORTESDETV': '日用百货',
    'SETDEREGALO': '日用百货',
    'SETLIVING': '日用百货',
    
    # 文具办公
    'ARTICULOS DELIBRERIA': '文具办公',
    'CARTUCHERAS': '文具办公',
    'AGENDAS Y CUADERNOS': '文具办公',
    'PIZARRAS': '文具办公',
    
    # 电器电子
    'PARLANTES': '电器电子',
    'AURICULARESVINCHA': '电器电子',
    'AURICULARESINEAR': '电器电子',
    'MICROFONOS': '电器电子',
    'CABLES': '电器电子',
    'CARGADORES': '电器电子',
    'CARGADORESPARAAUTOS': '电器电子',
    'TRANSFORMERS': '电器电子',
    'CAMARAS': '电器电子',
    'CAMARASDEPC': '电器电子',
    'ACCESORIOSPARA CELULARES': '电器电子',
    'ACCESORIOSPARA COMPUTADORAS': '电器电子',
    
    # 美妆个护
    'HIGIENE Y CUIDADO PERSONAL': '美妆个护',
    'BELLEZA Y CUIDADO PERSONAL': '美妆个护',
    'SET BELLEZA': '美妆个护',
    'KIT DE BIJOUTERIE': '美妆个护',
    
    # 玩具游戏
    'PELUCHES': '玩具游戏',
    'JUEGOS': '玩具游戏',
    'MUSICALES': '玩具游戏',
    'MASCOTAS': '玩具游戏',
    'ANIMALES': '玩具游戏',
    ' Soldados'.upper().replace(' ',''): '玩具游戏',
    'SOLDADOS': '玩具游戏',
    'AVIONES': '玩具游戏',
    'VEHICULO EN BOLSA BLISTER': '玩具游戏',
    'VEHICULOS EN CAJA BURBUJA': '玩具游戏',
    'VEHICULO A RADIO CONTROL': '玩具游戏',
    'MOTOS CAJA/ BLISTER/BOLSA': '玩具游戏',
    'ARRASTRE Y PULLSTRING': '玩具游戏',
    'LANZADORES': '玩具游戏',
    'PISTAS': '玩具游戏',
    'SET DE PESCA/PESCA MAGIC': '玩具游戏',
    'INFANTILES': '玩具游戏',
    'BANQUITOS Y SILLASINFANTILES': '玩具游戏',
    'BEBOTES': '玩具游戏',
    'SET POLICIA': '玩具游戏',
    'SET DOCTOR': '玩具游戏',
    'SET MEDIEVAL': '玩具游戏',
    'SET ESPACIAL': '玩具游戏',
    'MONOPATINES Y ANDADORES': '玩具游戏',
    
    # 派对用品
    'COTILLON': '派对用品',
    'SOMBREROS Y ACCESORIOS': '派对用品',
    'GORROS': '派对用品',
    'LLAVEROS': '派对用品',
    'SONAJEROS': '派对用品',
    'VERANO': '派对用品',
    
    # 婴幼儿用品
    'ARTICULOS PARA BEBE': '婴幼儿用品',
    'ARTICULOS PARA BEBE': '婴幼儿用品',
    'BEBE': '婴幼儿用品',
    
    # 运动户外
    'DEPORTES': '运动户外',
    'DEPORTE': '运动户外',
    'INDUMENTARIA DEPORTIVA': '运动户外',
    'AIRELIBRE Y CAMPING': '运动户外',
    'ACCESORIOS PARA BICICLETAS': '运动户外',
    
    # 五金工具
    'SET DE HERRAMIENTAS': '五金工具',
    'GUANTES': '五金工具',
    
    # 照明灯具
    'LUCES': '照明灯具',
    
    # 箱包配件
    'MOCHILAS': '箱包配件',
    'BOLSOS Y CARTERAS': '箱包配件',
    'RIÑONERAS Y MORRALES': '箱包配件',
    'BILLETERAS Y MONEDEROS': '箱包配件',
    'PORTABOTELLAS': '箱包配件',
    'FUNDAS': '箱包配件',
    
    # 家具
    'MESAS': '家居家具',
    'BANQUETAS': '家居家具',
    'SILLAS': '家居家具',
    'MUEBLES DEEXTERIOR': '家居家具',
    'SET DE MESAS': '家居家具',
    'PUFFS': '家居家具',
    
    # 家居纺织
    'ROPA DE CAMA': '家居纺织',
    'ROPA INTERIOR': '家居纺织',
    'PIJAMAS': '家居纺织',
    'MEDIAS': '家居纺织',
    'MANTELERIA': '家居纺织',
    
    # 旅行用品
    'ARTICULOS DE VIAJE': '旅行用品',
    
    # 时尚配饰
    'ACCESORIOS DE MODA': '时尚配饰',
    'RELOJES': '时尚配饰',
    
    # 园艺户外
    'FLOREROS': '园艺户外',
    
    # 服装服饰 - 没有直接的
    
    # 其他
    'MUNECAS': '玩具游戏',  # 洋娃娃归玩具
    'ACCESORIOS PARA AUTOS': '其他',
    'ACCESORIOSPARA AUTOS': '其他',
}

# 获取所有分类
cur.execute("SELECT DISTINCT category FROM products WHERE supplier_id=10")
all_cats = [r[0] for r in cur.fetchall()]

mapped = 0
unmapped = []
for cat in all_cats:
    if cat in category_map:
        mapped += 1
    else:
        unmapped.append(cat)

print(f"已映射: {mapped}/{len(all_cats)}")
print(f"未映射: {len(unmapped)}")
if unmapped:
    print("\n未映射分类:")
    for c in unmapped:
        cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=10 AND category=%s", (c,))
        cnt = cur.fetchone()[0]
        print(f"  '{c}' -> {cnt}条")

# 执行映射
updated = 0
for cat, std_cat in category_map.items():
    cur.execute("UPDATE products SET category=%s WHERE supplier_id=10 AND category=%s", (std_cat, cat))
    updated += cur.rowcount

conn.commit()
print(f"\n已更新: {updated} 条")

# 检查未映射的商品
cur.execute("""
    SELECT COUNT(*) FROM products 
    WHERE supplier_id=10 AND category NOT IN (
        '厨房餐具','厨房炊具','厨房储物','餐饮用品','清洁用品','卫浴用品',
        '装饰品','收纳整理','日用百货','文具办公','个人防护','电器电子',
        '美妆个护','玩具游戏','派对用品','宠物用品','季节商品','婴幼儿用品',
        '运动户外','其他','五金工具','照明灯具','鞋履护理','食品饮料',
        '数码科技','箱包配件','家居纺织','家居家具','家居收纳','家居清洁',
        '家居百货','家居装饰','旅行用品','时尚配饰','服装服饰','针线缝纫',
        '园艺户外','圣诞用品'
    )
""")
remaining = cur.fetchone()[0]
print(f"非标准分类剩余: {remaining}")

if remaining > 0:
    cur.execute("""
        SELECT category, COUNT(*) as cnt FROM products 
        WHERE supplier_id=10 AND category NOT IN (
            '厨房餐具','厨房炊具','厨房储物','餐饮用品','清洁用品','卫浴用品',
            '装饰品','收纳整理','日用百货','文具办公','个人防护','电器电子',
            '美妆个护','玩具游戏','派对用品','宠物用品','季节商品','婴幼儿用品',
            '运动户外','其他','五金工具','照明灯具','鞋履护理','食品饮料',
            '数码科技','箱包配件','家居纺织','家居家具','家居收纳','家居清洁',
            '家居百货','家居装饰','旅行用品','时尚配饰','服装服饰','针线缝纫',
            '园艺户外','圣诞用品'
        )
        GROUP BY category ORDER BY cnt DESC
    """)
    rows = cur.fetchall()
    print("\n剩余非标准分类:")
    for r in rows:
        print(f"  '{r[0]}' -> {r[1]}条")

conn.close()
