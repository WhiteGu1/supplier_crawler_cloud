# -*- coding: utf-8 -*-
"""
解析器: K&K 目录格式 (3列×2行布局)
布局特征:
  - A4页面 (595×842)
  - 3列×2行 = 每页6个商品
  - 价格在右上角: "C" + 数字 (如 C8100, C27500)
  - SKU: NS开头+数字 (如 NS413567E1), 也可能是DR等前缀
  - 商品名: SKU下方多行描述
  - 包装信息: "Pack: 50 -Int: 1"
  - 左侧竖排文字: 分类名，从下往上读 (如 BELLEZA Y CUIDADO PERSONAL)
  - 图片: 每个商品区域一张产品图
"""

import re
import io
from collections import defaultdict

PARSER_NAME = "K&K — 目录解析 (3列×2行)"
PARSER_DESC = "适用于 K&K 的商品目录PDF，3列2行布局，价格C开头在右上角"

# 3列布局的x坐标边界
COL_BOUNDS = [(0, 195), (195, 370), (370, 595)]
COL_CENTERS = [115, 280, 480]


def parse(pdf_path: str, images_dir: str, supplier_id: int) -> list:
    """解析 K&K PDF目录，返回商品列表"""
    import pdfplumber

    all_products = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            words = page.extract_words()
            if not words:
                continue
            # 跳过封面页和目录页 (文字太少)
            if len(words) < 30:
                continue
            all_products.extend(_parse_page(page, images_dir, supplier_id, page_idx))
    return all_products


def _get_col(x0: float) -> int:
    """根据x坐标判断所属列 (0, 1, 2)"""
    for i, (lo, hi) in enumerate(COL_BOUNDS):
        if lo <= x0 < hi:
            return i
    return 2


def _clean_price(text: str) -> float:
    """清理价格文本: 'C8100' → 8100.0"""
    text = re.sub(r'[^\d]', '', text)
    try:
        return float(text) if text else 0.0
    except ValueError:
        return 0.0


def _extract_row_category(vchars_in_row):
    """
    从竖排字母中提取分类名。
    字母从上到下排列，但分类名从下往上读。
    vchars_in_row: [(top, char), ...] 已按top排序(从小到大)
    返回分类名或空字符串
    """
    if not vchars_in_row:
        return ""
    # 从下往上读: 反转列表
    reversed_chars = list(reversed(vchars_in_row))  # [(top, char), ...] 从大到小
    
    # 在gap处分词: 相邻字母间距 > 10.5px 插入空格
    # (通过实测: BELLEZAYCUIDADOPERSONAL 在阈值10.5时正确分词为 BELLEZA Y CUIDADO PERSONAL)
    result = []
    prev_y = None
    for y, c in reversed_chars:
        if prev_y is not None and prev_y - y > 10.5:
            result.append(' ')
        result.append(c)
        prev_y = y
    
    raw = ''.join(result).strip()
    raw = re.sub(r'\s+', ' ', raw)
    return raw


def _detect_price_rows(words):
    """
    检测价格行的y坐标和列。
    返回 [(y_key, col, price_text), ...]
    """
    price_rows = []
    for w in words:
        # 匹配单独的 "C" 字母 (x0 在列中心位置)
        if w['text'] == 'C' and w['x0'] > 100:
            # 查找同行右侧紧邻的数字
            nearby = [
                ww for ww in words
                if abs(ww['top'] - w['top']) < 3
                and ww['x0'] > w['x0']
                and ww['x0'] < w['x0'] + 60
                and re.match(r'^\d+$', ww['text'])
            ]
            if nearby:
                col = _get_col(w['x0'])
                price_rows.append((round(w['top'] / 3) * 3, col, nearby[0]['text']))
    
    # 也匹配 C+数字连在一起的情况
    for w in words:
        if re.match(r'^C\d+$', w['text']) and w['x0'] > 100:
            col = _get_col(w['x0'])
            y_key = round(w['top'] / 3) * 3
            # 避免重复
            if not any(pr[0] == y_key and pr[1] == col for pr in price_rows):
                price_rows.append((y_key, col, w['text']))
    
    return price_rows


