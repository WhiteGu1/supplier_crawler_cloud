# -*- coding: utf-8 -*-
"""Kandel PDF 解析器 - 4列×2行布局，奇偶页x偏移交替"""

import re
import io
from collections import defaultdict

PARSER_NAME = "kandel — 目录解析 (4列×2行)"
PARSER_DESC = "适用于 kandel 的商品目录PDF，4列2行布局，奇偶页交替偏移"


def parse(pdf_path: str, images_dir: str, supplier_id: int) -> list:
    """解析 kandel PDF目录，返回商品列表"""
    import pdfplumber

    all_products = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            # 跳过无文字的封面页
            words = page.extract_words()
            if not words:
                continue
            all_products.extend(_parse_page(page, images_dir, supplier_id, page_idx))
    return all_products


def _clean_price(text: str) -> float:
    """清理价格文本: '$ 3.350,00' → 3350.00"""
    text = re.sub(r'[^\d\.,]', '', text)
    # 阿根廷格式: 千分位. 小数,
    if re.search(r'\d+\.\d{3},\d{2}', text):
        text = text.replace('.', '').replace(',', '.')
    elif ',' in text:
        text = text.replace(',', '.')
    nums = re.findall(r'\d+\.?\d*', text)
    return float(nums[0]) if nums else 0.0


def _detect_columns(page, page_idx: int) -> list:
    """检测4列的x0边界，奇偶页交替偏移"""
    # 第3页(idx=2): x0 ≈ 57, 242, 421, 603
    # 第4页(idx=3): x0 ≈ 25, 210, 389, 571
    # 规律: 偶数内容页偏右(57起), 奇数内容页偏左(25起)
    # 内容页从idx=2开始, 所以 (page_idx-2) % 2 决定偏移
    offset = (page_idx - 2) % 2
    if offset == 0:
        # 偏右布局
        col_centers = [140, 325, 504, 686]
        col_bounds = [(0, 230), (230, 410), (410, 590), (590, 792)]
    else:
        # 偏左布局
        col_centers = [108, 293, 472, 654]
        col_bounds = [(0, 200), (200, 380), (380, 560), (560, 792)]
    return col_bounds


def _get_col(x0: float, col_bounds: list) -> int:
    for i, (lo, hi) in enumerate(col_bounds):
        if lo <= x0 < hi:
            return i
    return 3


