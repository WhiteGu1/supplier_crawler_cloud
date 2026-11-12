# -*- coding: utf-8 -*-
"""
全库商品标准中文分类与多路径归类脚本
- 严格遵循 scripts/classification_batches/standard_categories.json 中的 270 条标准三级中文分类路径
- 将供应商网站原分类 (category) 作为辅助分类工具 (auxiliary domain scope)，结合商品西语标题进行高精度多路径映射
- 写入 product_categories 表 (多路径 1~4 条)
- 更新 products.category 为主分类路径 (严格使用 updated_at = updated_at 保持时间戳不变，避免影响补货及到货判断)
- 覆盖全部待分类商品 (包含 Randy、nativo home、sfpanda、Trapoman、Bella Central 等)
"""
import os
import sys
import json
import re
from typing import Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
STD_CATS_FILE = os.path.join(BASE_DIR, "scripts", "classification_batches", "standard_categories.json")

with open(STD_CATS_FILE, "r", encoding="utf-8") as f:
    STANDARD_CATS = json.load(f)

STD_SET = set(STANDARD_CATS)


def classify_product(name: str, raw_cat: str, brand: str = "") -> list:
    """
    结合 (raw_cat, name, brand) 映射到 1~4 个标准三级中文分类。
    网站原有分类作为 auxiliary domain scope (辅助分类工具)。
    严格保证返回的所有路径均在 standard_categories.json (270条标准路径) 中。
    """
    n = (name or "").upper()
    rc = (raw_cat or "").upper()
    cats = []

    # ----------------------------------------------------
    # 0. 精准特殊商品匹配 (马桶刷、卫浴配件、烤箱手套、工具、收纳箱等)
    # ----------------------------------------------------
    if any(w in n for w in ["INODORO", "ESCOBILLA", "CEPILLO DE BAÑO"]):
        cats.append("家居生活 > 卫浴用品 > 马桶刷")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["PAPEL HIGIENICO", "PORTA ROLLO"]):
        cats.append("家居生活 > 卫浴用品 > 马桶用品")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["RACK BAÑO", "ESTANTE BAÑO"]):
        cats.append("家居生活 > 卫浴用品 > 浴室置物架")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["BOLSAS GUARDADO", "BOLSA GUARDADO", "BOLSA AL VACIO"]):
        cats.append("家居生活 > 收纳整理 > 收纳工具")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["ANTIPARRA", "NATACION"]):
        cats.append("运动户外 > 户外装备 > 户外用品")
        cats.append("玩具 > 玩具游戏 > 户外/戏水玩具")
        return [c for c in cats if c in STD_SET]

    if "FAROL" in n:
        cats.append("电子电器 > 照明灯具 > LED灯")
        cats.append("摆件礼品 > 派对节庆 > 节庆灯饰")
        return [c for c in cats if c in STD_SET]

    if "TELEFONO" in n:
        cats.append("电子电器 > 小家电 > 小家电")
        return [c for c in cats if c in STD_SET]

    if "CAMARA" in n and "INFANTIL" in n:
        cats.append("玩具 > 玩具游戏 > 其他玩具")
        return [c for c in cats if c in STD_SET]

    if "POLIRESINA" in n:
        cats.append("摆件礼品 > 装饰摆件 > 装饰摆件")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["MANOPLA", "AGARRADERA", "GUANTE PARA HORNO"]):
        cats.append("厨房用品 > 炊具 > 厨房工具")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["HERRAMIENTA", "HERRAMIENTAS"]):
        cats.append("五金 > 五金工具 > 五金工具")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["BOLSA PARA LAVAR", "BOLSA DE LAVADO"]):
        cats.append("家居生活 > 收纳整理 > 收纳工具")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["CAJON", "CAJONES", "CAJONERA"]):
        cats.append("家居生活 > 收纳整理 > 收纳盒")
        cats.append("家居生活 > 收纳整理 > 收纳架")
        return [c for c in cats if c in STD_SET]

    if "BIROME" in n:
        cats.append("文具 > 文具办公 > 圆珠笔")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["CARTERA", "CARTERITA"]):
        cats.append("箱包皮具 > 箱包配件 > 手提包/斜挎包")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["BOLSO", "BOLSITO"]):
        cats.append("箱包皮具 > 箱包配件 > 手提包/斜挎包")
        cats.append("箱包皮具 > 旅行用品 > 旅行包")
        return [c for c in cats if c in STD_SET]

    if any(w in n for w in ["WALL DECO", "DECO GOMA EVA", "ADORNO POLI", "ADORNO"]):
        cats.append("摆件礼品 > 装饰摆件 > 装饰摆件")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 1. 圣诞 / 节日 / 派对 / COTILLON
    # ----------------------------------------------------
    if "NAVIDAD" in rc or any(w in n for w in ["NAVIDAD", "NAVIDEÑ", "PAPA NOEL", "ARBOL NAVID", "PESEBRE", "CASCANUECES", "GORRO PAPA NOEL"]):
        cats.append("摆件礼品 > 派对节庆 > 圣诞装饰")
        if any(w in n for w in ["LUZ", "LUCES", "GUIRNALDA DE LUZ", "LED"]):
            cats.append("摆件礼品 > 派对节庆 > 节庆灯饰")
        return [c for c in cats if c in STD_SET]

    if "HALLOWEEN" in rc or "HALLOWEEN" in n or "BRUJA" in n or "CALABAZA HALLOWEEN" in n:
        cats.append("摆件礼品 > 派对节庆 > 万圣节装饰")
        return [c for c in cats if c in STD_SET]

    if "COTILLON" in rc or any(w in n for w in ["COTILLON", "GLOBO", "GLOBOS", "ANTIFFAZ", "SERPENTINA", "LANZACONFETI", "CONFETI"]):
        if any(w in n for w in ["GLOBO", "GLOBOS"]):
            cats.append("摆件礼品 > 派对节庆 > 派对用品")
        elif any(w in n for w in ["REMERA", "CAMISETA"]):
            cats.append("服装鞋帽 > 服装服饰 > 雨衣/外套")
        elif any(w in n for w in ["BUFANDA"]):
            cats.append("服装鞋帽 > 服装服饰 > 围巾/披肩")
        elif any(w in n for w in ["PINTACARA"]):
            cats.append("玩具 > 玩具游戏 > 手工DIY")
        else:
            cats.append("摆件礼品 > 派对节庆 > 派对用品")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 2. 玩具品类 (JUGUET* in rc or toy keywords)
    # ----------------------------------------------------
    if "JUGUET" in rc or any(w in n for w in [
        "PISTOLA DE AGUA", "AUTITO", "CAMION", "MUÑECA", "MUÑECO", "PELUCHE", "PISTA",
        "JUEGO DE MESA", "TRUCO", "BURBUJERO", "MASA", "SLIME", "DINOSAURIO", "ROBOT",
        "SONAJERO", "LUDO", "DIDACTICO", "ROMPECABEZAS", "PUZZLE", "JUGUETE"
    ]):
        if any(w in n for w in ["PELUCHE", "OSO", "PLUSH", "PEREZOSO"]):
            cats.append("玩具 > 玩具游戏 > 毛绒玩具")
        elif any(w in n for w in ["AUTO", "CAMION", "CAMIONETA", "MOTO", "VEHICULO", "AVION", "HELICOPTERO", "CUATRICICLO", "TUNING CAR", "PISTA"]):
            cats.append("玩具 > 玩具游戏 > 玩具车")
        elif any(w in n for w in ["MUÑECA", "MUÑECO", "BEBE", "FIGURA", "LOL", "BARBIE", "SUPERHEROE", "AVENGERS", "BATMAN", "SPIDERMAN", "LEAGUE OF LEGENDS"]):
            cats.append("玩具 > 玩具游戏 > 玩偶/公仔")
        elif any(w in n for w in ["MESA", "CARTAS", "NAIPES", "TRUCO", "AJEDREZ", "DAMA", "DOMINO", "RULETA", "BINGO", "JENGA"]):
            cats.append("玩具 > 玩具游戏 > 桌游")
        elif any(w in n for w in ["ROMPECABEZAS", "PUZZLE"]):
            cats.append("玩具 > 玩具游戏 > 拼图")
        elif any(w in n for w in ["BLOQUE", "LADRILLO", "RASTI", "LEGO", "ENCASTRE", "DIDACTICO"]):
            cats.append("玩具 > 玩具游戏 > 拼装积木")
            cats.append("玩具 > 玩具游戏 > 益智玩具")
        elif any(w in n for w in ["PISTOLA DE AGUA", "INFLABLE", "LANZADOR", "FLOTADOR", "SALVAVIDAS", "ANTIPARRAS", "BURBUJERO", "PELOTA DE PLAYA"]):
            cats.append("玩具 > 玩具游戏 > 户外/戏水玩具")
        elif any(w in n for w in ["DISFRAZ", "MASCARA", "CARETA", "ALAS", "CAPA", "CORONA REINA"]):
            cats.append("玩具 > 玩具游戏 > 角色扮演")
        elif any(w in n for w in ["SLIME", "MASA", "PLASTILINA", "PINTA CARA", "PINTACARA"]):
            cats.append("玩具 > 玩具游戏 > 手工DIY")
        elif any(w in n for w in ["SONAJERO", "ANDADOR", "ARRASTRE"]):
            cats.append("玩具 > 玩具游戏 > 拖拉玩具")
        elif any(w in n for w in ["PELOTA", "FUTBOL", "BASQUET", "TENNIS", "PADEL"]):
            cats.append("玩具 > 玩具游戏 > 玩具球")
            cats.append("运动户外 > 运动健身 > 球类")
        else:
            cats.append("玩具 > 玩具游戏 > 益智玩具")
            cats.append("玩具 > 玩具游戏 > 其他玩具")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 3. 文具品类 (LIBRER* in rc or stationery keywords)
    # ----------------------------------------------------
    if "LIBRER" in rc or any(w in n for w in [
        "CUADERNO", "REPUESTO", "LIBRETA", "CARTUCHERA", "CANOPLA", "LAPICERA", "BOLIGRAFO",
        "RESALTADOR", "MARCADOR", "LAPIZ", "GOMA DE BORRAR", "SACAPUNTAS", "ABROCHADORA",
        "ABROCHADOR", "PLASTICOLA", "CORRECTOR", "REGLA", "TIJERA", "FOLIOS", "CARPETA", "BLOCK",
        "ANOTADOR", "POST IT", "NOTAS ADHESIVAS"
    ]):
        if any(w in n for w in ["CARTUCHERA", "CANOPLA", "PORTALAPIZ"]):
            cats.append("文具 > 文具办公 > 笔筒/笔袋")
        elif any(w in n for w in ["CUADERNO", "REPUESTO", "LIBRETA", "BLOCK", "AGENDA", "ANOTADOR"]):
            cats.append("文具 > 文具办公 > 便携记事本")
            cats.append("文具 > 文具办公 > 本册/文件夹")
        elif any(w in n for w in ["CARPETA", "FOLIO", "SEPARADOR", "BIBLIORATO"]):
            cats.append("文具 > 文具办公 > 本册/文件夹")
        elif any(w in n for w in ["BOLIGRAFO", "LAPICERA"]):
            cats.append("文具 > 文具办公 > 圆珠笔")
        elif any(w in n for w in ["RESALTADOR", "FIBRA", "MARCADOR", "MICROFIBRA"]):
            cats.append("文具 > 文具办公 > 马克笔/荧光笔")
        elif any(w in n for w in ["LAPIZ", "LAPICES"]):
            if any(w in n for w in ["COLOR", "COLORES", "ACUARELA", "TEMPERA", "CRAYON"]):
                cats.append("文具 > 文具办公 > 绘画用品")
            else:
                cats.append("文具 > 文具办公 > 笔类")
        elif any(w in n for w in ["GOMA", "BORRADOR"]):
            cats.append("文具 > 文具办公 > 橡皮擦")
        elif any(w in n for w in ["SACAPUNTA"]):
            cats.append("文具 > 文具办公 > 卷笔刀")
        elif any(w in n for w in ["ABROCHADORA", "GANCHO ABROCHADORA", "PERFORADORA"]):
            cats.append("文具 > 文具办公 > 办公文具")
        elif any(w in n for w in ["CORRECTOR"]):
            cats.append("文具 > 文具办公 > 修正工具")
        elif any(w in n for w in ["TIJERA"]):
            cats.append("文具 > 文具办公 > 剪刀")
        elif any(w in n for w in ["REGLA", "ESCUADRA", "TRANSPORTADOR", "COMPAS"]):
            cats.append("文具 > 文具办公 > 尺规")
        elif any(w in n for w in ["STICKER", "ETIQUETA", "AUTOADHESIVO", "PEGATINA"]):
            cats.append("文具 > 文具办公 > 贴纸/标签")
        elif any(w in n for w in ["CALCULADORA"]):
            cats.append("文具 > 文具办公 > 计算器")
        elif any(w in n for w in ["PLASTICOLA", "VOLIGOMA", "ADHESIVO", "PEGAMENTO", "CINTA ADHESIVA"]):
            cats.append("文具 > 文具办公 > 胶水/胶带")
        elif any(w in n for w in ["PINCEL", "TEMPERA", "ACUARELA", "ACRILICO", "PALETA"]):
            cats.append("文具 > 文具办公 > 绘画用品")
        else:
            cats.append("文具 > 文具办公 > 其他文具")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 4. 箱包皮具 (MARROQUINER* in rc or bag keywords)
    # ----------------------------------------------------
    if "MARROQUINER" in rc or any(w in n for w in [
        "MOCHILA", "BILLETERA", "MONEDERO", "VALIJA", "PORTA SUBE", "NECESER",
        "PORTACOSMETICO", "CANOPLA", "CARTUCHERA", "BOTINERO", "LUNCHERA"
    ]):
        if any(w in n for w in ["MOCHILA"]):
            cats.append("箱包皮具 > 箱包配件 > 背包")
        elif any(w in n for w in ["CARTUCHERA", "CANOPLA"]):
            cats.append("文具 > 文具办公 > 笔筒/笔袋")
        elif any(w in n for w in ["BILLETERA", "MONEDERO", "PORTA SUBE", "TARJETERO"]):
            cats.append("箱包皮具 > 箱包配件 > 零钱包/腰包")
        elif any(w in n for w in ["NECESER", "PORTACOSMETICO"]):
            cats.append("箱包皮具 > 箱包配件 > 化妆品包")
        elif any(w in n for w in ["LUNCHERA"]):
            cats.append("厨房用品 > 储物保鲜 > 便当盒/午餐盒")
            cats.append("箱包皮具 > 旅行用品 > 旅行包")
        elif any(w in n for w in ["BOLSO", "BOTINERO", "VALIJA", "CARRITO"]):
            cats.append("箱包皮具 > 旅行用品 > 旅行包")
        elif any(w in n for w in ["PARAGUA"]):
            cats.append("化妆品饰品 > 时尚配饰 > 雨伞/衣物")
        elif any(w in n for w in ["GUANTE", "GORRO", "BUFANDA", "PANTUMEDIA", "MEDIAS"]):
            if "GUANTE" in n:
                cats.append("服装鞋帽 > 服装服饰 > 手套")
            elif "GORRO" in n:
                cats.append("服装鞋帽 > 服装服饰 > 帽子")
            elif "MEDIAS" in n or "PANTUMEDIA" in n:
                cats.append("服装鞋帽 > 服装服饰 > 袜子")
            else:
                cats.append("服装鞋帽 > 服装服饰 > 围巾/披肩")
        elif any(w in n for w in ["ZAPATILLA", "ZAPATO", "CALZADO"]):
            cats.append("服装鞋帽 > 鞋履护理 > 鞋带")
        else:
            cats.append("箱包皮具 > 箱包配件 > 手提包/斜挎包")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 5. 美妆与时尚配饰 / 香水 (BIJOUTERIE, PERFUMERIA, DELINEADOR, MASCARA, LIMPIEZA FACIAL)
    # ----------------------------------------------------
    if any(k in rc for k in ["BIJOUTERIE", "PERFUMERIA", "DELINEADOR", "MANICURIA", "FACIAL", "SKIN CARE", "MAQUILLAJE"]) or any(w in n for w in [
        "AROS", "ARITOS", "COLLAR", "PULSERA", "ANILLO", "DIJE", "BROCHE DE PELO", "HEBILLA",
        "COLITA", "VINCHA", "TIC TAC", "PIQUITO", "INVISIBLE", "PINZA PARA PELO", "PEINE",
        "CEPILLO DE PELO", "CEPILLO PARA PELO", "BROCHA", "ESPONJA DE MAQUILLAJE", "LIMA DE UÑAS",
        "LIMAS", "DELINEADOR", "MASCARA DE PESTAÑA", "LABIAL", "LIP GLOSS", "ESMALTE", "UÑAS",
        "DEPILADOR", "ALHAJERO"
    ]):
        if any(w in n for w in ["COLITA", "BANDITA", "GOMITA", "ELASTICO", "SCRUNCHIE"]):
            cats.append("化妆品饰品 > 时尚配饰 > 发圈/皮筋")
        elif any(w in n for w in ["BROCHE DE PELO", "HEBILLA", "TIC TAC", "PIQUITO", "PINZA PARA PELO", "INVISIBLE", "CLIP PARA PELO", "PINZAS DE PELO"]):
            cats.append("化妆品饰品 > 时尚配饰 > 发夹/发卡")
        elif any(w in n for w in ["VINCHA", "TIARA", "CORONA"]):
            cats.append("化妆品饰品 > 时尚配饰 > 发箍/发饰")
        elif any(w in n for w in ["LLAVERO"]):
            cats.append("化妆品饰品 > 时尚配饰 > 钥匙扣")
        elif any(w in n for w in ["ESPEJO"]):
            cats.append("化妆品饰品 > 时尚配饰 > 镜子")
            cats.append("摆件礼品 > 装饰摆件 > 镜子")
        elif any(w in n for w in ["ALHAJERO"]):
            cats.append("化妆品饰品 > 时尚配饰 > 首饰盒")
            cats.append("摆件礼品 > 装饰摆件 > 首饰盒")
        elif any(w in n for w in ["PEINE", "CEPILLO DE PELO", "CEPILLO PARA PELO"]):
            cats.append("化妆品饰品 > 美妆个护 > 梳子/发刷")
        elif any(w in n for w in ["LIMA", "LIMAS", "UÑA", "UÑAS", "STRASS", "CORTA TIPS", "MANICURIA", "TORNO"]):
            cats.append("化妆品饰品 > 美妆个护 > 美甲工具")
        elif any(w in n for w in ["BROCHA", "ESPONJA DE MAQUILLAJE", "ESPONJA FACIAL", "ARQUEADOR", "PINZA DE DEPILAR", "APLICADOR"]):
            cats.append("化妆品饰品 > 美妆个护 > 化妆工具")
        elif any(w in n for w in ["DELINEADOR", "MASCARA DE PESTAÑA", "LABIAL", "LIP GLOSS", "SOMBRA", "RUBOR", "POLVO", "BASE", "CORRECTOR FACIAL"]):
            cats.append("化妆品饰品 > 美妆个护 > 彩妆/唇妆")
        elif any(w in n for w in ["DEPILADOR", "DEPILADORA", "AFEITADORA", "MASAJEADOR"]):
            cats.append("化妆品饰品 > 美妆个护 > 按摩/脱毛")
        elif any(w in n for w in ["CREMA", "SERUM", "MASCARILLA", "LOCION", "FACIAL", "LIMPIEZA"]):
            cats.append("化妆品饰品 > 美妆个护 > 护肤/化妆品")
        elif any(w in n for w in ["PERFUME", "COLONIA", "BODY SPLASH", "FRAGANCIA"]):
            cats.append("化妆品饰品 > 美妆个护 > 香水/香氛")
        elif any(w in n for w in ["AROS", "ARITOS", "COLLAR", "PULSERA", "ANILLO", "DIJE", "CADENA", "TOBILLERA", "GARGANILLA"]):
            cats.append("化妆品饰品 > 时尚配饰 > 首饰")
        else:
            cats.append("化妆品饰品 > 时尚配饰 > 首饰")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 6. 宠物用品 (PETS)
    # ----------------------------------------------------
    if "PETS" in rc or any(w in n for w in ["PERRO", "GATO", "MASCOTA", "PET "]):
        if any(w in n for w in ["COMEDERO", "BEBEDERO", "PLATO"]):
            cats.append("宠物 > 宠物用品 > 宠物食具")
        elif any(w in n for w in ["CAMITA", "COLCHONETA", "ALMOHADON"]):
            cats.append("宠物 > 宠物用品 > 宠物床")
        elif any(w in n for w in ["JUGUETE", "PELOTA", "MORDIDOR", "HUESO", "RASCADOR"]):
            cats.append("宠物 > 宠物用品 > 宠物护理/玩具")
        else:
            cats.append("宠物 > 宠物用品 > 宠物用品")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 7. 五金工具 (FERRETERIA)
    # ----------------------------------------------------
    if "FERRETERIA" in rc or any(w in n for w in [
        "DESTORNILLADOR", "PINZA", "MARTILLO", "LLAVE", "ALICATE", "NIVEL", "CANDADO",
        "CINTA METRICA", "CUTTER", "TRINCHETA", "CINTA AISLADORA", "TOPE DE PUERTA"
    ]):
        if any(w in n for w in ["CINTA METRICA", "METRO"]):
            cats.append("五金 > 五金工具 > 测量工具")
        elif any(w in n for w in ["CUTTER", "TRINCHETA"]):
            cats.append("五金 > 五金工具 > 美工刀")
        elif any(w in n for w in ["CANDADO", "CERRADURA"]):
            cats.append("五金 > 五金工具 > 锁具")
        elif any(w in n for w in ["TOPE DE PUERTA", "FRENO DE PUERTA"]):
            cats.append("五金 > 五金工具 > 门吸/门塞")
        elif any(w in n for w in ["CINTA AISLADORA", "CINTA"]):
            cats.append("五金 > 五金工具 > 胶带")
        else:
            cats.append("五金 > 五金工具 > 五金工具")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 8. 雨伞 / 遮阳伞
    # ----------------------------------------------------
    if "PARAGUA" in rc or "PARAGUA" in n or "PILOTO" in n:
        if "PILOTO" in n:
            cats.append("服装鞋帽 > 服装服饰 > 雨衣/外套")
        else:
            cats.append("化妆品饰品 > 时尚配饰 > 雨伞/衣物")
            cats.append("家居生活 > 园艺户外 > 遮阳伞")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 9. 地毯 / 地垫 (ALFOMBRAS, FELPUDO)
    # ----------------------------------------------------
    if "ALFOMBRA" in rc or any(w in n for w in ["ALFOMBRA", "FELPUDO", "PISOBELLA"]):
        cats.append("家居生活 > 家居装饰 > 地毯/地垫")
        cats.append("家居生活 > 卫浴用品 > 浴室地垫")
        cats.append("家居生活 > 家纺毛巾 > 地毯")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 10. 卫浴用品 (BAÑO)
    # ----------------------------------------------------
    if "BAÑO" in rc or any(w in n for w in ["JABONERA", "PORTACEPILLO", "CORTINA DE BAÑO", "ESCOBILLA", "DISPENSER DE JABON"]):
        if any(w in n for w in ["ESCOBILLA"]):
            cats.append("家居生活 > 卫浴用品 > 马桶刷")
        elif any(w in n for w in ["JABONERA"]):
            cats.append("家居生活 > 卫浴用品 > 皂盒")
        elif any(w in n for w in ["DISPENSER"]):
            cats.append("家居生活 > 卫浴用品 > 皂液器")
        elif any(w in n for w in ["CORTINA"]):
            cats.append("家居生活 > 卫浴用品 > 浴帘")
        else:
            cats.append("家居生活 > 卫浴用品 > 浴室套装")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 11. 摆件 / 礼品 / 家居装饰 / 相框 / 镜子 / 时钟 / 花瓶 / 香薰 (HOGAR Y DECO, REGALERIA, ESPEJOS, PORTARRETRATOS)
    # ----------------------------------------------------
    if any(k in rc for k in ["HOGAR", "REGALERIA", "DECO", "HORNITO", "ESPEJO", "PORTARRETRATO", "FLORERO", "VELA"]) or any(w in n for w in [
        "PORTARRETRATO", "PORTAFOTO", "PORTA RETRATO", "CUADRO", "MARCO", "ESPEJO", "RELOJ",
        "FLORERO", "JARRON", "PORTAVELA", "CANDELABRO", "FANAL", "VELA", "VELAS", "HORNITO",
        "HORNILLO", "DIFUSOR", "ESENCIA", "AROMATIZADOR", "PLANTA", "FLOR", "RAMA", "MACETA",
        "SUCULENTA", "CACTUS", "ALMOHADON", "FUNDA", "CANASTO", "CESTO", "RATTAN", "SEAGRASS",
        "PERCHA", "GANCHO", "ORGANIZADOR", "VELADOR", "LAMPARA", "LUZ", "LUCES", "APLIQUE"
    ]):
        if any(w in n for w in ["PORTARRETRATO", "PORTARRETRATOS", "PORTAFOTO", "PORTA RETRATO", "CUADRO", "MARCO"]):
            cats.append("摆件礼品 > 装饰摆件 > 相框")
        elif any(w in n for w in ["ESPEJO"]):
            cats.append("摆件礼品 > 装饰摆件 > 镜子")
            cats.append("化妆品饰品 > 时尚配饰 > 镜子")
        elif any(w in n for w in ["FLORERO", "JARRON"]):
            cats.append("摆件礼品 > 装饰摆件 > 花瓶")
        elif any(w in n for w in ["PLANTA", "FLOR", "RAMA", "MACETA", "SUCULENTA", "CACTUS"]):
            cats.append("家居生活 > 园艺户外 > 人造植物")
            cats.append("摆件礼品 > 装饰摆件 > 花盆/植物")
        elif any(w in n for w in ["PORTAVELA", "CANDELABRO", "FANAL", "PORTAVELAS"]):
            cats.append("摆件礼品 > 装饰摆件 > 烛台/蜡烛")
        elif any(w in n for w in ["VELA", "VELAS"]):
            cats.append("摆件礼品 > 装饰摆件 > 烛台/蜡烛")
        elif any(w in n for w in ["HORNITO", "HORNILLO", "DIFUSOR", "ESENCIA", "AROMATIZADOR"]):
            cats.append("摆件礼品 > 装饰摆件 > 香薰")
            cats.append("摆件礼品 > 装饰摆件 > 香薰/加湿器")
        elif any(w in n for w in ["RELOJ"]):
            cats.append("摆件礼品 > 装饰摆件 > 时钟")
            cats.append("家居生活 > 家居装饰 > 挂钟")
        elif any(w in n for w in ["ALHAJERO"]):
            cats.append("摆件礼品 > 装饰摆件 > 首饰盒")
        elif any(w in n for w in ["ALMOHADON", "FUNDA DE ALMOHADON", "FUNDA ALMOHADON"]):
            cats.append("家居生活 > 家纺毛巾 > 靠垫抱枕")
        elif any(w in n for w in ["PERCHA", "PERCHAS", "GANCHO", "COLGADOR"]):
            cats.append("家居生活 > 收纳整理 > 挂钩/衣架")
        elif any(w in n for w in ["CESTO PARA ROPA", "CESTO", "CANASTO", "CANASTA", "SEAGRASS", "RATTAN"]):
            cats.append("家居生活 > 收纳整理 > 收纳篮")
            cats.append("摆件礼品 > 装饰摆件 > 收纳篮")
        elif any(w in n for w in ["ORGANIZADOR BAJO MESADA", "ORGANIZADOR DE BACHA"]):
            cats.append("家居生活 > 收纳整理 > 收纳架")
            cats.append("厨房用品 > 储物保鲜 > 水槽置物架")
        elif any(w in n for w in ["ORGANIZADOR DE COSMETICO", "ORGANIZADOR DE MAQUILLAJE", "ORGANIZADOR ACRILICO"]):
            cats.append("化妆品饰品 > 美妆个护 > 化妆收纳")
            cats.append("家居生活 > 收纳整理 > 收纳盒")
        elif any(w in n for w in ["ORGANIZADOR", "CAJA"]):
            cats.append("家居生活 > 收纳整理 > 收纳盒")
        elif any(w in n for w in ["BALDE"]):
            cats.append("家居生活 > 清洁用品 > 垃圾袋/垃圾桶")
            cats.append("家居生活 > 清洁用品 > 清洁工具")
        elif any(w in n for w in ["CEPILLO C/ MANGO", "CEPILLO"]):
            cats.append("家居生活 > 清洁用品 > 清洁刷")
        elif any(w in n for w in ["APOYA FUENTE", "INDIVIDUAL", "MANTELES", "MANTEL", "CAMINO DE MESA"]):
            cats.append("厨房用品 > 餐具 > 桌布餐垫")
            cats.append("厨房用品 > 餐具 > 杯垫/隔热垫")
        elif any(w in n for w in ["LUCES", "LED", "LAMPARA", "VELADOR", "GUIRNALDA", "APLIQUE"]):
            cats.append("电子电器 > 照明灯具 > LED灯")
            cats.append("摆件礼品 > 派对节庆 > 节庆灯饰")
        else:
            cats.append("摆件礼品 > 装饰摆件 > 装饰摆件")
            cats.append("家居生活 > 家居装饰 > 桌面摆件")
        return [c for c in cats if c in STD_SET]

    # ----------------------------------------------------
    # 12. 厨房用品 / BAZAR / 餐饮水具 / 餐具 / 炊具 / 储物 (BAZAR, VIDRIO, ACERO, COCINA, CERAMICA, OPORTUNIDADES)
    # ----------------------------------------------------
    # 马黛茶具
    if any(w in n for w in ["MATE", "MATERO", "BOMBILLA", "SET MATERO"]):
        cats.append("厨房用品 > 餐饮水具 > 马黛茶具")
    # 酒具 / 杯类
    elif any(w in n for w in ["COPA", "VASO DE TRAGO", "CHAMPAGNERA", "HIELERA", "COCTELERA", "LICORERA", "PETACA", "WHISKY"]):
        cats.append("厨房用品 > 餐饮水具 > 酒具")
        if "COPA" in n:
            cats.append("厨房用品 > 餐饮水具 > 酒杯")
    elif any(w in n for w in ["TAZA", "VASO", "JARRO", "MUG", "CHOPP"]):
        cats.append("厨房用品 > 餐饮水具 > 杯子")
        cats.append("厨房用品 > 餐具 > 杯子")
    # 水壶 / 水杯 / 保温杯
    elif any(w in n for w in ["TERMO", "JARRO TERMICO"]):
        cats.append("厨房用品 > 餐饮水具 > 保温杯")
    elif any(w in n for w in ["BOTELLA", "BOTELLITA", "BIDON"]):
        cats.append("厨房用品 > 餐饮水具 > 水瓶/水壶")
    elif any(w in n for w in ["JARRA", "TETERA", "CAFETERA", "HERVIDOR"]):
        cats.append("厨房用品 > 餐饮水具 > 壶/水罐")
        if "TETERA" in n or "CAFETERA" in n:
            cats.append("厨房用品 > 餐饮水具 > 咖啡器具")
    # 盘子 / 碗 / 餐具
    elif any(w in n for w in ["PLATO", "PLATOS", "FUENTE"]):
        cats.append("厨房用品 > 餐具 > 盘子")
    elif any(w in n for w in ["BOWL", "COMPOTERA", "ENSALADERA", "TAZON"]):
        cats.append("厨房用品 > 餐具 > 碗/盆")
        cats.append("厨房用品 > 餐具 > 沙拉碗")
    elif any(w in n for w in ["CUBIERTO", "CUCHARA", "CUCHILLO", "TENEDOR", "CUCHARON"]):
        cats.append("厨房用品 > 餐具 > 刀叉勺")
    elif any(w in n for w in ["BANDEJA", "TABLA DE SERVIR", "PLATO GIRATORIO"]):
        cats.append("厨房用品 > 餐具 > 托盘")
    elif any(w in n for w in ["INDIVIDUAL", "MANTELES", "MANTEL", "CAMINO DE MESA", "APOYA FUENTE"]):
        cats.append("厨房用品 > 餐具 > 桌布餐垫")
        cats.append("厨房用品 > 餐具 > 杯垫/隔热垫")
    elif any(w in n for w in ["SERVILLETERO"]):
        cats.append("厨房用品 > 餐具 > 其他餐具")
    elif any(w in n for w in ["AZUCARERA", "CONDIMENTERO", "ESPECIERO", "SALERO", "PIMENTERO", "ACEITERO", "ACEITERA", "CONDIMENTOS", "SET CONDIMENTOS"]):
        cats.append("厨房用品 > 餐具 > 糖罐/调料罐")
        cats.append("厨房用品 > 餐具 > 调味器")
    # 储物保鲜
    elif any(w in n for w in ["FRASCO", "HERMETICO", "CONTENEDOR", "TUPPER", "POTE", "CARAMELERA"]):
        cats.append("厨房用品 > 储物保鲜 > 玻璃储物罐" if ("VIDRIO" in n or "VIDRIO" in rc) else "厨房用品 > 储物保鲜 > 保鲜盒/储物罐")
        if "CARAMELERA" in n:
            cats.append("厨房用品 > 餐具 > 果盘")
    elif any(w in n for w in ["CUBETERA", "HIELERA", "MOLDE DE HIELO"]):
        cats.append("厨房用品 > 储物保鲜 > 冰格")
    elif any(w in n for w in ["ESCURRIDOR", "SECAPLATOS", "ORGANIZADOR DE BACHA"]):
        cats.append("厨房用品 > 储物保鲜 > 水槽置物架")
        cats.append("厨房用品 > 餐具 > 沥水架")
    # 炊具 / 厨具
    elif any(w in n for w in ["SARTEN", "OLLA", "PANQUEQUERA", "WOK", "CACEROLA"]):
        cats.append("厨房用品 > 炊具 > 平底锅/煎锅" if "SARTEN" in n else "厨房用品 > 炊具 > 锅具")
    elif any(w in n for w in ["MOLDE"]):
        cats.append("厨房用品 > 炊具 > 模具/烤模")
    elif any(w in n for w in ["COLADOR", "TAMIZADOR", "TAMIZADORES", "ESPUMADERA"]):
        cats.append("厨房用品 > 炊具 > 滤网/漏勺")
    elif any(w in n for w in ["TABLA DE PICAR", "TABLA DE CORTE", "TABLA MADERA", "TABLA BAMBU"]):
        cats.append("厨房用品 > 炊具 > 切菜板")
    elif any(w in n for w in ["ABRELATAS", "SACACORCHOS"]):
        cats.append("厨房用品 > 炊具 > 开瓶器/开罐器")
    elif any(w in n for w in ["RALLADOR"]):
        cats.append("厨房用品 > 炊具 > 刨丝器/榨汁器")
    elif any(w in n for w in ["PELAPAPAS", "PELADOR"]):
        cats.append("厨房用品 > 炊具 > 削皮器")
    elif any(w in n for w in ["ESPATULA", "PALA DE TORTA", "PALA P/ FIDEOS"]):
        cats.append("厨房用品 > 炊具 > 硅胶铲")
        cats.append("厨房用品 > 炊具 > 烘焙工具")
    elif any(w in n for w in ["CORTAPIZZA"]):
        cats.append("厨房用品 > 炊具 > 刀具")
        cats.append("厨房用品 > 炊具 > 厨房工具")
    elif any(w in n for w in ["CUCHILLA", "CUCHILLAS", "SET CUCHILLOS"]):
        cats.append("厨房用品 > 炊具 > 刀具")
        cats.append("厨房用品 > 炊具 > 刀具套装")
    elif any(w in n for w in ["PINZA DE COCINA", "PINZA"]):
        cats.append("厨房用品 > 餐具 > 夹子")
    elif any(w in n for w in ["PISAPAPA"]):
        cats.append("厨房用品 > 炊具 > 压泥器")
    elif any(w in n for w in ["TACHO", "TACHOS", "CESTO"]):
        cats.append("家居生活 > 收纳整理 > 垃圾桶")
        cats.append("家居生活 > 清洁用品 > 垃圾袋/垃圾桶")
    elif any(w in n for w in ["ENCENDEDOR"]):
        cats.append("家居生活 > 日用杂货 > 打火机")
    elif any(w in n for w in ["OJOTAS", "CROCS"]):
        cats.append("家居生活 > 卫浴用品 > 其他卫浴")
        cats.append("家居生活 > 日用杂货 > 其他杂货")
    else:
        # 通用百货兜底
        if "VIDRIO" in rc:
            cats.append("厨房用品 > 餐具 > 盘子")
            cats.append("厨房用品 > 储物保鲜 > 玻璃储物罐")
        elif "COCINA" in rc or "ACERO" in rc or "BAZAR" in rc:
            cats.append("厨房用品 > 炊具 > 厨房工具")
        elif "DECO" in rc or "REGALERIA" in rc:
            cats.append("摆件礼品 > 装饰摆件 > 装饰摆件")
        else:
            cats.append("家居生活 > 日用杂货 > 其他杂货")

    valid_cats = [c for c in cats if c in STD_SET]
    return valid_cats


