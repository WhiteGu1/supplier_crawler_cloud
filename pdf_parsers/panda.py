# -*- coding: utf-8 -*-
"""Panda外务玩具 PDF 解析器 - 2列×2行布局，使用PyMuPDF提取文字和图片
布局：图片在上 → 价格红色标签叠加在图片右下角 → 名称 → 包装/SKU
支持多种SKU格式：24xxxx, 25xxxx, 22xxx, 9092S, W-21-1, 806-4, 507N 等
"""

import re
import os
from collections import defaultdict

PARSER_NAME = "panda — 目录解析 (2列×2行)"
PARSER_DESC = "适用于 panda外务玩具 的商品目录PDF，2列2行布局，价格叠加在图片右下角"


def parse(pdf_path: str, images_dir: str, supplier_id: int) -> list:
    """解析 panda PDF目录，返回商品列表"""
    import fitz

    all_products = []
    doc = fitz.open(pdf_path)
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        all_products.extend(_parse_page(page, images_dir, supplier_id, page_idx, doc))
    doc.close()
    return all_products


def _clean_price(text: str) -> float:
    """清理价格文本: '$8.51' 或 '$ 13,90' 或 '$26' → float"""
    text = re.sub(r'[^\d\.,]', '', text)
    if ',' in text and '.' not in text:
        text = text.replace(',', '.')
    elif ',' in text:
        text = text.replace('.', '').replace(',', '.')
    nums = re.findall(r'\d+\.?\d*', text)
    return float(nums[0]) if nums else 0.0


def _is_sku_like(text: str) -> bool:
    """判断文本是否像SKU编号"""
    # 去掉前缀 "10/24042" → "24042"
    text = re.sub(r'^\d+/', '', text)
    # 标准格式: 24xxxx, 25xxxx, 22xxx (5-6位数字+可选字母)
    if re.match(r'^2[0-5]\d{3,4}[A-Za-z]{0,4}$', text):
        return True
    # 非标准格式: 9092S, 806-4, W-21-1, 507N, 517, 139-2, 109N
    if re.match(r'^[A-Z]?\d{3,4}[-]?\d*[A-Z]?$', text):
        return True
    if re.match(r'^[A-Z]-\d+-\d+$', text):
        return True
    return False


def _extract_sku(text: str) -> str:
    """从文本中提取SKU"""
    text = re.sub(r'^\d+/', '', text)  # 去掉前缀 "10/24042"
    # 标准格式
    m = re.search(r'\b(2[0-5]\d{3,4}[A-Za-z]{0,4})\b', text)
    if m:
        return m.group(1)
    return ''


def _find_sku_in_tokens(tokens: list) -> str:
    """从token列表中找最像SKU的那个，返回SKU或空字符串"""
    candidates = []
    for txt in tokens:
        txt_clean = re.sub(r'^\d+/', '', txt)
        # 标准格式: 24xxxx, 25xxxx, 22xxx
        if re.match(r'^2[0-5]\d{3,4}[A-Za-z]{0,4}$', txt_clean):
            return txt_clean
        # 非标准格式: 9092S, 806-4, 507N, 517, 139-2, 109N, 701
        if re.match(r'^[A-Z]?\d{3,4}[-]?\d*[A-Z]?$', txt_clean):
            candidates.append(txt_clean)
        # 字母前缀+数字: SBS-618, XDZ-805, ADB-206, W-21-1
        elif re.match(r'^[A-Z]{2,3}-\d+(-\d+)?$', txt_clean):
            candidates.append(txt_clean)
        elif re.match(r'^[A-Z]-\d+-\d+$', txt_clean):
            candidates.append(txt_clean)
    return candidates[0] if candidates else ''


