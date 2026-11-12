# -*- coding: utf-8 -*-
"""
najal 供应商 PDF 解析器
目录格式：每页若干 4 列商品块，每块结构（自上而下）：
    [图片]  (位于文字上方)
    ART <SKU>
    <商品名称 1~4 行，含尺寸/包装数>
    $ <价格>   (阿根廷格式：点=千分位, 逗号=小数)

页脚含公司信息：Av.Corrientes 2294 ... najal@hotmail.com.ar
"""
import re
import io
import os
from collections import defaultdict

PARSER_NAME = "najal — 目录解析"
PARSER_DESC = "适用于 najal 目录 PDF，4列布局，ART SKU + 名称 + $价格，图片在文字上方"


def parse(pdf_path: str, images_dir: str, supplier_id: int) -> list:
    import pdfplumber

    products = []
    seen = set()
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for p in _parse_page(page, images_dir, supplier_id):
                key = (p['sku'], p['name'][:60])
                if key in seen:
                    continue
                seen.add(key)
                products.append(p)
    return products


def _clean_price(text: str) -> float:
    """阿根廷价格格式：'1.665'→1665, '4.500,00'→4500.0, '685'→685"""
    t = re.sub(r'[^\d\.,]', '', text or '')
    if not t:
        return 0.0
    if ',' in t:
        t = t.replace('.', '').replace(',', '.')
    else:
        t = t.replace('.', '')
    try:
        return float(t)
    except ValueError:
        nums = re.findall(r'\d+\.?\d*', t)
        return float(nums[0]) if nums else 0.0


# 4 列 x 边界（页面宽 595）
COL_BOUNDS = [(0, 150), (150, 295), (295, 440), (440, 600)]


def _get_col(x0: float) -> int:
    for i, (lo, hi) in enumerate(COL_BOUNDS):
        if lo <= x0 < hi:
            return i
    return 3


def _parse_page(page, images_dir: str, supplier_id: int) -> list:
    from PIL import Image

    words = page.extract_words()
    if not words:
        return []
    ph = page.height

    # ── 图片（排除底部 banner 与小图标）──
    imgs = []
    for im in page.images:
        w = im.get('width', 0)
        h = im.get('height', 0)
        if w < 35 or h < 35:
            continue
        if w >= 400:  # 底部通栏 banner
            continue
        imgs.append({
            'x0': im['x0'], 'x1': im['x1'],
            'top': ph - im['y1'],
            'bottom': ph - im['y0'],
            'stream': im.get('stream'),
        })

    # ── 找 ART 行（商品行锚点），按 y 聚类 ──
    art_ys = []
    for w in words:
        t = w['text'].strip()
        if t.upper() == 'ART' or re.match(r'^ART\s*\d+$', t, re.I):
            art_ys.append(w['top'])
    art_ys.sort()

    rows_y = []
    for y in art_ys:
        if rows_y and y - rows_y[-1] <= 10:
            continue
        rows_y.append(y)

    products = []

    for ri, row_y in enumerate(rows_y):
        # 该商品行的 y 范围：图片顶(row_y-100) 到 下一行起点前
        y_lo = row_y - 100
        y_hi = (rows_y[ri + 1] - 100 - 1) if ri + 1 < len(rows_y) else (row_y + 95)

        row_words = [w for w in words if y_lo <= w['top'] < y_hi]
        if not row_words:
            continue

        # 按列分组
        col_words = defaultdict(list)
        for w in row_words:
            col_words[_get_col(w['x0'])].append(w)

        # 商品行内按 y 分组找各列的 ART（同一行4列 ART 的 top 可能略有差异）
        for col in range(4):
            cw = sorted(col_words.get(col, []), key=lambda x: (x['top'], x['x0']))
            if not cw:
                continue

            sku = None
            art_i = None
            for i, w in enumerate(cw):
                t = w['text'].strip()
                if t.upper() == 'ART':
                    if i + 1 < len(cw):
                        sku = cw[i + 1]['text'].strip()
                    art_i = i
                    break
                m = re.match(r'^ART\s*(\d+)$', t, re.I)
                if m:
                    sku = m.group(1)
                    art_i = i
                    break
            if not sku or art_i is None:
                continue
            # 过滤明显非法 sku
            if not re.match(r'^[\dA-Za-z\-]+$', sku):
                continue

            # ── 名称 + 价格 ──
            name_parts = []
            price = None
            i = art_i + 1
            # 若 ART 是独立词，跳过紧跟的 sku 词
            if cw[art_i]['text'].strip().upper() == 'ART':
                if i < len(cw) and cw[i]['text'].strip() == sku:
                    i += 1
            while i < len(cw):
                t = cw[i]['text'].strip()
                if t.startswith('$'):
                    # 价格在本词或下一词
                    m = re.search(r'([\d][\d\.,]*)', t[1:])
                    if m:
                        price = _clean_price(m.group(1))
                    elif i + 1 < len(cw):
                        m2 = re.search(r'[\d][\d\.,]*', cw[i + 1]['text'])
                        if m2:
                            price = _clean_price(m2.group(0))
                    break
                if t == '$':
                    if i + 1 < len(cw):
                        m2 = re.search(r'[\d][\d\.,]*', cw[i + 1]['text'])
                        if m2:
                            price = _clean_price(m2.group(0))
                    break
                # 过滤页脚噪声
                if 'Corrientes' in t or 'hotmail' in t or t.startswith('---'):
                    break
                name_parts.append(t)
                i += 1

            name = ' '.join(name_parts)
            name = re.sub(r'\s+', ' ', name).strip()
            name = re.sub(r'^[\s;,\)]+', '', name)
            name = re.sub(r'[\s;,]+$', '', name)
            if not name:
                continue
            if price is None or price <= 0:
                price = 0.0

            # ── 图片匹配：同列、img_bottom ≈ row_y ──
            image_path = None
            best = None
            for im in imgs:
                cx = (im['x0'] + im['x1']) / 2
                if _get_col(im['x0']) != col and not (COL_BOUNDS[col][0] <= cx < COL_BOUNDS[col][1]):
                    continue
                d = abs(im['bottom'] - row_y)
                if d < 30:
                    if best is None or d < abs(best['bottom'] - row_y):
                        best = im
            if best and best.get('stream') is not None:
                try:
                    data = best['stream'].get_data()
                    img = Image.open(io.BytesIO(data))
                    sub = os.path.join(images_dir, f"najal_{supplier_id}")
                    os.makedirs(sub, exist_ok=True)
                    # SKU 可能在不同目录中重复（ART 号共用），确保文件名唯一
                    base_name = str(sku)
                    fname = f"{base_name}.jpg"
                    seq = 2
                    while os.path.exists(os.path.join(sub, fname)):
                        fname = f"{base_name}_{seq}.jpg"
                        seq += 1
                    img.convert('RGB').save(os.path.join(sub, fname), 'JPEG', quality=85)
                    image_path = f"/images/najal_{supplier_id}/{fname}"
                except Exception:
                    pass

            products.append({
                "sku": str(sku),
                "name": name[:300],
                "price": price,
                "category": "",
                "image": image_path,
            })

    return products
