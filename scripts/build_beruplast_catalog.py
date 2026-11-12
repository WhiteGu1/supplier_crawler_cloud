# -*- coding: utf-8 -*-
"""
scripts/build_beruplast_catalog.py
专门构建 Beruplast 花盆与园艺塑料用品目录 (方式 C：高清实物特写 + 原版规格条目行截图)
品名、价格、截图 100% 精准一一对应，不依赖通用解析器
"""
import fitz
from PIL import Image
import json
import os
import re
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.db_manager import DatabaseManager

PDF_PATH = os.path.join(ROOT_DIR, "downloads", "whatsapp", "20261024", "1.Lista Beruplast Abril 2026.pdf")
JSON_PATH = os.path.join(ROOT_DIR, "scratch_pages_ocr.json")
IMG_DIR = os.path.join(ROOT_DIR, "images", "beruplast_19")
os.makedirs(IMG_DIR, exist_ok=True)


def clean_num(txt: str) -> float:
    t = re.sub(r"[^\d,\.]", "", txt or "")
    if not t:
        return 0.0
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".")
    elif "," in t:
        t = t.replace(",", ".")
    try:
        return float(t)
    except Exception:
        m = re.findall(r"\d+\.?\d*", t)
        return float(m[0]) if m else 0.0


def extract_price_from_text(txt: str) -> float:
    # 查找批发价: 表格一般顺序为: 品名 Bulto $ 批发价 $ 零售价(PVP)
    # 取第一个出现的合法金额
    prices = re.findall(r"\$\s*([\d\.,]+)", txt)
    if prices:
        for p in prices:
            val = clean_num(p)
            if val > 0:
                return val
    # 兜底查找小数
    floats = re.findall(r"\b\d{1,3}(?:\.\d{3})*,\d{2}\b", txt)
    if floats:
        return clean_num(floats[0])
    return 0.0