def _parse_page(page, images_dir: str, supplier_id: int, page_idx: int) -> list:
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

    # 检测价格行
    price_rows = _detect_price_rows(words)
    if not price_rows:
        return []

    # 确定商品行 (y坐标分组)
    # 每个y坐标对应一行3个商品
    row_ys = sorted(set(y for y, _, _ in price_rows))

    # 提取页面级竖排分类 (x0 < 30 的单字符字母)
    # 竖排分类是整页的分类，虽然视觉上出现在中间行
    vchars_all = [(w['top'], w['text']) for w in words if w['x0'] < 30 and len(w['text']) == 1]
    vchars_all.sort()
    page_category = _extract_row_category(vchars_all)

    # 图片列表（过滤背景大图和小logo）
    img_list = []
    for pimg in page.images:
        if pimg['width'] < 50 or pimg['height'] < 50:
            continue
        if pimg['width'] >= 500:
            continue  # 背景全页图
        if pimg['x0'] < 40 and pimg['width'] < 50:
            continue  # 左侧竖条装饰
        img_list.append({
            **pimg,
            'img_top': page_height - pimg['y1'],
            'img_bottom': page_height - pimg['y0'],
        })

    products = []

    for price_y, col, price_text in price_rows:
        price = _clean_price(price_text)
        if price <= 0:
            continue

        # 页面级分类
        category = page_category

        # 确定该商品的区域范围 (y方向)
        # 区域: 当前价格行 → 同列下一个价格行
        same_col_next_y = page_height
        for next_y, next_col, _ in price_rows:
            if next_col == col and next_y > price_y:
                same_col_next_y = next_y
                break

        # 在价格行下方找SKU行
        sku = None
        sku_y = None
        for check_y in sorted_ys:
            if check_y <= price_y or check_y >= same_col_next_y:
                continue
            row = rows[check_y]
            for w in row:
                # 跳过竖排字母
                if w['x0'] < 30:
                    continue
                if _get_col(w['x0']) == col:
                    # SKU模式: NS+数字, DR+数字, 等 (2-3字母前缀+数字)
                    if re.match(r'^[A-Z]{2,3}\d+[A-Z]?\d*$', w['text']):
                        sku = w['text']
                        sku_y = check_y
                        break
            if sku:
                break

        if not sku:
            continue

        # 收集商品名称: SKU行下方到Pack行或区域下界
        name_parts = []
        pack_y = None

        for check_y in sorted_ys:
            if check_y <= (sku_y or price_y) or check_y >= same_col_next_y:
                continue
            row = rows[check_y]
            row_text = ' '.join(w['text'] for w in row)

            # 检测Pack行
            if 'Pack:' in row_text:
                pack_y = check_y
                break

            # 收集同列的文字作为名称 (排除竖排字母)
            for w in row:
                if w['x0'] < 30:
                    continue  # 跳过竖排分类字母
                if _get_col(w['x0']) == col:
                    txt = w['text']
                    # 跳过价格标记
                    if re.match(r'^C\d+$', txt) or txt == 'C':
                        continue
                    name_parts.append(txt)

        name = ' '.join(name_parts)
        # 清理包装信息
        name = re.sub(r'\s*Pack:\s*\d+\s*-?\s*Int:\s*\d+\s*', '', name)
        name = re.sub(r'\s+', ' ', name).strip()

        if not name:
            # 从SKU行本身提取名称 (SKU之后的所有非竖排文字)
            sku_row = rows.get(sku_y, [])
            after_sku = []
            found_sku = False
            for w in sorted(sku_row, key=lambda x: x['x0']):
                if w['x0'] < 30:
                    continue
                if w['text'] == sku:
                    found_sku = True
                    continue
                if not found_sku:
                    continue
                if _get_col(w['x0']) == col:
                    after_sku.append(w['text'])
            name = ' '.join(after_sku).strip()

        if not name:
            continue

        # 找图片: 在该商品区域内，同列的产品图片
        image_path = None
        best_img = None

        for pimg in img_list:
            img_center_x = (pimg['x0'] + pimg['x1']) / 2
            col_lo, col_hi = COL_BOUNDS[col]
            if not (col_lo <= img_center_x < col_hi):
                continue

            img_top = pimg['img_top']
            img_bottom = pimg['img_bottom']

            # 图片在商品区域内
            if img_top >= price_y - 10 and img_bottom <= same_col_next_y + 10:
                img_area = pimg['width'] * pimg['height']
                if best_img is None or img_area > best_img['width'] * best_img['height']:
                    best_img = pimg

        if best_img:
            try:
                data = best_img['stream'].get_data()
                img = Image.open(io.BytesIO(data))
                sub_dir = os.path.join(images_dir, f"kk_{supplier_id}")
                os.makedirs(sub_dir, exist_ok=True)
                fname = f"{sku}.jpg"
                img.convert('RGB').save(os.path.join(sub_dir, fname), 'JPEG', quality=85)
                image_path = f"/images/kk_{supplier_id}/{fname}"
            except Exception:
                pass

        products.append({
            "sku": sku,
            "name": name[:300],
            "price": price,
            "category": category,
            "image": image_path,
        })

    return products