DEFAULT_FALLBACK_CAT = next(
    (c for c in ["家居生活 > 日用杂货 > 其他杂货", "家居生活 > 日用百货 > 日用杂货"] if c in STD_SET),
    STANDARD_CATS[0],
)


def classify_pending_products(db, supplier_id: Optional[int] = None, batch_size: int = 200) -> dict:
    """
    Incremental standard-category classification compatible with both local MySQL and remote TiDB.
    Only touches products whose primary category is missing/non-standard or lacks product_categories rows,
    and preserves updated_at via `updated_at = updated_at`.
    """
    where_clause = "WHERE p.supplier_id = %s" if supplier_id is not None else ""
    params = (int(supplier_id),) if supplier_id is not None else ()

    with db.connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT p.id, p.supplier_id, s.name AS supplier_name, p.name, p.category, p.brand,
                   (CASE WHEN pc.product_id IS NULL THEN 1 ELSE 0 END) AS missing_pc
            FROM products p
            JOIN suppliers s ON s.id = p.supplier_id
            LEFT JOIN (SELECT DISTINCT product_id FROM product_categories) pc ON pc.product_id = p.id
            {where_clause}
            ORDER BY p.supplier_id ASC, p.id ASC
            """,
            params,
        )
        candidates = cur.fetchall()
        cur.close()

    targets = []
    for r in candidates:
        cat = (r["category"] or "").strip()
        if (cat not in STD_SET) or (r["missing_pc"] == 1):
            targets.append(r)

    print(f"扫描待处理商品总数: {len(targets)} 件", flush=True)
    if targets:
        sup_counts = {}
        for t in targets:
            sname = t["supplier_name"]
            sup_counts[sname] = sup_counts.get(sname, 0) + 1
        for sname, cnt in sorted(sup_counts.items(), key=lambda x: -x[1]):
            print(f"  - {sname.ljust(20)}: {cnt:5d} 件", flush=True)

    if not targets:
        print("未发现待分类商品，分类体系已完备！", flush=True)
        return {"pending": 0, "updated_products": 0, "written_paths": 0}

    total = len(targets)
    total_written_paths = 0
    total_updated_products = 0

    with db.connection() as conn:
        cur_write = conn.cursor()
        for start in range(0, total, batch_size):
            chunk = targets[start:start + batch_size]
            pids = []
            pc_rows = []
            upd_rows = []
            for item in chunk:
                pid = item["id"]
                cats = [c for c in classify_product(item["name"], item["category"], item["brand"]) if c in STD_SET]
                if not cats:
                    cats = [DEFAULT_FALLBACK_CAT]
                pids.append(pid)
                for c in cats:
                    pc_rows.append((pid, c))
                upd_rows.append((cats[0], pid))

            placeholders = ",".join(["%s"] * len(pids))
            cur_write.execute(f"DELETE FROM product_categories WHERE product_id IN ({placeholders})", tuple(pids))
            if pc_rows:
                cur_write.executemany(
                    "INSERT IGNORE INTO product_categories (product_id, category) VALUES (%s, %s)",
                    pc_rows,
                )
            if upd_rows:
                cur_write.executemany(
                    "UPDATE products SET category = %s, updated_at = updated_at WHERE id = %s",
                    upd_rows,
                )
            conn.commit()
            total_written_paths += len(pc_rows)
            total_updated_products += len(upd_rows)
            done = min(start + batch_size, total)
            print(f"  已处理: {done}/{total} ({done * 100 / total:.1f}%) | 已写入多路径: {total_written_paths} 条", flush=True)
        cur_write.close()

    return {
        "pending": total,
        "updated_products": total_updated_products,
        "written_paths": total_written_paths,
    }


def main():
    from database.db_manager import DatabaseManager

    print("=================================================================")
    print(" 启动全库商品标准中文分类与多路径归类")
    print(f" 标准分类库: {len(STD_SET)} 条标准三级中文路径")
    print("=================================================================")

    db = DatabaseManager.from_env(default_password=os.getenv("DB_PASSWORD", ""))
    stats = classify_pending_products(db)

    print("\n=================================================================")
    print(" 全库商品标准中文分类与多路径归类完成！")
    print(f" 更新商品主分类: {stats['updated_products']} 件")
    print(f" 写入多路径关系: {stats['written_paths']} 条")
    print("=================================================================")


if __name__ == "__main__":
    main()
