# -*- coding: utf-8 -*-
"""
LP 供应商 PDF 解析器 (Durax / Rigolleau 等同格式目录)
4列布局，每列一个商品块结构：
  Precio: $ <价格>
  ;CA x <包装数>
  Articulo :
  [Marca/s: <编号> -] <SKU>
  [Artículos Sin Prec]  (可选，无价格商品标记)
  <商品名称行1>
  <商品名称行2(可选)>
  <品牌名(DURAX/RIGOLLEAU/ENVASES RIGO等)>
图片在每个商品块上方（54x66px）
"""

import re
import io
from collections import defaultdict

PARSER_NAME = "lp — 目录解析 (4列标准目录)"
PARSER_DESC = "适用于 Durax/Rigolleau 等同格式目录PDF，4列布局，Precio+SKU+名称+品牌"


def parse(pdf_path: str, images_dir: str, supplier_id: int) -> list:
    """解析 LP 格式 PDF 目录，返回商品列表"""
    import pdfplumber

    all_products = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            if not words:
                continue
            all_products.extend(_parse_page(page, images_dir, supplier_id))
    return all_products


def _clean_price(text: str) -> float:
    """清理价格文本: '2771,98' → 2771.98, '10.048,70' → 10048.70"""
    text = re.sub(r'[^\d\.,]', '', text)
    if re.search(r'\d+\.\d{3},\d{2}', text):
        text = text.replace('.', '').replace(',', '.')
    elif re.search(r'\d+,\d{2}$', text):
        text = text.replace(',', '.')
    elif ',' in text:
        text = text.replace(',', '.')
    nums = re.findall(r'\d+\.?\d*', text)
    return float(nums[0]) if nums else 0.0


# 4列 x 边界（页面宽度 595px）
COL_BOUNDS = [(0, 145), (145, 290), (290, 435), (435, 595)]

def _get_col(x0: float) -> int:
    for i, (lo, hi) in enumerate(COL_BOUNDS):
        if lo <= x0 < hi:
            return i
    return 3


# 已知品牌名（全大写），用于从名称中排除
BRAND_NAMES = {'DURAX', 'RIGOLLEAU', 'ENVASES', 'RIGO'}


def _is_brand_line(text: str) -> bool:
    """判断是否为品牌行"""
    t = text.strip().upper()
    # 品牌行：纯品牌名 或 "ENVASES RIGO"
    for brand in BRAND_NAMES:
        if t == brand:
            return True
    if t == 'ENVASES RIGO':
        return True
    return False


def _is_skip_word(text: str) -> bool:
    """判断是否为应跳过的标记词"""
    t = text.strip()
    skip_words = {'Artículos', 'Sin', 'Pre', 'Precio:', '$', 'Articulo', 'Articulo:', ':',
                  'Marca/s:', ';', ';CA'}
    return t in skip_words