def _parse_page(page, images_dir: str, supplier_id: int, page_idx: int) -> list:
    import os
    from PIL import Image

    words = page.extract_words()
    page_height = page.height
    col_bounds = _detect_columns(page, page_idx)

    # 按行分组
    rows = defaultdict(list)
    for w in words:
        y_key = round(w['top'] / 3) * 3
        rows[y_key].append(w)

    # 提取页眉分类
    current_category = ""
    sorted_ys = sorted(rows.keys())
    for y_key in sorted_ys[:5]:
        row_text = ' '.join(w['text'] for w in rows[y_key])
        # 页眉如 "BATH COLLECTION" + "ACCESORIOS"
        if any(kw in row_text.upper() for kw in ['COLLECTION', 'CATEGORIA', 'CATALOGO']):
            continue
        if row_text.strip() and not re.search(r'\d{5,7}', row_text):
            current_category = row_text.strip()
            break

    # 重组页眉：第1行是大类，第2行是子类
    header_lines = []
    for y_key in sorted_ys[:5]:
        row_text = ' '.join(w['text'] for w in rows[y_key]).strip()
        if not row_text or re.search(r'\d{5,7}', row_text):
            break
        header_lines.append(row_text)
    if len(header_lines) >= 2:
        current_category = header_lines[0] + ' > ' + header_lines[1]
    elif header_lines:
        current_category = header_lines[0]

    # 图片列表（过滤背景大图和小图）
    img_list = []
    for pimg in page.images:
        if pimg['width'] < 100 or pimg['height'] < 100:
            continue
        if pimg['width'] >= 700:
            continue  # 背景图
        img_list.append({
            **pimg,
            'img_top': page_height - pimg['y1'],
            'img_bottom': page_height - pimg['y0'],
        })

    # 找SKU行：含5-7位数字SKU + $ + 价格
    sku_rows = []  # (y_key, idx)
    for idx, y_key in enumerate(sorted_ys):
        row = rows[y_key]
        row_text = ' '.join(w['text'] for w in row)
        if re.search(r'\d{5,7}', row_text) and re.search(r'\$\s*[\d\.,]+', row_text):
            sku_rows.append((y_key, idx))

    products = []

    for sku_idx, (y_key, idx) in enumerate(sku_rows):
        row = rows[y_key]
        row_text = ' '.join(w['text'] for w in row)

        # 按列分组SKU和价格
        # SKU格式: 4023672 $ 3.350,00  或  4027231A $ 2.830,00
        col_items = defaultdict(list)
        for w in row:
            col = _get_col(w['x0'], col_bounds)
            col_items[col].append(w)

        # 名称收集范围：SKU行下方，最多到下一个SKU行或+80px
        # 名称在SKU行下方（描述行在SKU和价格行之后）
        lower_y = y_key + 80
        if sku_idx < len(sku_rows) - 1:
            next_y = sku_rows[sku_idx + 1][0]
            lower_y = min(y_key + 80, next_y - 5)

        # 收集名称行（只在SKU行下方找）
        name_cols = defaultdict(list)
        for check_y in sorted_ys:
            if check_y <= y_key or check_y >= lower_y:
                continue
            for w in rows[check_y]:
                col = _get_col(w['x0'], col_bounds)
                name_cols[col].append(w['text'])

        # 也从SKU行本身提取名称（SKU和价格之间的文字）
        for col_idx in range(4):
            col_words_list = col_items.get(col_idx, [])
            in_name = False
            for w in sorted(col_words_list, key=lambda x: x['x0']):
                txt = w['text']
                if re.match(r'^\d{5,7}[A-Za-z]?$', txt):
                    in_name = True
                    continue
                if in_name and txt == '$':
                    break
                if in_name:
                    name_cols[col_idx].insert(0, txt)

        # 处理每列的商品
        for col_idx in range(4):
            col_words = col_items.get(col_idx, [])
            col_text = ' '.join(w['text'] for w in col_words)

            # 匹配 SKU + 价格: 4023672 $ 3.350,00
            m = re.search(r'(\d{5,7}[A-Za-z]?)\s*\$\s*([\d\.,]+)', col_text)
            if not m:
                continue

            sku = m.group(1)
            price = _clean_price(m.group(2))
            if price <= 0:
                continue

            # 名称：从同列名称行收集
            name_parts = ' '.join(name_cols.get(col_idx, [])).strip()
            name = re.sub(r'\s+', ' ', name_parts).strip()

            # 去掉包装信息 B:数字 M:数字
            name = re.sub(r'\s*B:\d+\s*', ' ', name)
            name = re.sub(r'\s*M:\d+\s*', ' ', name)
            name = re.sub(r'\s+', ' ', name).strip()

            if not name:
                # 如果名称为空，用SKU行中SKU和$之间的文字
                between = re.search(r'\d{5,7}[A-Za-z]?\s+(.+?)\$', col_text)
                if between:
                    name = between.group(1).strip()
                    name = re.sub(r'\s*B:\d+\s*', ' ', name)
                    name = re.sub(r'\s*M:\d+\s*', ' ', name).strip()

            if not name:
                continue

            # 找图片：该列中，图片底部靠近SKU行y坐标
            image_path = None
            best_img = None
            for pimg in img_list:
                img_center_x = (pimg['x0'] + pimg['x1']) / 2
                lo, hi = col_bounds[col_idx]
                if not (lo <= img_center_x < hi):
                    continue
                # 图片应该在SKU行上方
                img_bottom = pimg['img_bottom']
                if img_bottom <= y_key + 30 and img_bottom > y_key - 250:
                    if best_img is None or abs(img_bottom - y_key) < abs(best_img['img_bottom'] - y_key):
                        best_img = pimg

            if best_img:
                try:
                    data = best_img['stream'].get_data()
                    img = Image.open(io.BytesIO(data))
                    sub_dir = os.path.join(images_dir, f"kandel_{supplier_id}")
                    os.makedirs(sub_dir, exist_ok=True)
                    fname = f"{sku}.jpg"
                    img.convert('RGB').save(os.path.join(sub_dir, fname), 'JPEG', quality=85)
                    image_path = f"/images/kandel_{supplier_id}/{fname}"
                except Exception:
                    pass

            products.append({
                "sku": sku,
                "name": name[:300],
                "price": price,
                "category": current_category,
                "image": image_path,
            })

    return products
