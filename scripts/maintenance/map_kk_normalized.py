import pymysql, sys, re
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 标准化函数：去除所有空格、特殊字符，转大写
def normalize(s):
    if not s:
        return ''
    # 去除所有非字母数字字符
    s = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ]', '', s)
    return s.upper()

# 构建标准化映射表
# 原始分类 -> 标准中文分类
raw_map = {
    # 厨房餐具
    'CRISTALERIA': '厨房餐具',
    'VASOS': '厨房餐具',
    'VAJILLA': '厨房餐具',
    'BOTELLAS': '厨房餐具',
    'JARRASYDISPENSERS': '厨房餐具',
    'PAVASYTETERAS': '厨房餐具',
    'ARTICULOSDECOCTELERIA': '厨房餐具',
    # 厨房炊具
    'OLLASSARTENESYFUENTES': '厨房炊具',
    'UTENSILIOSDECOCINA': '厨房炊具',
    'MOLDES': '厨房炊具',
    'SETCOCINA': '厨房炊具',
    'BAZARYCOCINA': '厨房炊具',
    'COCINA': '厨房炊具',
    'CONDIMENTEROS': '厨房炊具',
    # 厨房储物
    'CONTENEDORESFRASCOSYLATAS': '厨房储物',
    'TERMICOS': '厨房储物',
    'TABLASYBANDEJAS': '厨房储物',
    # 家居清洁
    'LIMPIEZA': '家居清洁',
    'SETLIMPIEZA': '家居清洁',
    'TACHOSDEBASURA': '家居清洁',
    # 卫浴
    'BANO': '卫浴用品',
    # 家居装饰
    'DECORACION': '家居装饰',
    'VELADORES': '家居装饰',
    'PORTAVELAS': '家居装饰',
    'PORTARETRATOS': '家居装饰',
    'ALFOMBRAS': '家居装饰',
    'ALMOHADONES': '家居装饰',
    # 家居收纳
    'ORGANIZADORES': '家居收纳',
    'SETCAJAS': '家居收纳',
    'CANASTAS': '家居收纳',
    'CANASTOS': '家居收纳',
    # 日用百货
    'VARIOS': '日用百货',
    'SOPORTES': '日用百货',
    'SOPORTESDETV': '日用百货',
    'SETDEREGALO': '日用百货',
    'SETLIVING': '日用百货',
    # 文具办公
    'ARTICULOSDELIBRERIA': '文具办公',
    'CARTUCHERAS': '文具办公',
    'AGENDASYCUADERNOS': '文具办公',
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
    'ACCESORIOSPARACELULARES': '电器电子',
    'ACCESORIOSPARACOMPUTADORAS': '电器电子',
    # 美妆个护
    'HIGIENEYCUIDADOPERSONAL': '美妆个护',
    'BELLEZAYCUIDADOPERSONAL': '美妆个护',
    'SETBELLEZA': '美妆个护',
    'KITDEBIJOUTERIE': '美妆个护',
    # 玩具游戏
    'PELUCHES': '玩具游戏',
    'JUEGOS': '玩具游戏',
    'MUSICALES': '玩具游戏',
    'MASCOTAS': '玩具游戏',
    'ANIMALES': '玩具游戏',
    'SOLDADOS': '玩具游戏',
    'AVIONES': '玩具游戏',
    'VEHICULOENBOLSABLISTER': '玩具游戏',
    'VEHICULOSENCAJABURBUJA': '玩具游戏',
    'VEHICULOARADIOCONTROL': '玩具游戏',
    'MOTOSCAJABLISTERBOLSA': '玩具游戏',
    'ARRASTREYPULLSTRING': '玩具游戏',
    'LANZADORES': '玩具游戏',
    'PISTAS': '玩具游戏',
    'SETDEPESCAPESCAMAGIC': '玩具游戏',
    'INFANTILES': '玩具游戏',
    'BANQUITOSYSILLASINFANTILES': '玩具游戏',
    'BEBOTES': '玩具游戏',
    'SETPOLICIA': '玩具游戏',
    'SETDOCTOR': '玩具游戏',
    'SETMEDIEVAL': '玩具游戏',
    'SETESPACIAL': '玩具游戏',
    'MONOPATINESYANDADORES': '玩具游戏',
    'MUNECAS': '玩具游戏',
    # 派对用品
    'COTILLON': '派对用品',
    'SOMBREROSYACCESORIOS': '派对用品',
    'GORROS': '派对用品',
    'LLAVEROS': '派对用品',
    'SONAJEROS': '派对用品',
    'VERANO': '派对用品',
    # 婴幼儿用品
    'ARTICULOSPARABEBE': '婴幼儿用品',
    'BEBE': '婴幼儿用品',
    # 运动户外
    'DEPORTES': '运动户外',
    'DEPORTE': '运动户外',
    'INDUMENTARIADEPORTIVA': '运动户外',
    'AIRELIBREYCAMPING': '运动户外',
    'ACCESORIOSPARABICICLETAS': '运动户外',
    # 五金工具
    'SETDEHERRAMIENTAS': '五金工具',
    'GUANTES': '五金工具',
    # 照明灯具
    'LUCES': '照明灯具',
    # 箱包配件
    'MOCHILAS': '箱包配件',
    'BOLSOSYCARTERAS': '箱包配件',
    'RINONERASYMORRALES': '箱包配件',
    'BILLETERASYMONEDEROS': '箱包配件',
    'PORTABOTELLAS': '箱包配件',
    'FUNDAS': '箱包配件',
    # 家居家具
    'MESAS': '家居家具',
    'BANQUETAS': '家居家具',
    'SILLAS': '家居家具',
    'MUEBLESDEEXTERIOR': '家居家具',
    'SETDEMESAS': '家居家具',
    'PUFFS': '家居家具',
    # 家居纺织
    'ROPADECAMA': '家居纺织',
    'ROPAINTERIOR': '家居纺织',
    'PIJAMAS': '家居纺织',
    'MEDIAS': '家居纺织',
    'MANTELERIA': '家居纺织',
    # 旅行用品
    'ARTICULOSDEVIAJE': '旅行用品',
    # 时尚配饰
    'ACCESORIOSDEMODA': '时尚配饰',
    'RELOJES': '时尚配饰',
    # 园艺户外
    'FLOREROS': '园艺户外',
    # 其他
    'ACCESORIOSPARAAUTOS': '其他',
}