def _parse_page(page, images_dir: str, supplier_id: int) -> list:
    import os
    from PIL import Image

    words = page.extract_words()
    page_height = page.height

    # 按行分组（y坐标容差3px）
    rows = defaultdict(list)
    for w in words:
        y_key = round(w['top'] / 3) * 3
        rows[y_key].append(w)

    sorted_ys = sorted(rows.keys())

    # 图片列表
    img_list = []
    for pimg in page.images:
        if pimg['width'] < 40 or pimg['height'] < 40:
            continue
        if pimg['width'] >= 400:
            continue  # 底部 banner
        img_list.append({
            **pimg,
            'img_top': page_height - pimg['y1'],
            'img_bottom': page_height - pimg['y0'],
        })

    # ── 找所有 "Precio:" 行 ──
    precio_ys = []
    for y_key in sorted_ys:
        row = rows[y_key]
        row_text = ' '.join(w['text'] for w in row)
        if 'Precio:' in row_text and '$' in row_text:
            precio_ys.append(y_key)

    products = []

    for block_idx, precio_y in enumerate(precio_ys):
        # 确定该商品块行的 y 范围（同一 Precio 行的4列共享）
        # 找下一个不同 y 的 Precio 行
        block_end = page_height
        for next_y in precio_ys[block_idx + 1:]:
            if next_y - precio_y > 10:
                block_end = next_y - 1
                break

        # 按列分组该块的所有文字
        col_words = defaultdict(list)
        for y_key in sorted_ys:
            if precio_y <= y_key < block_end:
                for w in rows[y_key]:
                    col = _get_col(w['x0'])
                    col_words[col].append(w)

        # 处理每列
        for col_idx in range(4):
            col_w = col_words.get(col_idx, [])
            if not col_w:
                continue

            col_w_sorted = sorted(col_w, key=lambda x: (x['top'], x['x0']))
            col_text = ' '.join(w['text'] for w in col_w_sorted)

            # 提取价格
            price_match = re.search(r'Precio:\s*\$\s*([\d\.,]+)', col_text)
            if not price_match:
                continue
            price = _clean_price(price_match.group(1))
            if price <= 0:
                continue

            # 提取 SKU
            # 格式1: "Marca/s: 140 - 01153"  → SKU = 01153
            # 格式2: "Articulo : 01153"  → SKU = 01153
            # 格式3: "Articulo : Marca/s: 097,164 02961" → SKU = 02961 (最后一个数字)
            sku = None
            sku_y = None

            # 方法1: Marca/s: <数字> - <SKU>
            m = re.search(r'Marca/s:\s*\d+\s*-\s*(\d{3,7}[A-Za-z]?)', col_text)
            if m:
                sku = m.group(1)
                # 找 sku 对应的 y 坐标
                for w in col_w_sorted:
                    if w['text'] == sku or w['text'].endswith(sku):
                        sku_y = w['top']
                        break
            else:
                # 方法2: Articulo : <SKU>
                m = re.search(r'Articulo\s*:\s*(\d{3,7}[A-Za-z]?)', col_text)
                if m:
                    sku = m.group(1)
                    for w in col_w_sorted:
                        if w['text'] == sku:
                            sku_y = w['top']
                            break
                else:
                    # 方法3: Marca/s: <数字>,<数字> <SKU>  (如 "097,164 02961")
                    m = re.search(r'Marca/s:\s*[\d,]+\s+(\d{3,7}[A-Za-z]?)', col_text)
                    if m:
                        sku = m.group(1)
                        for w in col_w_sorted:
                            if w['text'] == sku:
                                sku_y = w['top']
                                break

            if not sku:
                continue

            # ── 提取商品名称 ──
            # 名称在 SKU 行之后、品牌行之前
            # 收集 SKU 之后的所有文字，排除品牌行和跳过词
            name_parts = []
            found_sku = False
            for w in col_w_sorted:
                txt = w['text']
                if not found_sku:
                    # 跳过 SKU 本身之前的所有内容
                    if txt == sku or (sku in txt and len(txt) <= len(sku) + 3):
                        found_sku = True
                    continue
                # SKU 之后
                # 跳过品牌行
                if _is_brand_line(txt):
                    continue
                # 跳过标记词
                if _is_skip_word(txt):
                    continue
                # 跳过 "Artículos Sin Prec" 系列标记
                if txt in ('Artículos', 'Sin', 'Pre', '-', 'Artículos'):
                    continue
                # 跳过下一个 Precio 行
                if 'Precio:' in txt:
                    break
                name_parts.append(txt)

            name = ' '.join(name_parts).strip()
            name = re.sub(r'\s+', ' ', name)
            # 清理括号残片
            name = re.sub(r'^[;)\s]+', '', name).strip()
            name = re.sub(r'[;)\s]+$', '', name).strip()

            if not name:
                continue

            # 提取图片
            # 此格式PDF中，文字在上半部分，图片在下半部分
            # 每行文字对应一行图片，按行序号一一对应
            image_path = None
            best_img = None

            # 计算 Precio 行是该页第几个商品行（0-3）
            block_row_idx = 0
            for py in precio_ys:
                if py < precio_y:
                    block_row_idx += 1
                else:
                    break
            # 同一 Precio 行中，我们处理的是该行的第 col_idx 个商品
            # 图片排列：4行x4列，每行4张图
            # 第 block_row_idx 行图片的 y 范围
            # 图片行间距约 117px (660-443=117, 443-326=117, 326-209=117)
            # 第一行图片 img_top ≈ 93, 第二行 ≈ 210, 第三行 ≈ 327, 第四行 ≈ 443
            # 对应文字行：第一行 precio_y ≈ 214, 第二行 ≈ 331, 第三行 ≈ 448, 第四行 ≈ 565
            # 文字行间距也约117px
            # 所以同一行号的文字和图片，图片的 img_top 在 precio_y 附近偏下

            for pimg in img_list:
                img_center_x = (pimg['x0'] + pimg['x1']) / 2
                lo, hi = COL_BOUNDS[col_idx]
                if not (lo <= img_center_x < hi):
                    continue
                # 图片应该在同一行：img_top 接近 precio_y
                if abs(pimg['img_top'] - precio_y) < 80:
                    if best_img is None or abs(pimg['img_top'] - precio_y) < abs(best_img['img_top'] - precio_y):
                        best_img = pimg

            if best_img:
                try:
                    data = best_img['stream'].get_data()
                    img = Image.open(io.BytesIO(data))
                    sub_dir = os.path.join(images_dir, f"lp_{supplier_id}")
                    os.makedirs(sub_dir, exist_ok=True)
                    fname = f"{sku}.jpg"
                    img.convert('RGB').save(os.path.join(sub_dir, fname), 'JPEG', quality=85)
                    image_path = f"/images/lp_{supplier_id}/{fname}"
                except Exception:
                    pass

            products.append({
                "sku": sku,
                "name": name[:300],
                "price": price,
                "category": "",
                "image": image_path,
            })

    return products