def _parse_page(page, images_dir: str, supplier_id: int, page_idx: int, doc) -> list:
    import fitz
    from PIL import Image

    page_w = page.rect.width
    page_h = page.rect.height

    # 2列布局
    col_mid = page_w / 2

    def get_col(x0):
        return 0 if x0 < col_mid else 1

    # 提取文字词
    words = page.get_text('words')
    content_words = [w for w in words if 100 <= w[1] <= 730]

    # 按行分组 (y坐标容差5pt)
    rows = defaultdict(list)
    for w in content_words:
        y_key = round(w[1] / 5) * 5
        rows[y_key].append(w)

    sorted_ys = sorted(rows.keys())

    # 提取页面图片位置
    img_positions = []
    for img_info in page.get_images(full=True):
        xref = img_info[0]
        rects = page.get_image_rects(xref)
        for rect in rects:
            w, h = rect.width, rect.height
            if w < 50 or h < 50:
                continue
            if w >= 700:
                continue
            img_positions.append({
                'xref': xref,
                'x0': rect.x0,
                'x1': rect.x1,
                'y0': rect.y0,
                'y1': rect.y1,
                'cx': (rect.x0 + rect.x1) / 2,
                'cy': (rect.y0 + rect.y1) / 2,
                'w': w,
                'h': h,
            })

    # 找价格行：含 $ 符号 + 数字的行
    price_rows = []
    for y_key in sorted_ys:
        row = rows[y_key]
        row_text = ' '.join(w[4] for w in row)
        if re.search(r'\$\s*\d+(?:[\.,]\d{1,2})?', row_text):
            price_rows.append(y_key)

    if not price_rows:
        return []

    # 合并相近的价格行（差<15pt）为商品行
    product_rows = []
    used = set()
    for pr_y in price_rows:
        if pr_y in used:
            continue
        group = [pr_y]
        used.add(pr_y)
        for other_y in price_rows:
            if other_y not in used and abs(other_y - pr_y) < 15:
                group.append(other_y)
                used.add(other_y)
        product_rows.append(group)

    products = []

    for row_group in product_rows:
        all_price_words = []
        for y_key in row_group:
            all_price_words.extend(rows[y_key])

        col_prices = defaultdict(list)
        for w in all_price_words:
            col = get_col(w[0])
            col_prices[col].append(w)

        row_y_min = min(row_group)
        row_y_max = max(row_group)

        for col_idx in range(2):
            col_words = col_prices.get(col_idx, [])
            col_text = ' '.join(w[4] for w in col_words)

            price_match = re.search(r'\$\s*(\d+(?:[\.,]\d{1,2})?)', col_text)
            if not price_match:
                continue

            price = _clean_price(price_match.group(1))
            if price <= 0:
                continue

            # 在价格行下方找名称和SKU
            search_ys = [y for y in sorted_ys if row_y_max + 5 <= y <= row_y_max + 120]

            name_parts = []
            all_tokens = []  # 收集所有token用于后续SKU查找

            for y_key in search_ys:
                for w in rows[y_key]:
                    if get_col(w[0]) != col_idx:
                        continue
                    txt = w[4]
                    all_tokens.append(txt)

                    # 跳过包装信息
                    if re.match(r'^\(\d+\)$', txt):
                        continue
                    if txt.upper() in ['PCS', 'PC']:
                        continue
                    # 跳过尺码 S M L
                    if txt in ['S', 'M', 'L', 'XL']:
                        continue
                    # 跳过OPP BAG
                    if txt.upper() in ['OPP', 'BAG']:
                        continue
                    # 跳过纯数字（包装数量或SKU前缀）
                    if re.match(r'^\d+$', txt):
                        continue
                    # 跳过序号前缀 如 "10/" 或 "22/"
                    if re.match(r'^\d+/$', txt):
                        continue
                    # 跳过颜色
                    if txt.upper() in ['RED', 'PINK', 'BLUE', 'BLACK', 'WHITE', 'GREEN', 'YELLOW', 'ORANGE', 'PURPLE']:
                        continue
                    # 跳过尺码组合 如 "12KG"
                    if re.match(r'^\d+KG$', txt):
                        continue
                    # 跳过尺寸标注 如 "60CM", "28CM", "53CM", "24CM"
                    if re.match(r'^\d+CM$', txt):
                        continue
                    # 跳过 BOTTOM: HEAD: 等标注
                    if re.match(r'^[A-Z]+:$', txt):
                        continue

                    # 名称文字
                    if txt not in ['$', 'de', 'De', 'DE']:
                        name_parts.append(txt)

            name = re.sub(r'\s+', ' ', ' '.join(name_parts)).strip()
            # 移除名称中残留的序号前缀 如 "10/" 或 "22/"
            name = re.sub(r'\b\d+/\s*', ' ', name).strip()
            name = re.sub(r'\s+', ' ', name).strip()

            # 从所有token中找SKU
            sku = _find_sku_in_tokens(all_tokens)
            # 如果没找到，尝试用_extract_sku
            if not sku:
                for txt in all_tokens:
                    sku = _extract_sku(txt)
                    if sku:
                        break

            if not sku or not name:
                continue

            # 从名称中移除SKU
            if sku and sku in name:
                name = name.replace(sku, '').strip()
                name = re.sub(r'\s+', ' ', name).strip()

            if not name:
                continue

            # 找图片
            image_path = None
            best_img = None
            best_score = float('inf')

            for pimg in img_positions:
                if col_idx == 0 and pimg['cx'] >= col_mid + 30:
                    continue
                if col_idx == 1 and pimg['cx'] < col_mid - 30:
                    continue

                if pimg['y0'] <= row_y_min <= pimg['y1'] + 30:
                    score = abs(pimg['y1'] - row_y_min)
                    if score < best_score:
                        best_score = score
                        best_img = pimg
                elif pimg['y1'] > row_y_min - 50 and pimg['y0'] < row_y_min + 50:
                    score = abs(pimg['y1'] - row_y_min)
                    if score < best_score:
                        best_score = score
                        best_img = pimg

            if best_img:
                try:
                    pix = fitz.Pixmap(doc, best_img['xref'])
                    sub_dir = os.path.join(images_dir, f"panda_{supplier_id}")
                    os.makedirs(sub_dir, exist_ok=True)
                    fname = f"{sku}.jpg"
                    if pix.n - pix.alpha >= 4:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix.samples
                    img_mode = 'RGB' if pix.n - pix.alpha == 3 else 'RGBA'
                    img = Image.frombytes(img_mode, [pix.width, pix.height], img_data)
                    img.convert('RGB').save(os.path.join(sub_dir, fname), 'JPEG', quality=85)
                    image_path = f"/images/panda_{supplier_id}/{fname}"
                    pix = None
                except Exception:
                    pass

            products.append({
                "sku": sku,
                "name": name[:300],
                "price": price,
                "category": "玩具游戏",
                "image": image_path,
                "_page": page_idx + 1,
            })

    # 页内去重：同一页上相同SKU+name只保留一个
    seen = set()
    unique = []
    for p in products:
        key = (p['sku'], p['name'])
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique
