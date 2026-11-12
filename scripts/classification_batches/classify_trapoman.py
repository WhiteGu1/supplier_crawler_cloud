"""
Trapoman 分类脚本 — 基于商品名称逐条审查
名称置信度高的直接分类，不确定的标记 NEEDS_IMAGE 供后续图片审查
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# 分类规则（基于名称关键词匹配）
# ═══════════════════════════════════════════════════════════════

# (关键词列表, 分类)  — 按优先级从高到低
RULES = [
    # 需要图片审查的（名称含糊）
    (['BICHO RED'], 'NEEDS_IMAGE'),  # 不确定是什么
    (['ANDARIN'], 'NEEDS_IMAGE'),    # 不确定
    (['BANQUET'], 'NEEDS_IMAGE'),    # 不确定
    (['RELOJ'], 'NEEDS_IMAGE'),      # 不确定是什么类型
    (['BOLSA DE AGUA CALIENTE'], '个人防护'),  # 热水袋
    (['HAND SOAP'], '清洁用品'),
    (['BATH SPONGE'], '清洁用品'),
    (['MOPA', 'PAÑO MICROFIBRA', 'ESPONJA MICROFIBRA', 'PAÑO ALAMBRE', 'PAÑO X5 METALICO'], '清洁用品'),
    (['CEPILLO', 'LIMPIA'], '清洁用品'),
    (['ESCOBILLA'], '清洁用品'),
    (['ORGANIZADOR DE LIMPIEZA'], '清洁用品'),
    (['LIMPIADOR'], '清洁用品'),
    (['CHISPERO', 'ENCENDEDOR'], '厨房炊具'),
    (['SAHUMERIO', 'RESINAS'], '装饰品'),
    (['VELA', 'VELONCITO'], '装饰品'),
    (['HERMETICO', 'HERMETICOS', 'TAPER', 'TUPPER'], '厨房储物'),
    (['HERMETICO'], '厨房储物'),
    (['CONTENEDOR', 'SNACK BOX'], '厨房储物'),
    (['FRASCO', 'TARRO', 'ESPECIERO'], '厨房储物'),
    (['CANASTO', 'CANASTITO', 'CAJON', 'CAJA', 'CESTO', 'BOLSA PARA MASCOTA'], '收纳整理'),
    (['SARTEN', 'MOLDE', 'ASADERA', 'BUDINERA', 'TORTERA', 'PASTAFROLA', 'SAVARIN', 'PIZZERA', 'TARTERA'], '厨房炊具'),
    (['OLLA', 'CACEROLA', 'PAVA', 'CAFETERA', 'HERVIDOR', 'COLAPASTA'], '厨房炊具'),
    (['BIFERA', 'BUDINERA'], '厨房炊具'),
    (['SANDWICHERA'], '厨房炊具'),
    (['BOLSA PARA HORNO'], '厨房炊具'),
    (['DIFUSOR', 'VAPORIERA'], '厨房炊具'),
    (['CUCHARA', 'CUCHARITA', 'TENEDOR', 'CUCHILLO', 'CUBIERTO', 'CUBIERTOS', 'UNTADOR', 'ESPATULA', 'ESPUMADERA', 'CUCHARON', 'BATIDOR', 'BATEDOR', 'RALLADOR', 'SACACORCHO', 'ABRELATA', 'CORTA PIZZA', 'PELAPAPA', 'PICA AJO', 'EXPRIMIDOR', 'BATE BIFE', 'PINZA', 'PINCEL', 'TIJERA', 'CORNET', 'MANGA REPOSTERA', 'ESPIRAL DE VERDURA', 'PISAPAPA', 'FILTRO TE', 'ESPAGUETERA', 'PALA TORTA', 'PALA ALIMENTOS', 'CUCHARAS MEDIDORAS', 'HUEVERA', 'CUBIERTERO', 'PICADOR'], '厨房餐具'),
    (['SET 5 CUCHILLAS', 'SET CAROL ACERO', 'SILICONE UTENSILLS', 'SET X9 UTENSILLOS', 'SET X5 UTENSILLOS', 'SET X2 PINZA', 'SET X5 CORTANTE'], '厨房餐具'),
    (['VASO', 'TAZA', 'MUG', 'JARRA', 'JARRITO', 'BOTELLA', 'TERMO', 'CHOP', 'BOTELLON', 'BOTELLA INSULADA', 'BOTELLA METALICA', 'BOTELLA VIDRIO', 'BOTELLA JUGO', 'BOTELLA DAILY', 'BOTELLA KEEP', 'PACK TAZA', 'PACK X6 VASO', 'PACK X6 TAZAS', 'PACK X6 COPA', 'PACK X6 WHISKY', 'VASO DOBLE VIDRIO', 'VASO PLASTICO', 'VASO TE', 'VASO ALTO', 'VASO STARBUCKS', 'VASO FERNETOMETRO', 'FERNETOMETRO', 'JARRO', 'BOTELLA TERMICA', 'BOTELLA DE ACERO', 'BOTELLA DOBLE PARED'], '餐饮用品'),
    (['MATE', 'BOMBILLA', 'SACAYERBA', 'CEBANTE', 'YERBA', 'BOLSO MATERO', 'SET MATE', 'LIMPIADOR PARA BOMBILLA'], '餐饮用品'),
    (['SET 3 VASOS KIDO', 'BOTELLA KIDO', 'LUNCHERA TERMICA'], '餐饮用品'),
    (['JUEGO CUBIERTOS', 'PACK 16 CUBIERTOS', 'PACK CUBIERTOS'], '厨房餐具'),
    (['PERCHA', 'BARRAL', 'GANCHO', 'GANCHOS'], '收纳整理'),
    (['ESPEJO', 'ALFOMBRA BAÑO', 'ALFOMBRA RECTANGULAR', 'ALFOMBRA BATH', 'ALFOMBRA'], '装饰品'),
    (['CORTINA', 'MANTEL', 'INDIVIDUAL', 'PROTECTOR MAGH'], '装饰品'),
    (['ORGANIZADOR DUCHA', 'PORTA CEPILLO', 'PORTA ROLLO', 'PORTA JABON', 'DISPENSER', 'JABONERA', 'POSA JABON', 'TAPON BACHA', 'TAPA PILETA', 'REJILLA PILETA', 'PORTA TOALLA', 'PORTA TOALLA'], '卫浴用品'),
    (['FLORERO', 'FRUTERA', 'BANDEJA', 'TAZON', 'BOWL', 'ENSALADERA', 'CESTA', 'FUENTE', 'PLATO', 'RECIPIENTE'], '餐饮用品'),
    (['PLATO PLAYO', 'PLATO HONDO', 'PLATO BAMBU'], '餐饮用品'),
    (['BURBUJERO', 'BUBBLE'], '玩具游戏'),
    (['PISTOLA', 'AIR BLASTERS', 'AIR POWER', 'AIR GUN'], '玩具游戏'),
    (['MUÑECA', 'MUÑECO', 'BEBOTE', 'BABY', 'SIRENA'], '玩具游戏'),
    (['AUTO', 'CAMION', 'AUTOBUS', 'MONOPATIN', 'PATINES', 'PISTA DE AUTO', 'PISTA DE TREN', 'FORMULA 1', 'RUEDA LANZADORA', 'PISTA LANZADORA'], '玩具游戏'),
    (['PELOTA', 'PELOTITAS', 'PELOTAS', 'BOWLING', 'TIRO', 'ARO DE BASQUET', 'LANZA Y ATRAPA', 'FUTBOL TRAINING', 'ENTRENAMIENTO FUTBOL', 'ARCO DE FUTBOL', 'SET DE PALETAS', 'JUEGO LANZA PELOTA', 'BARRILETE', 'SOGA', 'RAQUETA', 'METEGOL', 'YO-YO'], '运动户外'),
    (['BINGO', 'TATETI', 'STOP', 'LUDO', 'DOMINO', 'DESCUBRI QUIEN', 'JUEGO DE MESA', 'JUEGO DE DADOS', 'HAPPY MONKEY', 'CRAZY DINO', 'SUPER GOL', 'POOL TABLE', 'JUEGO CARRERA', 'DINO AL SUELO', 'TOUCH GAME', 'CARTAS', 'BINGO AFA'], '玩具游戏'),
    (['DINOSAURIO', 'DINOS', 'HUEVO DINOSAURIO', 'ROBOT', 'TRANSFORMER', 'MONSTRUO', 'MONSTER ANIMAL', 'LEON MONSTER'], '玩具游戏'),
    (['MAQUILLAJE', 'SET BELLEZA', 'SET UÑAS', 'ESMALTE', 'LAPIZ LABIAL', 'SET BIJOUTERIE', 'BIJOUTERIE', 'SET DE ARTE', 'POP IT'], '美妆个护'),
    (['SQUISHY', 'TABLET', 'PIZARRA MAGICA', 'CELULAR BABY', 'TELEFONO BABY', 'RADIO MUSICAL', 'GUITARRA', 'TROMPETA', 'PIANITO', 'SUPER MICROFONO', 'CAJA FUERTE', 'SET JUEGO AROS', 'TORRE APILABLE', 'JUEGO DE ENCASTRE', 'ROMPECABEZA', 'JUEGO DIDACTICO', 'CONJUNTO POLICIA', 'SET BARCO PIRATA', 'ALAS MAGICAS', 'VARITA PRINCESA', 'SET DE PRINCESAS', 'FISHING GAME', 'WATER GAME', 'JUEGO MARIPOSA', 'PACK PARA ARMAR', 'SET BIJOU'], '玩具游戏'),
    (['SET ARCO Y FLECHA', 'ARCO Y FLECHA'], '玩具游戏'),
    (['MACETA'], '装饰品'),
    (['RECIPIENTE GIGANTE', 'RECIPIENTE VIDRIO'], '厨房储物'),
    (['SECAPLATO', 'SECAPLATOS'], '厨房餐具'),
    (['TACHO', 'VAIVEN', 'BALDE'], '厨房炊具'),
    (['JARRO ENLOZADO', 'JARRO CON ASA', 'PLATO ENLOZADO', 'PAVA ENLOZADA'], '厨房餐具'),
    (['BIFERA ENLOZADA'], '厨房炊具'),
    (['SET HERMETICOS VERDURAS'], '厨房储物'),
    (['BALANZA'], '厨房餐具'),
    (['PACK MUNDIAL'], '派对用品'),
    (['CUADERNO', 'SET DE ARTE'], '文具办公'),
    (['ORGANIZADOR ESCRITORIO'], '文具办公'),
    (['PASTILLERO'], '日用百货'),
    (['PARAGUA'], '日用百货'),
    (['BOLSA DE AGUA'], '个人防护'),
    (['SANDWICHERA'], '厨房炊具'),
]

# 需要图片审查的特定 ID（名称实在无法判断）
NEEDS_IMAGE_IDS = set()

def classify_by_name(name):
    """根据名称关键词分类，返回 (category, confidence)"""
    name_upper = name.upper()
    
    # 先检查 NEEDS_IMAGE 规则
    for keywords, cat in RULES:
        if cat == 'NEEDS_IMAGE':
            for kw in keywords:
                if kw.upper() in name_upper:
                    return None, 0
    
    # 常规规则匹配
    for keywords, cat in RULES:
        if cat == 'NEEDS_IMAGE':
            continue
        for kw in keywords:
            if kw.upper() in name_upper:
                return cat, 95
    
    # 无法匹配
    return None, 0

# ═══════════════════════════════════════════════════════════════
# 主逻辑
# ═══════════════════════════════════════════════════════════════

conn = pymysql.connect(
    host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler',
    charset='utf8mb4'
)
cur = conn.cursor()

# 获取所有未分类商品
cur.execute("""
    SELECT id, name, image_local
    FROM products
    WHERE supplier_id=3 AND (category IS NULL OR category='')
      AND is_available=1
    ORDER BY id
""")
rows = cur.fetchall()

classified = []
needs_image = []

for pid, name, img in rows:
    cat, conf = classify_by_name(name)
    if cat and conf >= 90:
        classified.append((pid, name, cat))
    else:
        needs_image.append((pid, name, img))

print(f"总计: {len(rows)}")
print(f"名称分类成功(>=90%): {len(classified)}")
print(f"需要图片审查: {len(needs_image)}")
print()

if needs_image:
    print("=== 需要图片审查的商品 ===")
    for pid, name, img in needs_image:
        print(f"  ID:{pid}  {name}  img={'Y' if img else 'N'}")

# 执行写入
if classified:
    print(f"\n=== 写入 {len(classified)} 条分类 ===")
    updated = 0
    for pid, name, cat in classified:
        cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
        updated += cur.rowcount
    conn.commit()
    print(f"成功写入: {updated}/{len(classified)}")
    
    # 检查剩余
    cur.execute("""
        SELECT COUNT(*) FROM products
        WHERE supplier_id=3 AND (category IS NULL OR category='')
          AND is_available=1
    """)
    remaining = cur.fetchone()[0]
    print(f"Trapoman 剩余未分类: {remaining}")

conn.close()