# 获取所有未映射到标准分类的商品
std_categories = (
    '厨房餐具','厨房炊具','厨房储物','餐饮用品','清洁用品','卫浴用品',
    '装饰品','收纳整理','日用百货','文具办公','个人防护','电器电子',
    '美妆个护','玩具游戏','派对用品','宠物用品','季节商品','婴幼儿用品',
    '运动户外','其他','五金工具','照明灯具','鞋履护理','食品饮料',
    '数码科技','箱包配件','家居纺织','家居家具','家居收纳','家居清洁',
    '家居百货','家居装饰','旅行用品','时尚配饰','服装服饰','针线缝纫',
    '园艺户外','圣诞用品'
)

cur.execute("""
    SELECT DISTINCT category FROM products 
    WHERE supplier_id=10 AND category NOT IN (%s)
""" % ','.join(['%s']*len(std_categories)), std_categories)
remaining_cats = [r[0] for r in cur.fetchall()]

print(f"剩余非标准分类: {len(remaining_cats)}")

updated = 0
unmapped = []
for cat in remaining_cats:
    norm = normalize(cat)
    if norm in raw_map:
        std_cat = raw_map[norm]
        cur.execute("UPDATE products SET category=%s WHERE supplier_id=10 AND category=%s", (std_cat, cat))
        updated += cur.rowcount
    else:
        unmapped.append((cat, norm))

conn.commit()
print(f"已更新: {updated} 条")
print(f"仍未映射: {len(unmapped)}")
if unmapped:
    print("\n未映射分类:")
    for orig, norm in unmapped:
        cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=10 AND category=%s", (orig,))
        cnt = cur.fetchone()[0]
        print(f"  '{orig}' (norm: '{norm}') -> {cnt}条")

# 最终检查
cur.execute("""
    SELECT COUNT(*) FROM products 
    WHERE supplier_id=10 AND category NOT IN (%s)
""" % ','.join(['%s']*len(std_categories)), std_categories)
final_remaining = cur.fetchone()[0]
print(f"\n最终非标准分类剩余: {final_remaining}")

# 分类分布
cur.execute("""
    SELECT category, COUNT(*) as cnt FROM products 
    WHERE supplier_id=10 
    GROUP BY category ORDER BY cnt DESC
""")
rows = cur.fetchall()
print(f"\nKK分类分布 ({len(rows)} 个):")
for r in rows:
    print(f"  {r[0]:<20} {r[1]:>5}")

conn.close()
