# -*- coding: utf-8 -*-
"""
将所有西班牙语/非标准分类映射到统一中文分类体系
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 获取所有分类及其数量
cur.execute("""
    SELECT category, COUNT(*) as cnt FROM products
    WHERE category IS NOT NULL AND category != ''
    GROUP BY category ORDER BY cnt DESC
""")
all_cats = cur.fetchall()
print(f"共有 {len(all_cats)} 个不同分类名")

# 标准中文分类体系（已有的）
standard_cats = {
    '厨房餐具', '厨房炊具', '厨房储物', '餐饮用品', '清洁用品',
    '卫浴用品', '装饰品', '收纳整理', '日用百货', '文具办公',
    '个人防护', '电器电子', '美妆个护', '玩具游戏', '派对用品',
    '宠物用品', '季节商品', '婴幼儿用品', '运动户外', '其他',
    '五金工具', '照明灯具', '鞋履护理', '食品饮料', '数码科技',
    '箱包配件', '家居纺织', '家居家具', '家居收纳', '家居清洁',
    '家居百货', '家居装饰', '旅行用品', '时尚配饰', '服装服饰',
    '针线缝纫', '园艺户外', '圣诞用品',
}

# 映射规则：西班牙语/非标准分类 → 标准分类
mapping = {}

def add_map(pattern, target):
    """添加映射规则"""
    mapping[pattern.upper().strip()] = target

# === 基于关键词的映射 ===
# 对于嵌套分类 "A > B > C"，取最后一级
# 对于 "COLLECTION > XXX" 格式，基于XXX判断

# KITCHEN COLLECTION → 厨房相关
kitchen_kitchen = ['KITCHEN COLLECTION', 'Coc. Bazar', 'BAZAR', 'Coc.']
for kw in kitchen_kitchen:
    add_map(kw, '厨房餐具')  # 默认归厨房餐具

# 精确映射
category_mapping = {
    # KITCHEN COLLECTION 子类
    'KITCHEN COLLECTION > BOTELLAS DEPORTIVAS': '餐饮用品',
    'KITCHEN COLLECTION > TERMOS': '餐饮用品',
    'KITCHEN COLLECTION > LUNCHERAS': '餐饮用品',
    'KITCHEN COLLECTION > CAFETERAS': '厨房炊具',
    'KITCHEN COLLECTION > CAFETERAS CON POCILLOS': '厨房炊具',
    'KITCHEN COLLECTION > TETERA': '餐饮用品',
    'KITCHEN COLLECTION > JUEGO DE TE': '餐饮用品',
    'KITCHEN COLLECTION > CAJAS DE TE': '餐饮用品',
    'KITCHEN COLLECTION > INFUSORES': '餐饮用品',
    'KITCHEN COLLECTION > TIMERS / INFUSORES': '餐饮用品',
    'KITCHEN COLLECTION > UTENSILIOS': '厨房炊具',
    'KITCHEN COLLECTION > ESPATULAS/CUCHARONES/ESPUMADERAS': '厨房炊具',
    'KITCHEN COLLECTION > ACCESORIOS DE ALAMBRE': '厨房炊具',
    'KITCHEN COLLECTION > CUCHILLAS ACERO': '厨房餐具',
    'KITCHEN COLLECTION > CUCHILLAS CERAMICA': '厨房餐具',
    'KITCHEN COLLECTION > CUBIERTOS': '厨房餐具',
    'KITCHEN COLLECTION > RALLADORES': '厨房炊具',
    'KITCHEN COLLECTION > PICADORAS': '厨房炊具',
    'KITCHEN COLLECTION > MOLDES DE SILICONA': '厨房炊具',
    'KITCHEN COLLECTION > REPOSTERIA': '厨房炊具',
    'KITCHEN COLLECTION > COCINA TEFLON': '厨房炊具',
    'KITCHEN COLLECTION > OLLAS Y SARTENES': '厨房炊具',
    'KITCHEN COLLECTION > FREIDORAS': '厨房炊具',
    'KITCHEN COLLECTION > MOLDE PARA HELADOS': '厨房炊具',
    'KITCHEN COLLECTION > ESCURRIDORES DE PLATOS / CUBIERTOS': '厨房餐具',
    'KITCHEN COLLECTION > COLADORES Y BATIDORES': '厨房炊具',
    'KITCHEN COLLECTION > ORGANIZADOR DE COCINA': '收纳整理',
    'KITCHEN COLLECTION > ALMACENAMIENTO Y ORGANIZACIÓN': '收纳整理',
    'KITCHEN COLLECTION > ACRÍLICO COCINA': '厨房储物',
    'KITCHEN COLLECTION > FRASCOS DE ACRILICO': '厨房储物',
    'KITCHEN COLLECTION > ESPECIEROS': '厨房储物',
    'KITCHEN COLLECTION > AZUCARERAS': '厨房储物',
    'KITCHEN COLLECTION > CEREALERAS': '厨房储物',
    'KITCHEN COLLECTION > DISPENSER': '厨房储物',
    'KITCHEN COLLECTION > DISPENSER DE JUGO': '厨房储物',
    'KITCHEN COLLECTION > ACEITERAS / VINAGRERAS': '厨房储物',
    'KITCHEN COLLECTION > SALEROS / PIMENTEROS': '厨房餐具',
    'KITCHEN COLLECTION > VASOS': '餐饮用品',
    'KITCHEN COLLECTION > INDIVIDUALES PVC': '厨房餐具',
    'KITCHEN COLLECTION > INDIVIDUALES PAPEL': '厨房餐具',
    'KITCHEN COLLECTION > SERVILLETAS DE PAPEL': '厨房餐具',
    'KITCHEN COLLECTION > SERVILLETEROS': '厨房餐具',
    'KITCHEN COLLECTION > TABLAS DE PICAR': '厨房餐具',
    'KITCHEN COLLECTION > BANDEJAS METAL': '厨房餐具',
    'KITCHEN COLLECTION > BANDEJAS MADERA': '厨房餐具',
    'KITCHEN COLLECTION > CHANGOS PARA COMPRAS': '日用百货',
    'KITCHEN COLLECTION > CARROS COCINA': '日用百货',
    'KITCHEN COLLECTION > SETS DE ASADO': '厨房炊具',
    'KITCHEN COLLECTION > SUSHI': '厨房餐具',
    'KITCHEN COLLECTION > COCTELERIA': '餐饮用品',
    'KITCHEN COLLECTION > HIELOS / HIELERAS': '厨房储物',
    'KITCHEN COLLECTION > CONSERVADORA TERMICA': '餐饮用品',
    'KITCHEN COLLECTION > MELAMINA': '厨房餐具',
    'KITCHEN COLLECTION > MOLINILLOS DE CAFE': '厨房炊具',
    'KITCHEN COLLECTION > BALANZAS': '厨房炊具',
    'KITCHEN COLLECTION > PINZA ALIMENTOS': '厨房餐具',
    'KITCHEN COLLECTION > POSAVASOS / POSAPAVAS': '厨房餐具',
    'KITCHEN COLLECTION > POSA UTENSILIO': '厨房餐具',
    'KITCHEN COLLECTION > PORTARROLLOS': '厨房餐具',
    'KITCHEN COLLECTION > PERCHEROS': '收纳整理',
    'KITCHEN COLLECTION > ALFOMBRAS COCINA': '日用百货',
    'KITCHEN COLLECTION > PARA TEFLON': '厨房炊具',
    'KITCHEN COLLECTION > PAVAS': '餐饮用品',
    'KITCHEN COLLECTION > CORTADORES': '厨房炊具',
    'KITCHEN COLLECTION > CUBREALIMENTOS': '厨房储物',
    'KITCHEN COLLECTION > FUENTES METAL': '厨房餐具',
    'KITCHEN COLLECTION > FRUTAS / IMANES': '厨房餐具',
    'KITCHEN COLLECTION > PLATO DE MASAS': '厨房餐具',
    'KITCHEN COLLECTION > DESTAPADORES DE BOTELLA': '厨房炊具',
    'KITCHEN COLLECTION > PORTABOTELLAS': '餐饮用品',
    'KITCHEN COLLECTION > ABRELATAS': '厨房炊具',
    'KITCHEN COLLECTION > BANQUITOS': '收纳整理',
    'KITCHEN COLLECTION > FONDUES': '厨房炊具',
    'KITCHEN COLLECTION > MUEBLES': '家居家具',
    'KITCHEN COLLECTION > PIZARRAS': '文具办公',
    'KITCHEN COLLECTION > VAJILLA PLASTICO TRIGO': '厨房餐具',
    'KITCHEN COLLECTION > LATON PREMIUM': '厨房餐具',
    'KITCHEN COLLECTION > SET PARA QUESO': '厨房餐具',
    'KITCHEN COLLECTION > TACOS DE CUCHILLO': '厨房餐具',
    'KITCHEN COLLECTION > MANTEQUERA': '厨房炊具',
    
    # BATH COLLECTION → 卫浴用品
    'BATH COLLECTION > ACCESORIOS': '卫浴用品',
    'BATH COLLECTION > PORTA COSMETICOS': '卫浴用品',
    'BATH COLLECTION > ALFOMBRAS DE BAÑO': '卫浴用品',
    'BATH COLLECTION > ALFOMBRAS ANTIDESLIZANTE': '卫浴用品',
    'BATH COLLECTION > DISPENSER DE BAÑO': '卫浴用品',
    'BATH COLLECTION > TACHOS / CESTOS': '卫浴用品',
    'BATH COLLECTION > CEPILLOS DE BAÑO': '清洁用品',
    'BATH COLLECTION > SET DE BAÑO': '卫浴用品',
    'BATH COLLECTION > SET BAÑO PORCELANA': '卫浴用品',
    'BATH COLLECTION > SET DE SPA': '卫浴用品',
    'BATH COLLECTION > ESPEJOS': '美妆个护',
    'BATH COLLECTION > CORTINA DE BAÑO': '卫浴用品',
    'BATH COLLECTION > CUIDADO PERSONAL': '美妆个护',
    'BATH COLLECTION > JABONERAS': '卫浴用品',
    'BATH COLLECTION > TENDER': '收纳整理',
    'BATH COLLECTION > TAPAS DE INODORO': '卫浴用品',
    
    # DECO COLLECTION → 装饰品
    'DECO COLLECTION > FLOREROS DECO': '装饰品',
    'DECO COLLECTION > PETIT MUEBLES': '装饰品',
    'DECO COLLECTION > CUADROS': '装饰品',
    'DECO COLLECTION > CANDELABROS': '装饰品',
    'DECO COLLECTION > VELAS / INCIENSOS': '装饰品',
    'DECO COLLECTION > CANASTAS': '收纳整理',
    'DECO COLLECTION > PLANTAS ARTIFICIALES': '装饰品',
    'DECO COLLECTION > ILUMINACION DECO': '照明灯具',
    'DECO COLLECTION > ESPEJOS DE PARED': '装饰品',
    'DECO COLLECTION > PERCHERO DE PARED': '收纳整理',
    'DECO COLLECTION > PERCHEROS / PARAGÜEROS': '收纳整理',
    'DECO COLLECTION > SILLAS Y BANQUETAS': '家居家具',
    'DECO COLLECTION > BOX': '收纳整理',
    'DECO COLLECTION > ENANITOS / FUENTES DE AGUA': '装饰品',
    'DECO COLLECTION > CENTROS DE MESA Y ACC.': '装饰品',
    'DECO COLLECTION > FIG DECORATIVAS': '装饰品',
    'DECO COLLECTION > MACETEROS': '装饰品',
    'DECO COLLECTION > ACCESORIOS VARIOS': '装饰品',
    'DECO COLLECTION > AFRICANAS / FUENTES': '装饰品',
    'DECO COLLECTION > FLORES ARTIFICIALES': '装饰品',
    'DECO COLLECTION > PORTALLAVES': '日用百货',
    'DECO COLLECTION > PORTARRETRATOS METAL': '装饰品',
    'DECO COLLECTION > PORTARRETRATOS MADERA': '装饰品',
    'DECO COLLECTION > BAULES / COFRES': '收纳整理',
    'DECO COLLECTION > DECORACION INDU': '装饰品',
    'DECO COLLECTION > LINEA NAVIERA': '装饰品',
    
    # GLASS COLLECTION → 厨房餐具/装饰品
    'GLASS COLLECTION > POCILLOS': '厨房餐具',
    'GLASS COLLECTION > POTISCH': '厨房餐具',
    'GLASS COLLECTION > COPAS': '餐饮用品',
    'GLASS COLLECTION > FLOREROS': '装饰品',
    'GLASS COLLECTION > JARRAS / BOTELLAS / DISPENSER': '餐饮用品',
    'GLASS COLLECTION > CENTROS DE MESA': '装饰品',
    'GLASS COLLECTION > FUENTES / COPETINEROS': '厨房餐具',
    
    # NAVIDAD → 圣诞用品
    'NAVIDAD > BOLAS': '圣诞用品',
    'NAVIDAD > ARBOLES': '圣诞用品',
    'NAVIDAD > ADORNOS': '圣诞用品',
    'NAVIDAD > MUÑECOS': '圣诞用品',
    'NAVIDAD > CANDELABROS NAVIDAD': '圣诞用品',
    'NAVIDAD > CAJA MUSICAL': '圣诞用品',
    'NAVIDAD > ILUMINACION': '圣诞用品',
    'NAVIDAD > CASCANUECES': '圣诞用品',
    'NAVIDAD > CIERVOS CON ILUMINACION': '圣诞用品',
    'NAVIDAD > FANALES NAVIDEÑOS': '圣诞用品',
    'NAVIDAD > VELAS ARTIFICIALES': '圣诞用品',
    'NAVIDAD > FLORES Y ARMADOS SECOS': '圣诞用品',
    'NAVIDAD > PUNTALES P/ARBOL': '圣诞用品',
    'NAVIDAD > BOTAS': '圣诞用品',
    'NAVIDAD > GORROS': '圣诞用品',
    'NAVIDAD > MOÑOS': '圣诞用品',
    'NAVIDAD > PAPA NOEL MUSICAL': '圣诞用品',
    'NAVIDAD > VINCHAS Y ANTEOJOS': '圣诞用品',
    'NAVIDAD > PLATOS DE SITIO NAVIDEÑOS': '圣诞用品',
    'NAVIDAD > CINTAS DECORATIVAS': '圣诞用品',
    'NAVIDAD > CORONA': '圣诞用品',
    'NAVIDAD > ACCESORIOS': '圣诞用品',
    'NAVIDAD > ACCESORIOS NAVIDAD': '圣诞用品',
    
    # CLOCK COLLECTION → 装饰品
    'CLOCK COLLECTION > RELOJES PARED PLASTICO': '装饰品',
    'CLOCK COLLECTION > RELOJES C/PENDULO': '装饰品',
    'CLOCK COLLECTION > RELOJES ESCRITORIO': '装饰品',
    'CLOCK COLLECTION > RELOJES PARED ACERO': '装饰品',
    'CLOCK COLLECTION > CUCUS': '装饰品',
    'CLOCK COLLECTION > RELOJES MESA': '装饰品',
    'CLOCK COLLECTION > RELOJES CON DISEÑO': '装饰品',
    'CLOCK COLLECTION > RELOJES DE VIDRIO': '装饰品',
    
    # TEXTIL COLLECTION → 家居纺织
    'TEXTIL COLLECTION > MANTELES / INDIVIDUALES / REPASADORES': '家居纺织',
    'TEXTIL COLLECTION > CUBRECAMAS/MANTAS': '家居纺织',
    'TEXTIL COLLECTION > FELPUDOS': '家居纺织',
    'TEXTIL COLLECTION > FUNDAS': '家居纺织',
    'TEXTIL COLLECTION > ALMOHADON CON RELLENO': '家居纺织',
    'TEXTIL COLLECTION > 70X120CM COSTADO DE CAMA': '家居纺织',
    'TEXTIL COLLECTION > 50X80CM COSTADO DE CAMA': '家居纺织',
    'TEXTIL COLLECTION > 120X180CM COSTADO DE CAMA': '家居纺织',
    'TEXTIL COLLECTION > 60X90CM COSTADO DE CAMA': '家居纺织',
    'TEXTIL COLLECTION > 40X60CM COSTADO DE CAMA': '家居纺织',
    'TEXTIL COLLECTION > 90X150CM COSTADO DE CAMA': '家居纺织',
    'TEXTIL COLLECTION > 70X140CM COSTADO DE CAMA': '家居纺织',
    'TEXTIL COLLECTION > DELANTAL COCINA': '家居纺织',
    'TEXTIL COLLECTION > CAMINOS': '家居纺织',
    'TEXTIL COLLECTION > MARROQUINERIA': '箱包配件',
    
    # WINE COLLECTION → 餐饮用品
    'WINE COLLECTION > SACACORCHOS': '餐饮用品',
    'WINE COLLECTION > SETS DE ACCESORIOS': '餐饮用品',
    'WINE COLLECTION > PETACAS': '餐饮用品',
    'WINE COLLECTION > DECANTADORES': '餐饮用品',
    'WINE COLLECTION > TAPONES / CORTAGOTAS': '餐饮用品',
    
    # OFFICE COLLECTION → 文具办公
    'OFFICE COLLECTION > CENICEROS': '其他',
    'OFFICE COLLECTION > LAPICERAS': '文具办公',
    'OFFICE COLLECTION > DECO OFFICE': '文具办公',
    'OFFICE COLLECTION > SETS OFFICE': '文具办公',
    
    # Coc. Bazar → 厨房
    'Coc. Bazar > COOKING / SERVING': '厨房炊具',
    'Coc. Bazar > ORGANIZADORES': '收纳整理',
    'Coc. Bazar > FRASCOS Y JARRAS': '厨房储物',
    'Coc. Bazar > UTENSILIOS DE SILICONA': '厨房炊具',
    'Coc. Bazar > UTENSILIOS DE ACERO': '厨房炊具',
    'Coc. Bazar > UTENSILIOS DE PLASTICO': '厨房炊具',
    'Coc. Bazar > UTENSILIOS DE MADERA': '厨房炊具',
    'Coc. Bazar > CUCHILLERIA / CUBIERTOS': '厨房餐具',
    'Coc. Bazar > CAFE/TE/DESAYUNO': '餐饮用品',
    'Coc. Bazar > TETERAS Y ACCESORIOS': '餐饮用品',
    'Coc. Bazar > BANDEJAS': '厨房餐具',
    'Coc. Bazar > COLADORES Y ESCURRIDORES': '厨房炊具',
    'Coc. Bazar > A-V-S-P Y ESPECIEROS': '厨房储物',
    'Coc. Bazar > INDIVIDUALES Y POSA FUENT': '厨房餐具',
    'Coc. Bazar > REPOSTERIA': '厨房炊具',
    'Coc. Bazar > CONTENEDORES Y LUNCHERAS': '餐饮用品',
    'Coc. Bazar > ESCURRIDOR PLATOS Y PAÃ‘OS': '厨房餐具',
    'Coc. Bazar > TERMOS / VASOS TERMICOS': '餐饮用品',
    'Coc. Bazar > WINE & DRINKS': '餐饮用品',
    'Coc. Bazar > ACCESORIOS': '厨房餐具',
    'Coc. Bazar > ACRILICO': '厨房储物',
    'Coc. Bazar > SUSHI': '厨房餐具',
    'Coc. Bazar > RALLADORES/MANDOLINAS': '厨房炊具',
    
    # BAZAR → 厨房
    'BAZAR > CUBIERTOS': '厨房餐具',
    'BAZAR > MOLDES BANDEJAS Y TAPERS > MOLDES': '厨房炊具',
    'BAZAR > MOLDES BANDEJAS Y TAPERS > TAPERS': '厨房储物',
    'BAZAR > MOLDES BANDEJAS Y TAPERS': '厨房储物',
    'BAZAR > TAPERS': '厨房储物',
    'BAZAR > OTROS': '其他',
    'BAZAR > UTENSILIOS': '厨房炊具',
    'BAZAR > BOTELLAS Y TERMOS': '餐饮用品',
    'BAZAR > PLATOS Y BOWLS': '厨房餐具',
    'BAZAR > VASOS': '餐饮用品',
    
    # Deco Hogar → 装饰品
    'Deco Hogar > FLORES ART. CON MACETA': '装饰品',
    'Deco Hogar > MACETERO DECO': '装饰品',
    'Deco Hogar > ORGANIZADORES': '收纳整理',
    'Deco Hogar > PIEDRAS DECO': '装饰品',
    'Deco Hogar > PARA TU VIAJE': '旅行用品',
    'Deco Hogar > FLORES ART. SUELTAS': '装饰品',
    'Deco Hogar > PORTA RETRATOS': '装饰品',
    'Deco Hogar > NAVIDAD': '圣诞用品',
    'Deco Hogar > DECORACION INTERIORES': '装饰品',
    'Deco Hogar > EXTERIOR': '园艺户外',
    'Deco Hogar > ALMOHADONES': '家居纺织',
    'Deco Hogar > CENTROS DE MESA': '装饰品',
    
    # Porcelana/PORCELANA/CERÁMICA → 厨房餐具
    'Porcelana > MUGS Y BOWLS DECO': '厨房餐具',
    'Porcelana > PORCELANA BLANCO': '厨房餐具',
    'Porcelana > PORCELANA COLORIDA': '厨房餐具',
    'Porcelana > TETERAS DE PORCELANA': '餐饮用品',
    'Porcelana > UTILITARIOS': '厨房餐具',
    'PORCELANA/CERÁMICA > FUENTES PORCELANA': '厨房餐具',
    'PORCELANA/CERÁMICA > MUGS': '厨房餐具',
    'PORCELANA/CERÁMICA > JUEGOS DE VAJILLA': '厨房餐具',
    'PORCELANA/CERÁMICA > COPETINEROS': '厨房餐具',
    'PORCELANA/CERÁMICA > BOWLS': '厨房餐具',
    'PORCELANA/CERÁMICA > PORCELANA CON MADERA': '厨房餐具',
    'PORCELANA/CERÁMICA > SWEET HOME': '厨房餐具',
    
    # 陶瓷瓷器 → 厨房餐具
    '陶瓷瓷器 > 白瓷': '厨房餐具',
    '陶瓷瓷器 > 装饰杯碗': '厨房餐具',
    '陶瓷瓷器 > 瓷茶壶': '餐饮用品',
    '陶瓷瓷器 > 佛罗伦萨系列': '厨房餐具',
    '陶瓷瓷器 > 餐具套装': '厨房餐具',
    '陶瓷瓷器 > 实用瓷器': '厨房餐具',
    '陶瓷瓷器 > 彩色瓷器': '厨房餐具',
    
    # Cristalería → 餐饮用品
    'Cristalería > COPAS': '餐饮用品',
    'Cristalería > FLOREROS': '装饰品',
    'Cristalería > CARAMELERA /PORTA VELA': '厨房餐具',
    'Cristalería > UTILITARIOS': '厨房餐具',
    
    # 玻璃器皿 → 厨房餐具/装饰品
    '玻璃器皿 > 花瓶': '装饰品',
    '玻璃器皿 > 糖果罐烛台': '厨房餐具',
    '玻璃器皿 > 酒杯': '餐饮用品',
    '玻璃器皿 > 蛋糕托盘': '厨房餐具',
    '玻璃器皿 > 实用器皿': '厨房餐具',
    
    # Baño → 卫浴用品
    'Baño > ORGANIZADORES': '卫浴用品',
    'Baño > CESTOS Y COMPLEMENTOS': '卫浴用品',
    'Baño > ESPEJOS': '美妆个护',
    'Baño > ALFOMBRAS': '卫浴用品',
    'Baño > COSMETICOS Y ACC': '美妆个护',
    'Baño > SET BAÃ‘O MESADA': '卫浴用品',
    'Baño > DISPENSER / VAPORIZADORES': '卫浴用品',
    
    # ILUMINACIÓN → 照明灯具
    'ILUMINACIÓN > OTROS': '照明灯具',
    'ILUMINACIÓN > VELADORES': '照明灯具',
    'ILUMINACIÓN > ARBOLES LED': '照明灯具',
    
    # LIBRERÍA → 文具办公
    'LIBRERÍA > BOLÍGRAFOS > ANIMADOS': '文具办公',
    'LIBRERÍA > BOLÍGRAFOS > COLORES': '文具办公',
    'LIBRERÍA > NOTAS ADHESIVAS Y BLOCK DE PAPEL > NOTAS ADHESIVAS': '文具办公',
    'LIBRERÍA > TIJERAS Y CUTTER': '文具办公',
    
    # JUGUETERÍA → 玩具游戏
    'JUGUETERÍA > NIÑAS Y NIÑOS': '玩具游戏',
    
    # MARROQUINERÍA → 箱包配件
    'MARROQUINERÍA > BOLSOS Y CARTERAS > BOLSOS': '箱包配件',
    'MARROQUINERÍA > MOCHILAS > ADULTOS': '箱包配件',
    'MARROQUINERÍA > NECESER PORTACOSMÉTICOS': '美妆个护',
    'MARROQUINERÍA > BOLSOS TERMICOS': '箱包配件',
    'MARROQUINERÍA > VIAJES > ALMOHADAS': '旅行用品',
    
    # BELLEZA Y CUIDADO PERSONAL → 美妆个护
    'BELLEZA Y CUIDADO PERSONAL > ACCESORIOS PARA EL CABELLO > CEPILLOS DE CABELLO': '美妆个护',
    'BELLEZA Y CUIDADO PERSONAL > ACCESORIOS DE MAQUILLAJE > ESPONJAS DE MAQUILLAJE': '美妆个护',
    'BELLEZA Y CUIDADO PERSONAL > OTROS': '美妆个护',
    
    # HOGAR Y DECORACIÓN → 家居
    'HOGAR Y DECORACIÓN > ALFOMBRAS': '家居纺织',
    'HOGAR Y DECORACIÓN > ORGANIZADORES > CESTO': '收纳整理',
    'HOGAR Y DECORACIÓN > ORGANIZADORES > PLEGABLES': '收纳整理',
    'HOGAR Y DECORACIÓN > LIMPIEZA > CEPILLOS Y ESPONJAS': '清洁用品',
    'HOGAR Y DECORACIÓN > MUEBLES > ESTANTES': '家居家具',
    
    # JARDINERÍA Y EXTERIORES → 园艺户外
    'JARDINERÍA Y EXTERIORES > OTROS': '园艺户外',
    
    # DIA DE LA MADRE → 时尚配饰
    'DIA DE LA MADRE > ACCESORIOS DE MODA': '时尚配饰',
    
    # OPORTUNIDADES PANDA → 其他
    'OPORTUNIDADES PANDA > HASTA EL 40% > HOGAR': '日用百货',
    
    # 已有中文分类但带子分类的 → 取父分类
    '厨房餐具 > 杯子': '厨房餐具',
    '厨房餐具 > 厨房用品': '厨房餐具',
    '厨房餐具 > 锅具烤盘': '厨房炊具',
    '厨房餐具 > 调料厨房配件': '厨房餐具',
    '厨房餐具 > 餐盘碗碟': '厨房餐具',
    '厨房餐具 > 刀具餐具': '厨房餐具',
    '厨房餐具 > 烘焙模具': '厨房炊具',
    '厨房餐具 > 茶壶茶具': '餐饮用品',
    '厨房餐具 > 咖啡茶饮': '餐饮用品',
    '厨房餐具 > 保温杯保温壶': '餐饮用品',
    '厨房餐具 > 保鲜盒便当盒': '厨房储物',
    '厨房餐具 > 收纳整理': '收纳整理',
    '厨房餐具 > 滤网沥水架': '厨房餐具',
    '厨房餐具 > 不锈钢厨具': '厨房炊具',
    '厨房餐具 > 餐巾纸架': '厨房餐具',
    '厨房餐具 > 刨丝切菜器': '厨房炊具',
    '厨房餐具 > 烹饪服务': '厨房炊具',
    '厨房餐具 > 水瓶': '餐饮用品',
    '厨房餐具 > 餐具厨具': '厨房餐具',
    '厨房餐具 > 餐垫': '厨房餐具',
    '厨房餐具 > 硅胶厨具': '厨房炊具',
    '厨房餐具 > 木制厨具': '厨房炊具',
    '厨房餐具 > 托盘': '厨房餐具',
    '厨房餐具 > 不粘涂层厨具': '厨房炊具',
    '厨房餐具 > 酒具饮品': '餐饮用品',
    '厨房餐具 > 厨房配件': '厨房餐具',
    '厨房餐具 > 寿司餐具': '厨房餐具',
    '厨房餐具 > 塑料厨具': '厨房炊具',
    '厨房餐具 > 收纳铁罐': '厨房储物',
    '厨房餐具 > 马黛茶具': '餐饮用品',
    '厨房餐具 > 亚克力器皿': '厨房餐具',
    '厨房餐具 > 调料架': '厨房餐具',
    '厨房餐具 > 瓶罐水壶': '餐饮用品',
    
    '文具办公 > 其他': '文具办公',
    '文具办公 > 笔记本': '文具办公',
    '文具办公 > 手工材料': '文具办公',
    '文具办公 > 彩色笔': '文具办公',
    '文具办公 > 文件夹': '文具办公',
    '文具办公 > 橡皮削笔刀': '文具办公',
    '文具办公 > 记号笔': '文具办公',
    '文具办公 > 胶水': '文具办公',
    '文具办公 > 笔袋': '文具办公',
    '文具办公 > 记事本': '文具办公',
    '文具办公 > 便签本': '文具办公',
    '文具办公 > 笔筒': '文具办公',
    '文具办公 > 便利贴': '文具办公',
    '文具办公 > 桌面收纳': '文具办公',
    '文具办公 > 胶带': '文具办公',
    '文具办公 > 荧光笔': '文具办公',
    '文具办公 > 回形针': '文具办公',
    '文具办公 > 夹子回形针': '文具办公',
    '文具办公 > 彩色铅笔': '文具办公',
    '文具办公 > 卡通圆珠笔': '文具办公',
    '文具办公 > 圆珠笔': '文具办公',
    '文具办公 > 可擦笔': '文具办公',
    '文具办公 > 尺子胶水': '文具办公',
    '文具办公 > 铅笔自动铅笔': '文具办公',
    '文具办公 > 贴纸': '文具办公',
    '文具办公 > 纸张': '文具办公',
    '文具办公 > 文具套装': '文具办公',
    '文具办公 > 蜡笔': '文具办公',
    '文具办公 > 削笔刀': '文具办公',
    '文具办公 > 图钉': '文具办公',
    '文具办公 > 文具小件': '文具办公',
    '文具办公 > 标签贴': '文具办公',
    '文具办公 > 橡皮筋': '文具办公',
    '文具办公 > 水彩颜料': '文具办公',
    '文具办公 > 涂色本': '文具办公',
    '文具办公 > 计划本': '文具办公',
    '文具办公 > 记号笔荧光笔': '文具办公',
    '文具办公 > 套装': '文具办公',
    '文具办公 > 打孔机': '文具办公',
    '文具办公 > 日记本': '文具办公',
    '文具办公 > 白板黑板': '文具办公',
    '文具办公 > 迷你打印机': '文具办公',
    '文具办公 > 活页文件夹': '文具办公',
    '文具办公 > 笔袋笔筒': '文具办公',
    '文具办公 > 胶带座': '文具办公',
    '文具办公 > 计算器': '文具办公',
    '文具办公 > 订书机': '文具办公',
    '文具办公 > 订书机打孔机': '文具办公',
    '文具办公 > 信封': '文具办公',
    '文具办公 > 文件夹信封': '文具办公',
    '文具办公 > 印章': '文具办公',
    '文具办公 > 胶带贴纸': '文具办公',
    '文具办公 > 订书钉': '文具办公',
    '文具办公 > 橡皮': '文具办公',
    '文具办公 > 绘画用品': '文具办公',
    
    '家居收纳 > 收纳整理': '收纳整理',
    '家居收纳 > 挂钩衣架': '收纳整理',
    '家居收纳 > 其他': '收纳整理',
    '家居收纳 > 折叠收纳': '收纳整理',
    '家居收纳 > 收纳篮': '收纳整理',
    '家居收纳 > 收纳架': '收纳整理',
    '家居收纳 > 晾衣架': '收纳整理',
    
    '箱包配件 > 背包': '箱包配件',
    '箱包配件 > 化妆包': '箱包配件',
    '箱包配件 > 其他': '箱包配件',
    '箱包配件 > 行李箱': '箱包配件',
    '箱包配件 > 儿童书包': '箱包配件',
    '箱包配件 > 手提包': '箱包配件',
    '箱包配件 > 成人背包': '箱包配件',
    '箱包配件 > 保温袋': '箱包配件',
    '箱包配件 > 单肩包': '箱包配件',
    '箱包配件 > 钱包零钱包': '箱包配件',
    '箱包配件 > 腰包': '箱包配件',
    '箱包配件 > 购物袋': '箱包配件',
    '箱包配件 > 零钱包': '箱包配件',
    '箱包配件 > 儿童包': '箱包配件',
    '箱包配件 > 钱包': '箱包配件',
    '箱包配件 > 运动包': '箱包配件',
    
    '时尚配饰 > 其他': '时尚配饰',
    '时尚配饰 > 钥匙扣': '时尚配饰',
    '时尚配饰 > 镜子': '时尚配饰',
    '时尚配饰 > 内衣': '时尚配饰',
    '时尚配饰 > 仿珠宝饰品': '时尚配饰',
    '时尚配饰 > 首饰盒': '时尚配饰',
    '时尚配饰 > 雨伞': '时尚配饰',
    '时尚配饰 > 帽子手套': '时尚配饰',
    '时尚配饰 > 围巾头巾': '时尚配饰',
    
    '浴室用品 > 其他': '卫浴用品',
    '浴室用品 > 收纳整理': '卫浴用品',
    '浴室用品 > 配件': '卫浴用品',
    '浴室用品 > 收纳篮': '卫浴用品',
    '浴室用品 > 浴室套装': '卫浴用品',
    '浴室用品 > 镜子': '美妆个护',
    '浴室用品 > 分装瓶喷雾': '卫浴用品',
    '浴室用品 > 浴室地毯': '卫浴用品',
    '浴室用品 > 美妆配件': '美妆个护',
    '浴室用品 > 壁挂分装器': '卫浴用品',
    '浴室用品 > 浴帘': '卫浴用品',
    
    '家居清洁 > 清洁用品': '清洁用品',
    '家居清洁 > 刷子': '清洁用品',
    '家居清洁 > 胶水粘合剂': '其他',
    '家居清洁 > 垃圾桶': '清洁用品',
    '家居清洁 > 刷子海绵': '清洁用品',
    
    '家居装饰 > 仿真花': '装饰品',
    '家居装饰 > 其他': '装饰品',
    '家居装饰 > 时钟': '装饰品',
    '家居装饰 > 陶瓷花瓶': '装饰品',
    '家居装饰 > 装饰画': '装饰品',
    '家居装饰 > 相框装饰画': '装饰品',
    '家居装饰 > 装饰摆件': '装饰品',
    '家居装饰 > 桌面摆件': '装饰品',
    '家居装饰 > 仿真盆栽': '装饰品',
    '家居装饰 > 花盆': '装饰品',
    '家居装饰 > 烛台': '装饰品',
    '家居装饰 > 铁罐磁铁': '装饰品',
    '家居装饰 > 圣诞装饰': '圣诞用品',
    '家居装饰 > 香薰烛台': '装饰品',
    '家居装饰 > 室内装饰': '装饰品',
    '家居装饰 > 相框': '装饰品',
    '家居装饰 > 香薰蜡烛': '装饰品',
    '家居装饰 > 抱枕': '家居纺织',
    '家居装饰 > 窗帘': '家居纺织',
    '家居装饰 > 装饰石': '装饰品',
    
    '家居百货 > 套装组合': '日用百货',
    '家居百货 > 打火机燃气': '其他',
    '家居百货 > 其他': '日用百货',
    '家居百货 > 园艺用品': '园艺户外',
    
    '派对用品 > 其他': '派对用品',
    '派对用品 > 万圣节装饰': '派对用品',
    '派对用品 > 纪念品': '派对用品',
    '派对用品 > 礼品袋礼盒': '派对用品',
    '派对用品 > 万圣节面具服装': '派对用品',
    '派对用品 > 彩旗纸花': '派对用品',
    '派对用品 > 生日派对': '派对用品',
    '派对用品 > 气球蜡烛': '派对用品',
    '派对用品 > 万圣节': '派对用品',
    '派对用品 > 派对庆典': '派对用品',
    '派对用品 > 邀请卡': '派对用品',
    '派对用品 > 万圣节面具': '派对用品',
    '派对用品 > 宝宝派对': '派对用品',
    
    '玩具 > 儿童玩具': '玩具游戏',
    '玩具 > 玩具游戏': '玩具游戏',
    '玩具 > 减压益智': '玩具游戏',
    '玩具 > 婴儿玩具': '婴幼儿用品',
    '玩具 > 儿童节专区': '玩具游戏',
    '玩具 > 其他': '玩具游戏',
    
    '数码科技 > 电池': '数码科技',
    '数码科技 > 手机配件': '数码科技',
    '数码科技 > 风扇': '电器电子',
    '数码科技 > 耳机音响': '数码科技',
    
    '季节商品 > 秋冬保暖': '季节商品',
    '季节商品 > 夏季玩水': '季节商品',
    
    '运动户外 > 自行车配件': '运动户外',
    '运动户外 > 健身器材': '运动户外',
    '运动户外 > 钓鱼弹弓': '运动户外',
    '运动户外 > 户外露营': '运动户外',
    '运动户外 > 体育用品': '运动户外',
    '运动户外 > 其他': '运动户外',
    
    '婴幼儿用品 > 奶瓶奶嘴': '婴幼儿用品',
    '婴幼儿用品 > 其他': '婴幼儿用品',
    
    '宠物用品 > 其他': '宠物用品',
    '宠物用品 > 宠物包': '宠物用品',
    '宠物用品 > 宠物玩具': '宠物用品',
    '宠物用品 > 梳子剪甲刀': '宠物用品',
    '宠物用品 > 项圈牵引绳': '宠物用品',
    '宠物用品 > 宠物床': '宠物用品',
    '宠物用品 > 食盆水盆': '宠物用品',
    '宠物用品 > 宠物梳子': '宠物用品',
    
    '园艺户外 > 其他': '园艺户外',
    '园艺户外 > 植物支架': '园艺户外',
    '园艺户外 > 花盆': '装饰品',
    '园艺户外 > 装饰摆件': '装饰品',
    '园艺户外 > 风铃': '装饰品',
    '园艺户外 > 仿真植物': '装饰品',
    
    '五金工具 > 胶带捆扎': '五金工具',
    '五金工具 > 工具配件': '五金工具',
    '五金工具 > 润滑剂胶棒': '五金工具',
    '五金工具 > 润滑油': '五金工具',
    '五金工具': '五金工具',
    
    '照明灯具 > LED面板灯': '照明灯具',
    '照明灯具 > 灯泡灯具': '照明灯具',
    '照明灯具 > 台灯': '照明灯具',
    '照明灯具 > 灯带': '照明灯具',
    '照明灯具 > 其他': '照明灯具',
    '照明灯具 > 工矿灯射灯': '照明灯具',
    '照明灯具 > LED装饰灯': '照明灯具',
    '照明灯具 > 水晶球灯': '照明灯具',
    '照明灯具 > LED蜡烛灯': '照明灯具',
    '照明灯具 > 装饰灯': '照明灯具',
    '照明灯具 > 应急灯': '照明灯具',
    '照明灯具': '照明灯具',
    
    '鞋履护理 > 护鞋用品': '鞋履护理',
    '鞋履护理': '鞋履护理',
    
    '针线缝纫 > 缝纫材料': '针线缝纫',
    
    '家居家具 > 其他': '家居家具',
    '家居家具 > 置物架': '家居家具',
    '家居家具 > 桌子': '家居家具',
    '家居家具 > 梯子': '家居家具',
    
    '家居纺织 > 地毯': '家居纺织',
    '家居纺织 > 枕头枕套': '家居纺织',
    '家居纺织 > 毯子': '家居纺织',
    '家居纺织 > 床上用品': '家居纺织',
    '家居纺织 > 毛巾': '家居纺织',
    '家居纺织 > 其他': '家居纺织',
    
    '旅行用品 > 其他': '旅行用品',
    '旅行用品 > 旅行枕': '旅行用品',
    '旅行用品 > 收纳袋': '旅行用品',
    
    '服装服饰 > 其他': '服装服饰',
    
    '圣诞用品 > LED灯串': '圣诞用品',
    '圣诞用品 > 圣诞树装饰': '圣诞用品',
    '圣诞用品 > 声光装饰': '圣诞用品',
    '圣诞用品 > 装饰标牌': '圣诞用品',
    '圣诞用品 > 圣诞树': '圣诞用品',
    '圣诞用品 > 带灯圣诞树': '圣诞用品',
    '圣诞用品 > 水晶球灯': '圣诞用品',
    '圣诞用品 > 装饰玩偶': '圣诞用品',
    '圣诞用品 > 装饰贴纸': '圣诞用品',
    
    '美妆个护 > 化妆工具': '美妆个护',
    '美妆个护 > 个人卫生': '美妆个护',
    '美妆个护 > 其他': '美妆个护',
    '美妆个护 > 美甲美足': '美妆个护',
    '美妆个护 > 化妆收纳': '美妆个护',
    '美妆个护 > 梳子': '美妆个护',
    '美妆个护 > 发圈发夹': '美妆个护',
    '美妆个护 > 化妆海绵': '美妆个护',
    '美妆个护 > 发饰': '美妆个护',
    '美妆个护 > 旅行分装瓶': '美妆个护',
    '美妆个护 > 足部护理': '美妆个护',
    '美妆个护 > 指甲剪': '美妆个护',
    '美妆个护 > 指甲锉': '美妆个护',
    
    '食品饮料': '食品饮料',
}

# 执行映射
updated = 0
unmapped = {}
for cat, cnt in all_cats:
    if cat in standard_cats:
        continue  # 已经是标准分类
    if cat in category_mapping:
        new_cat = category_mapping[cat]
        cur.execute("UPDATE products SET category=%s WHERE category=%s", (new_cat, cat))
        updated += cur.rowcount
        print(f"  '{cat}' → '{new_cat}' ({cur.rowcount} 条)")
    else:
        unmapped[cat] = cnt
        print(f"  ❌ 未映射: '{cat}' ({cnt} 条)")

conn.commit()
print(f"\n已更新 {updated} 条")
print(f"未映射分类: {len(unmapped)} 个")

if unmapped:
    print("\n未映射的分类列表:")
    for cat, cnt in sorted(unmapped.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt}")

# 最终分类统计
cur.execute("""
    SELECT category, COUNT(*) FROM products
    WHERE category IS NOT NULL AND category != ''
    GROUP BY category ORDER BY COUNT(*) DESC
""")
final_cats = cur.fetchall()
print(f"\n最终分类数: {len(final_cats)} 个")
for cat, cnt in final_cats:
    print(f"  {cat}: {cnt}")

conn.close()