def build_composite(
    doc: fitz.Document,
    page_num: int,
    pot_bbox: tuple,
    header_bbox: tuple,
    row_bbox: tuple,
    out_path: str,
):
    """
    方式 C：
    上半部分 (约 65% 高度) 为该款花盆高清实物摄影图；
    下半部分 (约 35% 高度) 为该商品在原版 PDF 中的表头与条目行截图。
    """
    pix = doc[page_num - 1].get_pixmap(dpi=200)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    s = 200 / 150  # 坐标缩放比率

    # 裁剪实物图
    px0, py0, px1, py1 = pot_bbox
    pot = img.crop((int(px0 * s), int(py0 * s), int(px1 * s), int(py1 * s)))

    # 裁剪表头与数据行
    hx0, hy0, hx1, hy1 = header_bbox
    rx0, ry0, rx1, ry1 = row_bbox

    # 统一横向宽度裁剪以保持表格边框对齐
    tx0 = min(hx0, rx0)
    tx1 = max(hx1, rx1)

    header = img.crop((int(tx0 * s), int(hy0 * s), int(tx1 * s), int(hy1 * s)))
    row = img.crop((int(tx0 * s), int(ry0 * s), int(tx1 * s), int(ry1 * s)))

    comp = Image.new("RGB", (600, 600), (255, 255, 255))

    # 顶部实物图
    pot_h = 430
    comp.paste(pot.resize((600, pot_h)), (0, 0))

    # 底部表格图
    target_table_w = 560
    h_sc = header.resize((target_table_w, max(22, int(header.height * target_table_w / header.width))))
    r_sc = row.resize((target_table_w, max(26, int(row.height * target_table_w / row.width))))

    tot_table_h = h_sc.height + r_sc.height
    avail_h = 600 - pot_h
    start_y = pot_h + max(5, (avail_h - tot_table_h) // 2)

    comp.paste(h_sc, (20, start_y))
    comp.paste(r_sc, (20, start_y + h_sc.height))

    comp.save(out_path, "JPEG", quality=95)


def run():
    print("[1/4] 加载 OCR 数据与 PDF 文档...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        pages_ocr = json.load(f)

    doc = fitz.open(PDF_PATH)
    products = []

    # ── Page 2: Uovo 自吸水花盆 ──────────────────────────
    p2_pot = (20, 120, 1220, 840)
    p2_header = (585, 915, 1220, 945)
    p2_items = [
        ("uovo_chico", "Maceta Uovo Chico Individual", 24386.49, (585, 948, 1220, 980), "Macetas > Autorriego"),
        ("uovo_mediano", "Maceta Uovo Mediano Individual", 37880.59, (585, 984, 1220, 1016), "Macetas > Autorriego"),
        ("uovo_grande", "Maceta Uovo Grande Individual", 51211.82, (585, 1018, 1220, 1052), "Macetas > Autorriego"),
    ]
    for slug, name, price, rbox, cat in p2_items:
        products.append({"page": 2, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p2_pot, "header": p2_header, "row": rbox})

    # ── Page 3: Autorriego & Riga ──────────────────────────
    p3_pot1 = (20, 25, 1220, 480)
    p3_h1 = (20, 495, 660, 525)
    p3_items1 = [
        ("autorriego_1", "Maceta Autorriego N° 1", 829.24, (20, 524, 660, 552), "Macetas > Autorriego"),
        ("autorriego_2", "Maceta Autorriego N° 2", 1461.71, (20, 550, 660, 578), "Macetas > Autorriego"),
        ("autorriego_3", "Maceta Autorriego N° 3", 1879.13, (20, 578, 660, 606), "Macetas > Autorriego"),
        ("autorriego_4", "Maceta Autorriego N° 4", 2775.29, (20, 606, 660, 633), "Macetas > Autorriego"),
        ("autorriego_5", "Maceta Autorriego N° 5", 3940.08, (20, 633, 660, 660), "Macetas > Autorriego"),
        ("auto_jardinera_20", "Auto. Jardinera 20", 2526.57, (20, 660, 660, 688), "Jardineras > Autorriego"),
        ("set_autorriego_caja", "Set Autorriego - Caja", 18809.41, (20, 688, 660, 715), "Macetas > Autorriego"),
    ]
    for slug, name, price, rbox, cat in p3_items1:
        products.append({"page": 3, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p3_pot1, "header": p3_h1, "row": rbox})

    p3_pot2 = (20, 920, 1220, 1480)
    p3_h2 = (20, 1375, 660, 1405)
    p3_items2 = [
        ("riga_9", "Riga Autorriego 9", 1408.18, (20, 1403, 660, 1430), "Macetas > Riga"),
        ("riga_13", "Riga Autorriego 13", 2552.32, (20, 1430, 660, 1458), "Macetas > Riga"),
        ("riga_17", "Riga Autorriego 17", 4987.29, (20, 1458, 660, 1485), "Macetas > Riga"),
        ("riga_21", "Riga Autorriego 21", 7040.88, (20, 1485, 660, 1513), "Macetas > Riga"),
        ("riga_25", "Riga Autorriego 25", 11588.12, (20, 1513, 660, 1540), "Macetas > Riga"),
        ("riga_29", "Riga Autorriego 29", 14375.13, (20, 1540, 660, 1568), "Macetas > Riga"),
        ("riga_35", "Riga Autorriego 35", 23469.60, (20, 1568, 660, 1595), "Macetas > Riga"),
        ("riga_jardinera_25", "Riga Jardinera 25", 4840.03, (20, 1595, 660, 1622), "Jardineras > Riga"),
        ("riga_jardinera_35", "Riga Jardinera 35", 7519.63, (20, 1622, 660, 1650), "Jardineras > Riga"),
        ("riga_jardinera_45", "Riga Jardinera 45", 10758.59, (20, 1650, 660, 1678), "Jardineras > Riga"),
    ]
    for slug, name, price, rbox, cat in p3_items2:
        products.append({"page": 3, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p3_pot2, "header": p3_h2, "row": rbox})

    # ── Page 4: Nórdicas & Regaderas ──────────────────────────
    p4_pot1 = (20, 25, 1220, 780)
    p4_h1 = (20, 795, 710, 825)
    p4_items1 = [
        ("nordica_12", "Maceta Nórdica Enlozada 12", 2008.38, (20, 840, 710, 870), "Macetas > Nórdicas"),
        ("nordica_17", "Maceta Nórdica Enlozada 17", 3286.43, (20, 885, 710, 915), "Macetas > Nórdicas"),
        ("nordica_19", "Maceta Nórdica Enlozada 19", 4564.49, (20, 930, 710, 960), "Macetas > Nórdicas"),
        ("nordica_22", "Maceta Nórdica Enlozada 22", 6099.91, (20, 978, 710, 1008), "Macetas > Nórdicas"),
    ]
    for slug, name, price, rbox, cat in p4_items1:
        products.append({"page": 4, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p4_pot1, "header": p4_h1, "row": rbox})

    p4_pot2 = (20, 1150, 1220, 1720)
    p4_h2 = (20, 1598, 710, 1625)
    products.append({"page": 4, "slug": "regadera_2_5l", "name": "Regadera Apilable 2,5 litros", "price": 3136.99, "cat": "Jardinería > Regaderas", "pot": p4_pot2, "header": p4_h2, "row": (20, 1640, 710, 1670)})

    # ── Page 5: Línea Wood (Símil Madera & Facetado) ─────────
    p5_pot1 = (20, 25, 1220, 520)
    p5_h1 = (20, 985, 710, 1015)
    p5_items1 = [
        ("simil_madera_10", "Símil Madera 10", 860.65, (20, 1015, 710, 1045), "Macetas > Wood"),
        ("simil_madera_12", "Símil Madera 12", 1098.74, (20, 1045, 710, 1075), "Macetas > Wood"),
        ("simil_madera_16", "Símil Madera 16", 1816.33, (20, 1075, 710, 1105), "Macetas > Wood"),
        ("simil_madera_20", "Símil Madera 20", 2634.87, (20, 1105, 710, 1135), "Macetas > Wood"),
        ("simil_madera_24", "Símil Madera 24", 3185.65, (20, 1135, 710, 1165), "Macetas > Wood"),
        ("simil_madera_28", "Símil Madera 28", 4146.91, (20, 1165, 710, 1195), "Macetas > Wood"),
        ("simil_madera_35", "Símil Madera 35", 7280.90, (20, 1192, 710, 1222), "Macetas > Wood"),
    ]
    for slug, name, price, rbox, cat in p5_items1:
        products.append({"page": 5, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p5_pot1, "header": p5_h1, "row": rbox})

    p5_h2 = (20, 1505, 710, 1535)
    p5_items2 = [
        ("facetado_madera_12", "Facetado Madera 12", 1090.71, (20, 1538, 710, 1568), "Macetas > Wood"),
        ("facetado_madera_15", "Facetado Madera 15", 1473.96, (20, 1568, 710, 1598), "Macetas > Wood"),
        ("facetado_madera_18", "Facetado Madera 18", 2461.54, (20, 1598, 710, 1625), "Macetas > Wood"),
        ("facetado_madera_21", "Facetado Madera 21", 2873.26, (20, 1625, 710, 1655), "Macetas > Wood"),
    ]
    for slug, name, price, rbox, cat in p5_items2:
        products.append({"page": 5, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p5_pot1, "header": p5_h2, "row": rbox})

    # ── Page 6: Clásicas & Eco Recicladas ─────────────────────
    p6_pot1 = (20, 25, 1220, 560)
    p6_h1 = (20, 660, 660, 686)
    p6_items1 = [
        ("maceta_clasica_6", "Maceta Clásica 6", 154.77, (20, 686, 660, 714), "Macetas > Clásicas"),
        ("maceta_clasica_8", "Maceta Clásica 8", 241.70, (20, 714, 660, 740), "Macetas > Clásicas"),
        ("maceta_clasica_10", "Maceta Clásica 10", 460.49, (20, 740, 660, 765), "Macetas > Clásicas"),
        ("maceta_clasica_12", "Maceta Clásica 12", 664.51, (20, 765, 660, 792), "Macetas > Clásicas"),
        ("maceta_clasica_14", "Maceta Clásica 14", 901.11, (20, 792, 660, 818), "Macetas > Clásicas"),
        ("maceta_clasica_16", "Maceta Clásica 16", 1210.03, (20, 818, 660, 845), "Macetas > Clásicas"),
        ("maceta_clasica_18", "Maceta Clásica 18", 1552.10, (20, 845, 660, 871), "Macetas > Clásicas"),
        ("maceta_clasica_21", "Maceta Clásica 21", 1989.88, (20, 871, 660, 898), "Macetas > Clásicas"),
        ("maceta_clasica_24", "Maceta Clásica 24", 2653.37, (20, 898, 660, 924), "Macetas > Clásicas"),
        ("maceta_clasica_32", "Maceta Clásica 32", 5333.44, (20, 922, 660, 952), "Macetas > Clásicas"),
    ]
    for slug, name, price, rbox, cat in p6_items1:
        products.append({"page": 6, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p6_pot1, "header": p6_h1, "row": rbox})

    p6_pot2 = (20, 960, 1220, 1370)
    p6_h2 = (20, 1380, 660, 1410)
    p6_items2 = [
        ("eco_reciclada_6", "Eco Reciclada 6", 131.55, (20, 1410, 660, 1437), "Macetas > Eco"),
        ("eco_reciclada_8", "Eco Reciclada 8", 206.57, (20, 1437, 660, 1464), "Macetas > Eco"),
        ("eco_reciclada_10", "Eco Reciclada 10", 391.34, (20, 1464, 660, 1491), "Macetas > Eco"),
        ("eco_reciclada_12", "Eco Reciclada 12", 564.88, (20, 1491, 660, 1518), "Macetas > Eco"),
        ("eco_reciclada_14", "Eco Reciclada 14", 765.88, (20, 1518, 660, 1545), "Macetas > Eco"),
        ("eco_reciclada_16", "Eco Reciclada 16", 1028.42, (20, 1545, 660, 1572), "Macetas > Eco"),
        ("eco_reciclada_18", "Eco Reciclada 18", 1319.23, (20, 1572, 660, 1599), "Macetas > Eco"),
        ("eco_reciclada_21", "Eco Reciclada 21", 1691.42, (20, 1599, 660, 1625), "Macetas > Eco"),
        ("eco_reciclada_24", "Eco Reciclada 24", 2255.37, (20, 1625, 660, 1651), "Macetas > Eco"),
        ("eco_reciclada_32", "Eco Reciclada 32", 4533.39, (20, 1651, 660, 1680), "Macetas > Eco"),
    ]
    for slug, name, price, rbox, cat in p6_items2:
        products.append({"page": 6, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p6_pot2, "header": p6_h2, "row": rbox})

    # ── Page 7: Facetadas & Símil Barro ───────────────────────
    p7_pot1 = (20, 25, 1220, 560)
    p7_h1 = (20, 620, 660, 646)
    p7_items1 = [
        ("facetado_10", "Porta Facetado 10", 657.04, (20, 646, 660, 674), "Macetas > Facetadas"),
        ("facetado_12", "Porta Facetado 12", 948.44, (20, 674, 660, 702), "Macetas > Facetadas"),
        ("facetado_15", "Porta Facetado 15", 1281.71, (20, 702, 660, 730), "Macetas > Facetadas"),
        ("facetado_18", "Porta Facetado 18", 2140.47, (20, 730, 660, 758), "Macetas > Facetadas"),
        ("facetado_21", "Porta Facetado 21", 2498.48, (20, 758, 660, 786), "Macetas > Facetadas"),
        ("facetado_24", "Porta Facetado 24", 3943.63, (20, 786, 660, 813), "Macetas > Facetadas"),
        ("facetado_35", "Porta Facetado 35", 7320.26, (20, 813, 660, 843), "Macetas > Facetadas"),
    ]
    for slug, name, price, rbox, cat in p7_items1:
        products.append({"page": 7, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p7_pot1, "header": p7_h1, "row": rbox})

    p7_pot2 = (20, 960, 1220, 1390)
    p7_h2 = (20, 1408, 660, 1435)
    p7_items2 = [
        ("simil_10", "Maceta Símil 10", 748.40, (20, 1433, 660, 1462), "Macetas > Símil"),
        ("simil_12", "Maceta Símil 12", 955.43, (20, 1462, 660, 1490), "Macetas > Símil"),
        ("simil_16", "Maceta Símil 16", 1579.43, (20, 1490, 660, 1517), "Macetas > Símil"),
        ("simil_20", "Maceta Símil 20", 2291.18, (20, 1517, 660, 1544), "Macetas > Símil"),
        ("simil_24", "Maceta Símil 24", 2770.12, (20, 1544, 660, 1571), "Macetas > Símil"),
        ("simil_28", "Maceta Símil 28", 3606.02, (20, 1571, 660, 1598), "Macetas > Símil"),
        ("simil_35", "Maceta Símil 35", 6619.00, (20, 1598, 660, 1625), "Macetas > Símil"),
        ("simil_40", "Maceta Símil 40", 9875.39, (20, 1625, 660, 1652), "Macetas > Símil"),
        ("simil_50", "Maceta Símil 50", 21113.70, (20, 1652, 660, 1680), "Macetas > Símil"),
    ]
    for slug, name, price, rbox, cat in p7_items2:
        products.append({"page": 7, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p7_pot2, "header": p7_h2, "row": rbox})

    # ── Page 8: Cuadradas & Jardineras ────────────────────────
    p8_pot1 = (20, 25, 1220, 560)
    p8_h1 = (20, 650, 660, 680)
    p8_items1 = [
        ("cuadrada_6", "Maceta Cuadrada 6", 299.58, (20, 680, 660, 708), "Macetas > Cuadradas"),
        ("cuadrada_8", "Maceta Cuadrada 8", 426.13, (20, 708, 660, 738), "Macetas > Cuadradas"),
        ("cuadrada_10", "Maceta Cuadrada 10", 540.75, (20, 738, 660, 766), "Macetas > Cuadradas"),
        ("cuadrada_12", "Maceta Cuadrada 12", 802.67, (20, 766, 660, 795), "Macetas > Cuadradas"),
        ("cuadrada_14", "Maceta Cuadrada 14", 1140.04, (20, 795, 660, 824), "Macetas > Cuadradas"),
        ("cuadrada_16", "Maceta Cuadrada 16", 1446.20, (20, 824, 660, 854), "Macetas > Cuadradas"),
        ("cuadrada_18", "Maceta Cuadrada 18", 1853.42, (20, 854, 660, 883), "Macetas > Cuadradas"),
        ("cuadrada_20", "Maceta Cuadrada 20", 2375.34, (20, 883, 660, 913), "Macetas > Cuadradas"),
        ("jardinera_cuad_20", "Jardinera Cuad 20", 1641.71, (20, 913, 660, 942), "Jardineras > Cuadradas"),
    ]
    for slug, name, price, rbox, cat in p8_items1:
        products.append({"page": 8, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p8_pot1, "header": p8_h1, "row": rbox})

    p8_pot2 = (20, 960, 1220, 1420)
    p8_h2 = (20, 1535, 660, 1565)
    p8_items2 = [
        ("jardinera_mini_20", "Jardinera Mini 20", 1561.97, (20, 1565, 660, 1595), "Jardineras"),
        ("jardinera_35", "Jardinera 35", 3410.23, (20, 1595, 660, 1623), "Jardineras"),
        ("jardinera_50", "Jardinera 50", 4867.07, (20, 1623, 660, 1653), "Jardineras"),
    ]
    for slug, name, price, rbox, cat in p8_items2:
        products.append({"page": 8, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p8_pot2, "header": p8_h2, "row": rbox})

    # ── Page 9: Deco & Tutores ────────────────────────────────
    p9_pot1 = (20, 25, 1220, 500)
    p9_h1 = (20, 515, 660, 540)
    p9_items1 = [
        ("deco_circ_8", "Deco Circular 8", 841.79, (20, 540, 660, 565), "Macetas > Deco"),
        ("deco_circ_10", "Deco Circular 10", 1136.78, (20, 565, 660, 590), "Macetas > Deco"),
        ("deco_circ_12", "Deco Circular 12", 1516.41, (20, 590, 660, 615), "Macetas > Deco"),
        ("deco_circ_14", "Deco Circular 14", 2021.37, (20, 615, 660, 640), "Macetas > Deco"),
        ("deco_circ_16", "Deco Circular 16", 2442.12, (20, 640, 660, 665), "Macetas > Deco"),
        ("deco_circ_18", "Deco Circular 18", 2947.30, (20, 665, 660, 690), "Macetas > Deco"),
        ("deco_circ_24", "Deco Circular 24", 7529.45, (20, 690, 660, 716), "Macetas > Deco"),
    ]
    for slug, name, price, rbox, cat in p9_items1:
        products.append({"page": 9, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p9_pot1, "header": p9_h1, "row": rbox})

    p9_h2 = (20, 715, 660, 740)
    p9_items2 = [
        ("deco_cuad_8", "Deco Cuadrada 8", 1415.98, (20, 740, 660, 764), "Macetas > Deco"),
        ("deco_cuad_10", "Deco Cuadrada 10", 1699.16, (20, 764, 660, 789), "Macetas > Deco"),
        ("deco_cuad_12", "Deco Cuadrada 12", 2948.99, (20, 789, 660, 814), "Macetas > Deco"),
        ("deco_cuad_14", "Deco Cuadrada 14", 3209.54, (20, 814, 660, 839), "Macetas > Deco"),
        ("deco_cuad_16", "Deco Cuadrada 16", 3964.72, (20, 839, 660, 864), "Macetas > Deco"),
        ("deco_cuad_18", "Deco Cuadrada 18", 5852.67, (20, 864, 660, 890), "Macetas > Deco"),
    ]
    for slug, name, price, rbox, cat in p9_items2:
        products.append({"page": 9, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p9_pot1, "header": p9_h2, "row": rbox})

    p9_h3 = (20, 890, 660, 915)
    products.append({"page": 9, "slug": "deco_jardinera_20", "name": "Deco Jardinera 20", "price": 4186.33, "cat": "Jardineras > Deco", "pot": p9_pot1, "header": p9_h3, "row": (20, 914, 660, 940)})

    p9_pot2 = (20, 960, 1220, 1420)
    p9_h4 = (20, 1280, 660, 1305)
    p9_items3 = [
        ("cactus_tutor_2aros", "Cactus + Tutor + 2 Aros", 1978.48, (20, 1305, 660, 1332), "Jardinería > Tutores"),
        ("mariposa_tutor", "Mariposa + Tutor", 1194.41, (20, 1332, 660, 1358), "Jardinería > Tutores"),
        ("libelula_tutor", "Libélula + Tutor", 1194.41, (20, 1358, 660, 1384), "Jardinería > Tutores"),
        ("vra_grande_tutor", "VRA Grande + Tutor", 1194.41, (20, 1384, 660, 1410), "Jardinería > Tutores"),
        ("buho_tutor", "Búho + Tutor", 1194.41, (20, 1410, 660, 1435), "Jardinería > Tutores"),
        ("aro_puente", "Aro + Puente", 288.40, (20, 1435, 660, 1460), "Jardinería > Tutores"),
    ]
    for slug, name, price, rbox, cat in p9_items3:
        products.append({"page": 9, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p9_pot2, "header": p9_h4, "row": rbox})

    # ── Page 10: Ornamentadas & Bonsai ───────────────────────
    p10_pot1 = (20, 25, 1220, 560)
    p10_h1 = (20, 740, 700, 770)
    p10_items1 = [
        ("olla_caldero", "Olla Caldero", 8224.85, (20, 770, 700, 798), "Macetas > Ornamentadas"),
        ("ondulado_19", "Maceta Ondulado 19", 2719.30, (20, 798, 700, 826), "Macetas > Ornamentadas"),
        ("tulipan_24", "Maceta Tulipán 24", 3127.11, (20, 826, 700, 854), "Macetas > Ornamentadas"),
        ("tulipan_30", "Maceta Tulipán 30", 4443.24, (20, 854, 700, 882), "Macetas > Ornamentadas"),
    ]
    for slug, name, price, rbox, cat in p10_items1:
        products.append({"page": 10, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p10_pot1, "header": p10_h1, "row": rbox})

    p10_h2 = (20, 888, 700, 915)
    p10_items2 = [
        ("copa_mini", "Copa Mini con base", 3530.13, (20, 915, 700, 942), "Macetas > Copas"),
        ("copa_chica", "Copa Chica con base", 5896.80, (20, 942, 700, 970), "Macetas > Copas"),
        ("copa_mediana", "Copa Mediana con base", 8942.67, (20, 970, 700, 998), "Macetas > Copas"),
        ("copa_grande", "Copa Grande con base", 16954.53, (20, 998, 700, 1026), "Macetas > Copas"),
    ]
    for slug, name, price, rbox, cat in p10_items2:
        products.append({"page": 10, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p10_pot1, "header": p10_h2, "row": rbox})

    p10_pot2 = (20, 1020, 1220, 1480)
    p10_h3 = (20, 1545, 700, 1572)
    p10_items3 = [
        ("bonsai_redondo_2", "Bonsai Redondo 2", 1003.14, (20, 1572, 700, 1600), "Macetas > Bonsai"),
        ("bonsai_ovalado_1", "Bonsai Ovalado 1", 1738.74, (20, 1600, 700, 1628), "Macetas > Bonsai"),
        ("bonsai_ovalado_2", "Bonsai Ovalado 2", 2608.78, (20, 1628, 700, 1656), "Macetas > Bonsai"),
        ("bonsai_rectangular_2", "Bonsai Rectangular 2", 2852.35, (20, 1656, 700, 1684), "Macetas > Bonsai"),
    ]
    for slug, name, price, rbox, cat in p10_items3:
        products.append({"page": 10, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p10_pot2, "header": p10_h3, "row": rbox})

    # ── Page 11: Platos & Ménsulas & Cercos ──────────────────
    p11_pot1 = (20, 25, 1220, 560)
    p11_h1 = (20, 600, 800, 634)
    p11_items1 = [
        ("plato_8", "Plato para Maceta 8", 258.63, (20, 635, 800, 672), "Platos"),
        ("plato_12", "Plato para Maceta 12", 584.60, (20, 672, 800, 710), "Platos"),
        ("plato_14", "Plato para Maceta 14", 639.03, (20, 710, 800, 748), "Platos"),
        ("plato_16", "Plato para Maceta 16", 777.66, (20, 748, 800, 784), "Platos"),
        ("plato_18", "Plato para Maceta 18", 938.56, (20, 784, 800, 822), "Platos"),
        ("plato_20", "Plato para Maceta 20", 1097.00, (20, 822, 800, 858), "Platos"),
        ("plato_22", "Plato para Maceta 22", 1154.04, (20, 858, 800, 894), "Platos"),
        ("plato_24", "Plato para Maceta 24", 1344.64, (20, 894, 800, 932), "Platos"),
        ("plato_26", "Plato para Maceta 26", 1542.07, (20, 932, 800, 968), "Platos"),
        ("plato_28", "Plato para Maceta 28", 1720.18, (20, 968, 800, 1005), "Platos"),
        ("plato_38", "Plato para Maceta 38", 3713.38, (20, 1005, 800, 1040), "Platos"),
        ("plato_jardi_35", "Plato para Jardinera N° 35", 1949.05, (20, 1040, 800, 1076), "Platos"),
        ("plato_jardi_50", "Plato para Jardinera N° 50", 2726.58, (20, 1076, 800, 1115), "Platos"),
    ]
    for slug, name, price, rbox, cat in p11_items1:
        products.append({"page": 11, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p11_pot1, "header": p11_h1, "row": rbox})

    p11_h2 = (20, 1118, 800, 1148)
    p11_items2 = [
        ("mensula_chica_2", "Ménsula Chica N° 2", 1721.92, (20, 1148, 800, 1185), "Accesorios > Ménsulas"),
        ("mensula_mediana_3", "Ménsula Mediana N° 3", 2138.87, (20, 1185, 800, 1222), "Accesorios > Ménsulas"),
        ("mensula_grande_4", "Ménsula Grande N° 4", 3990.25, (20, 1222, 800, 1260), "Accesorios > Ménsulas"),
    ]
    for slug, name, price, rbox, cat in p11_items2:
        products.append({"page": 11, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p11_pot1, "header": p11_h2, "row": rbox})

    p11_h3 = (20, 1262, 800, 1295)
    p11_items3 = [
        ("gancho_cultivo", "Gancho Cultivo", 270.61, (20, 1295, 800, 1332), "Accesorios > Ganchos"),
        ("gancho_corto", "Gancho Corto", 406.01, (20, 1332, 800, 1370), "Accesorios > Ganchos"),
        ("gancho_rombo", "Gancho Rombo", 518.96, (20, 1370, 800, 1408), "Accesorios > Ganchos"),
        ("gancho_cultivo_pro", "Gancho Cultivo PRO", 490.06, (20, 1408, 800, 1445), "Accesorios > Ganchos"),
        ("gancho_trenzado_pro", "Gancho Trenzado PRO", 620.77, (20, 1445, 800, 1482), "Accesorios > Ganchos"),
        ("gancho_cadena_pro", "Gancho Cadena PRO", 620.77, (20, 1482, 800, 1520), "Accesorios > Ganchos"),
    ]
    for slug, name, price, rbox, cat in p11_items3:
        products.append({"page": 11, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p11_pot1, "header": p11_h3, "row": rbox})

    p11_h4 = (20, 1520, 800, 1552)
    products.append({"page": 11, "slug": "cerco_jardin_1m", "name": "Cerco Jardín x 1 Mt", "price": 4758.99, "cat": "Accesorios > Cercos", "pot": p11_pot1, "header": p11_h4, "row": (20, 1552, 800, 1592)})

    p11_h5 = (20, 1595, 800, 1625)
    products.append({"page": 11, "slug": "mini_palita_jardinera", "name": "Mini Palita Jardinera", "price": 495.17, "cat": "Accesorios > Herramientas", "pot": p11_pot1, "header": p11_h5, "row": (20, 1625, 800, 1665)})

    # ── Page 12: Floristas & Macetas Colgantes ────────────────
    p12_pot1 = (20, 25, 1220, 560)
    p12_h1 = (20, 588, 660, 614)
    p12_items1 = [
        ("florero_chico", "Florero F. Chico c/base", 2577.40, (20, 614, 660, 642), "Floristería"),
        ("florero_mediano", "Florero F. Mediano c/base", 4867.07, (20, 642, 660, 670), "Floristería"),
        ("florero_grande", "Florero F. Grande c/base", 7686.65, (20, 670, 660, 698), "Floristería"),
    ]
    for slug, name, price, rbox, cat in p12_items1:
        products.append({"page": 12, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p12_pot1, "header": p12_h1, "row": rbox})

    p12_h2 = (20, 695, 660, 720)
    p12_items2 = [
        ("cono_chico", "Cono Exhibidor Chico", 2249.03, (20, 720, 660, 748), "Floristería"),
        ("cono_mediano", "Cono Exhibidor Mediano", 4635.38, (20, 748, 660, 776), "Floristería"),
    ]
    for slug, name, price, rbox, cat in p12_items2:
        products.append({"page": 12, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p12_pot1, "header": p12_h2, "row": rbox})

    p12_h3 = (20, 775, 660, 800)
    p12_items3 = [
        ("plato_espuma_red", "Plato Espuma Red.", 507.24, (20, 800, 660, 826), "Floristería"),
        ("plato_espuma_cuad", "Plato Espuma Cuad.", 566.14, (20, 826, 660, 852), "Floristería"),
        ("base_espuma_rect", "Base Espuma Rect.", 1093.13, (20, 852, 660, 880), "Floristería"),
        ("rejilla_espuma", "Rejilla Espuma", 974.99, (20, 880, 660, 910), "Floristería"),
    ]
    for slug, name, price, rbox, cat in p12_items3:
        products.append({"page": 12, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p12_pot1, "header": p12_h3, "row": rbox})

    p12_pot2 = (20, 960, 1220, 1420)
    p12_h4 = (20, 1350, 660, 1375)
    p12_items4 = [
        ("bols_15", "Maceta Bols 15", 861.11, (20, 1375, 660, 1402), "Macetas > Colgantes"),
        ("bols_18", "Maceta Bols 18", 1028.25, (20, 1402, 660, 1428), "Macetas > Colgantes"),
        ("bols_21", "Maceta Bols 21", 1485.74, (20, 1428, 660, 1454), "Macetas > Colgantes"),
        ("bols_24", "Maceta Bols 24", 1822.75, (20, 1454, 660, 1478), "Macetas > Colgantes"),
        ("bols_28", "Maceta Bols 28", 2434.26, (20, 1478, 660, 1506), "Macetas > Colgantes"),
        ("bols_esc_18", "Maceta Bols Esc 18", 834.75, (20, 1506, 660, 1532), "Macetas > Colgantes"),
    ]
    for slug, name, price, rbox, cat in p12_items4:
        products.append({"page": 12, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p12_pot2, "header": p12_h4, "row": rbox})

    p12_h5 = (20, 1530, 660, 1558)
    products.append({"page": 12, "slug": "caldero_mensula", "name": "Caldero c/ménsula", "price": 4452.92, "cat": "Macetas > Colgantes", "pot": p12_pot2, "header": p12_h5, "row": (20, 1558, 660, 1585)})

    p12_h6 = (20, 1585, 660, 1610)
    p12_items6 = [
        ("porta_bols_cadena_15", "Porta Bols con cadena 15", 5210.09, (20, 1610, 660, 1634), "Macetas > Colgantes"),
        ("porta_bols_cadena_21", "Porta Bols con cadena 21", 6847.72, (20, 1634, 660, 1660), "Macetas > Colgantes"),
        ("porta_bols_cadena_30", "Porta Bols con cadena 30", 8743.39, (20, 1660, 660, 1688), "Macetas > Colgantes"),
    ]
    for slug, name, price, rbox, cat in p12_items6:
        products.append({"page": 12, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p12_pot2, "header": p12_h6, "row": rbox})

    # ── Page 15: Mate ─────────────────────────────────────────
    p15_pot1 = (20, 25, 1220, 560)
    p15_h1 = (20, 785, 860, 816)
    products.append({"page": 15, "slug": "mate_mafalda_pack", "name": "Mate Mafalda en Pack Individual", "price": 5339.69, "cat": "Bazar > Mate", "pot": p15_pot1, "header": p15_h1, "row": (20, 816, 860, 850)})

    p15_h2 = (20, 1020, 860, 1050)
    products.append({"page": 15, "slug": "mate_deco_pack", "name": "Mate Deco en Pack Individual", "price": 4592.14, "cat": "Bazar > Mate", "pot": p15_pot1, "header": p15_h2, "row": (20, 1050, 860, 1080)})

    p15_h3 = (20, 1250, 860, 1282)
    products.append({"page": 15, "slug": "mate_deco_bombilla", "name": "Mate Deco + Bombilla + Saca Yerba", "price": 4118.53, "cat": "Bazar > Mate", "pot": p15_pot1, "header": p15_h3, "row": (20, 1282, 860, 1314)})

    p15_h4 = (20, 1485, 860, 1515)
    products.append({"page": 15, "slug": "mate_pastel_pack", "name": "Mate Pastel en Pack Individual", "price": 4408.49, "cat": "Bazar > Mate", "pot": p15_pot1, "header": p15_h4, "row": (20, 1515, 860, 1545)})

    # ── Page 16: Vasos Deco ───────────────────────────────────
    p16_pot = (20, 50, 1220, 1200)
    p16_h = (20, 1410, 1220, 1445)
    p16_items = [
        ("vaso_500_tapa", "Vaso 500ml + Tapa", 1467.53, (20, 1450, 1220, 1488), "Bazar > Vasos"),
        ("vaso_750_tapa", "Vaso 750ml + Tapa", 1842.58, (20, 1488, 1220, 1528), "Bazar > Vasos"),
        ("vaso_deco_500_tapa", "Vaso Deco 500ml + Tapa", 2935.07, (20, 1528, 1220, 1568), "Bazar > Vasos"),
        ("vaso_deco_750_tapa", "Vaso Deco 750ml + Tapa", 3685.16, (20, 1568, 1220, 1608), "Bazar > Vasos"),
        ("vaso_mafalda_500_tapa", "Vaso Mafalda 500ml + Tapa", 3261.18, (20, 1608, 1220, 1645), "Bazar > Vasos"),
        ("vaso_mafalda_750_tapa", "Vaso Mafalda 750ml + Tapa", 4094.63, (20, 1645, 1220, 1685), "Bazar > Vasos"),
    ]
    for slug, name, price, rbox, cat in p16_items:
        products.append({"page": 16, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p16_pot, "header": p16_h, "row": rbox})

    # ── Page 17: Línea Kids & Tarros ──────────────────────────
    p17_pot1 = (20, 50, 1220, 920)
    p17_h1 = (20, 970, 1220, 1005)
    p17_items1 = [
        ("valijita_deco", "Valijita Deco", 7387.38, (20, 1005, 1220, 1045), "Bazar > Kids"),
        ("vaso_deco_330", "Vaso Deco 330ml", 1607.92, (20, 1045, 1220, 1080), "Bazar > Kids"),
        ("valijita_set_completo", "Valijita Deco + Vaso 330 + Taza + Plato", 9027.59, (20, 1080, 1220, 1115), "Bazar > Kids"),
    ]
    for slug, name, price, rbox, cat in p17_items1:
        products.append({"page": 17, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p17_pot1, "header": p17_h1, "row": rbox})

    p17_pot2 = (20, 1150, 1220, 1520)
    p17_h2 = (20, 1550, 1000, 1582)
    p17_items2 = [
        ("tarro_yerbero", "Tarro Yerbero - Picovertedor", 2035.40, (20, 1585, 1000, 1615), "Bazar > Tarros"),
        ("tarro_azucarero", "Tarro Azucarero - Picovertedor", 1871.54, (20, 1615, 1000, 1645), "Bazar > Tarros"),
        ("cuchara_matera", "Cuchara Matera", 410.42, (20, 1645, 1000, 1678), "Bazar > Accesorios"),
    ]
    for slug, name, price, rbox, cat in p17_items2:
        products.append({"page": 17, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p17_pot2, "header": p17_h2, "row": rbox})

    # ── Page 18: Conservadoras & Limpieza ─────────────────────
    p18_pot1 = (20, 25, 1220, 560)
    p18_h1 = (20, 885, 1220, 940)
    p18_items1 = [
        ("conservadora_24latas", "Conservadora Lata Gigante Grande 24 Latas", 57854.90, (20, 1050, 600, 1080), "Camping > Conservadoras"),
        ("conservadora_12latas", "Conservadora Lata Gigante Mediana 12 Latas", 37882.57, (600, 1050, 1220, 1080), "Camping > Conservadoras"),
    ]
    for slug, name, price, rbox, cat in p18_items1:
        products.append({"page": 18, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p18_pot1, "header": p18_h1, "row": rbox})

    p18_pot2 = (20, 1080, 1220, 1460)
    p18_h2 = (20, 1475, 900, 1505)
    p18_items2 = [
        ("fuenton_eco_12l", "Fuenton Eco. 12 litros", 2824.94, (20, 1505, 900, 1533), "Limpieza > Baldes"),
        ("balde_eco_10l", "Balde Eco. 10 litros", 3204.38, (20, 1533, 900, 1561), "Limpieza > Baldes"),
        ("balde_12l_reforzado", "Balde 12 Ls (reforzado)", 4246.90, (20, 1561, 900, 1589), "Limpieza > Baldes"),
    ]
    for slug, name, price, rbox, cat in p18_items2:
        products.append({"page": 18, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p18_pot2, "header": p18_h2, "row": rbox})

    p18_h3 = (20, 1588, 900, 1616)
    p18_items3 = [
        ("fuenton_12l", "Fuenton 12 litros", 3429.32, (20, 1616, 900, 1643), "Limpieza > Baldes"),
        ("balde_10l", "Balde 10 litros", 3654.04, (20, 1643, 900, 1672), "Limpieza > Baldes"),
    ]
    for slug, name, price, rbox, cat in p18_items3:
        products.append({"page": 18, "slug": slug, "name": name, "price": price, "cat": cat, "pot": p18_pot2, "header": p18_h3, "row": rbox})

    print(f"[2/4] 总计整理出 {len(products)} 个准确商品，正在逐一生成【实物特写+规格行】组合截图...")
    for idx, p in enumerate(products):
        out_name = f"{p['slug']}.jpg"
        out_path = os.path.join(IMG_DIR, out_name)
        build_composite(
            doc=doc,
            page_num=p["page"],
            pot_bbox=p["pot"],
            header_bbox=p["header"],
            row_bbox=p["row"],
            out_path=out_path,
        )
        p["image_url"] = f"/images/beruplast_19/{out_name}"
        if (idx + 1) % 20 == 0 or idx + 1 == len(products):
            print(f"  已生成截图 ({idx + 1}/{len(products)}): {p['name']} -> {p['image_url']}")

    print("[3/4] 写入 MySQL 数据库 products 表 (supplier_id = 19)...")
    db = DatabaseManager("localhost", 3306, "root", "admin123", "supplier_crawler")
    with db.connection() as conn:
        cursor = conn.cursor()
        # 清除历史商品
        cursor.execute("DELETE ph FROM price_history ph JOIN products p ON p.id=ph.product_id WHERE p.supplier_id=19")
        cursor.execute("DELETE FROM products WHERE supplier_id=19")
        conn.commit()

        inserted = 0
        for p in products:
            sku = f"BERU-{p['slug'].upper()}"
            cursor.execute(
                """
                INSERT INTO products (supplier_id, sku, name, price, category, image_url, is_available, is_new, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, 1, 1, NOW(), NOW())
                """,
                (19, sku, p["name"], p["price"], p["cat"], p["image_url"]),
            )
            pid = cursor.lastrowid
            cursor.execute(
                "INSERT INTO price_history (product_id, price, recorded_at) VALUES (%s, %s, NOW())",
                (pid, p["price"]),
            )
            inserted += 1
        conn.commit()

    print(f"[4/4] 成功录入 {inserted} 件花盆/塑料制品商品入库！")


if __name__ == "__main__":
    run()
