"""
解析器: d'sazá 目录格式（兼容两种布局）
格式1（4列目录）: catalogo_productos_dsaza_*.pdf
  - 4列并排, SKU行格式 "108538 Bultos:240 $3.990,00", 分类在页眉 "Baño::ACCESORIOS"
格式2（单列新商品）: Nuevos_Ingresos_*.pdf
  - 单列布局, 表头 "Codigo Foto Precio List. Bulto", SKU行格式 "104507 $ 1.290,00 240"
  - 无分类页眉, 图片固定左侧
"""

import re
import io
from collections import defaultdict

PARSER_NAME = "d'sazá — 目录解析 (4列/单列兼容)"
PARSER_DESC = "适用于 d'sazá 的商品目录PDF，自动识别4列目录格式或单列新商品格式"


def parse(pdf_path: str, images_dir: str, supplier_id: int) -> list:
    """
    解析 d'sazá PDF目录，自动检测格式，返回商品列表。
    每条: {sku, name, price, category, image}
    """
    import pdfplumber

    all_products = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if _is_new_format(page):
                all_products.extend(_parse_new_page(page, images_dir, supplier_id))
            else:
                all_products.extend(_parse_4col_page(page, images_dir, supplier_id))
    return all_products


# ── 格式检测 ──────────────────────────────────────────────────

def _is_new_format(page) -> bool:
    """检测是否为单列新格式：表头含 Codigo/Foto/Precio/List/Bulto"""
    words = page.extract_words()
    header_text = ' '.join(w['text'] for w in words[:30])
    return 'Codigo' in header_text and 'Bulto' in header_text


# ── 通用工具函数 ──────────────────────────────────────────────

def _clean_price(text: str) -> float:
    text = re.sub(r'[¥$€£\s\u00a0]', '', text)
    text = re.sub(r'[xX][A-Za-z\.]+.*$', '', text).strip()
    if re.search(r'\d+\.\d{3},\d{2}', text):
        text = text.replace('.', '').replace(',', '.')
    elif re.search(r'^\d+\.\d{3}$', text.strip()):
        text = text.replace('.', '')
    elif ',' in text and '.' in text:
        text = text.replace(',', '')
    elif ',' in text:
        text = text.replace(',', '.')
    nums = re.findall(r'\d+\.?\d*', text)
    return float(nums[0]) if nums else 0.0


def _get_col(x: float) -> int:
    """4列布局，按x坐标判断所在列"""
    if x < 210: return 0
    if x < 420: return 1
    if x < 630: return 2
    return 3


# ── 格式1: 4列目录 ────────────────────────────────────────────

def _parse_4col_page(page, images_dir: str, supplier_id: int) -> list:
    import os
    from PIL import Image

    words = page.extract_words()
    page_height = page.height
    current_category = ""

    # 按行分组
    rows = defaultdict(list)
    for w in words:
        y_key = round(w['top'] / 3) * 3
        rows[y_key].append(w)

    # 提取页眉分类（含"::"的行）
    for y_key in sorted(rows):
        row_text = ' '.join(w['text'] for w in rows[y_key])
        if '::' in row_text and 'Página' not in row_text:
            current_category = row_text.strip()
            break

    # 图片坐标转换：PDF坐标系(从下往上) → top从上往下，过滤logo小图
    img_list = []
    for pimg in page.images:
        if pimg['height'] < 50:
            continue
        img_list.append({
            **pimg,
            'img_top': page_height - pimg['y1'],
            'img_bottom': page_height - pimg['y0'],
        })

    products = []
    sorted_ys = sorted(rows.keys())

    for idx, y_key in enumerate(sorted_ys):
        row = rows[y_key]
        row_text = ' '.join(w['text'] for w in row)

        # 识别商品行：含SKU和Bultos
        if not re.search(r'\d{5,7}', row_text) or 'Bultos' not in row_text:
            continue

        # 按列收集SKU+价格
        sku_cols = defaultdict(list)
        for w in row:
            sku_cols[_get_col(w['x0'])].append(w['text'])

        # 收集名称行（直到下一个SKU行或间距过大）
        name_cols = defaultdict(list)
        for next_y in sorted_ys[idx + 1:]:
            if next_y - y_key > 150:
                break
            next_row = rows[next_y]
            next_text = ' '.join(w['text'] for w in next_row)
            if re.search(r'\d{5,7}', next_text) and 'Bultos' in next_text:
                break
            for w in next_row:
                name_cols[_get_col(w['x0'])].append(w['text'])

        # 找每列对应图片（图片底部 ≤ SKU行top + 20px）
        img_by_col = {}
        for pimg in img_list:
            if pimg['img_bottom'] <= y_key + 20:
                col = _get_col(pimg['x0'])
                if col not in img_by_col or pimg['img_bottom'] > img_by_col[col]['img_bottom']:
                    img_by_col[col] = pimg

        for col_idx in range(4):
            col_text = ' '.join(sku_cols.get(col_idx, []))
            m = re.search(r'(\d{5,7})\s*Bultos:\d+\s*(\$[\d\.,]+)', col_text)
            if not m:
                continue
            sku = m.group(1)
            price = _clean_price(m.group(2))
            name = ' '.join(name_cols.get(col_idx, [])).lstrip('.').strip()
            if not name or price <= 0:
                continue

            # 提取图片
            image_path = None
            if col_idx in img_by_col:
                try:
                    data = img_by_col[col_idx]['stream'].get_data()
                    img = Image.open(io.BytesIO(data))
                    # 每个供应商单独子目录
                    sub_dir = os.path.join(images_dir, f"dsaza_{supplier_id}")
                    os.makedirs(sub_dir, exist_ok=True)
                    fname = f"{sku}.jpg"
                    img.convert('RGB').save(os.path.join(sub_dir, fname), 'JPEG', quality=85)
                    image_path = f"/images/dsaza_{supplier_id}/{fname}"
                except Exception:
                    pass

            # 分类格式：Baño::ACCESORIOS → Baño > ACCESORIOS
            category = current_category.replace('::', ' > ')

            products.append({
                "sku": sku,
                "name": name[:300],
                "price": price,
                "category": category,
                "image": image_path,
            })

    return products


# ── 格式2: 单列新商品 ──────────────────────────────────────────

def _parse_new_page(page, images_dir: str, supplier_id: int) -> list:
    """解析单列布局的新商品PDF页"""
    import os
    from PIL import Image

    words = page.extract_words()
    page_height = page.height
    rows = defaultdict(list)
    for w in words:
        y_key = round(w['top'] / 3) * 3
        rows[y_key].append(w)

    # 图片列表（过滤logo小图）
    img_list = []
    for pimg in page.images:
        if pimg['height'] < 50:
            continue
        img_list.append({
            **pimg,
            'img_top': page_height - pimg['y1'],
            'img_bottom': page_height - pimg['y0'],
        })

    # 找出所有SKU行的y坐标
    sorted_ys = sorted(rows.keys())
    sku_y_indices = []  # (y_key, idx_in_sorted_ys)
    for idx, y_key in enumerate(sorted_ys):
        row = rows[y_key]
        row_text = ' '.join(w['text'] for w in row)
        if 'Codigo' in row_text or 'Descripcion' in row_text:
            continue
        if re.search(r'\d{5,7}', row_text) and re.search(r'\$\s*[\d\.,]+', row_text):
            sku_y_indices.append((y_key, idx))

    products = []

    for sku_idx, (y_key, idx) in enumerate(sku_y_indices):
        row = rows[y_key]
        row_text = ' '.join(w['text'] for w in row)

        sku_match = re.search(r'(\d{5,7})', row_text)
        price_match = re.search(r'\$\s*([\d\.,]+)', row_text)
        if not sku_match or not price_match:
            continue

        sku = sku_match.group(1)
        price = _clean_price(price_match.group(0))

        # 确定名称收集的y范围：相邻SKU行中点
        upper_y = y_key
        if sku_idx > 0:
            prev_sku_y = sku_y_indices[sku_idx - 1][0]
            upper_y = prev_sku_y + (y_key - prev_sku_y) // 2 + 5
        else:
            for check_y in sorted_ys[:idx]:
                check_text = ' '.join(w['text'] for w in rows[check_y])
                if 'Bulto' in check_text:
                    upper_y = check_y + 5

        lower_y = y_key + 100
        if sku_idx < len(sku_y_indices) - 1:
            next_sku_y = sku_y_indices[sku_idx + 1][0]
            lower_y = y_key + (next_sku_y - y_key) // 2

        # 收集名称文字
        name_parts = []

        # SKU行中SKU之后、$之前的文字（同行描述）
        between_parts = []
        found_sku = False
        for w in sorted(row, key=lambda x: x['x0']):
            if w['text'] == sku:
                found_sku = True
                continue
            if not found_sku:
                continue
            if '$' in w['text'] or re.match(r'^[\d\.,]+$', w['text']):
                break
            between_parts.append(w['text'])
        if between_parts:
            name_parts.append(' '.join(between_parts))

        # 范围内的描述行（x0 > 200，跳过.JPG行和价格行）
        for check_y in sorted_ys:
            if check_y <= upper_y or check_y >= lower_y:
                continue
            check_row = rows[check_y]
            check_text = ' '.join(w['text'] for w in check_row)
            if re.match(r'^\d{5,7}\.JPG', check_text):
                continue
            if re.search(r'\$\s*[\d\.,]+', check_text) and re.search(r'\d{5,7}', check_text):
                continue
            desc_words = [w['text'] for w in check_row if w['x0'] > 200]
            if desc_words:
                name_parts.append(' '.join(desc_words))

        name = re.sub(r'\s+', ' ', ' '.join(name_parts)).strip()

        # 找图片：左侧列(x0 60-220)，靠近SKU行y坐标
        image_path = None
        best_img = None
        for pimg in img_list:
            img_center_y = (pimg['img_top'] + pimg['img_bottom']) / 2
            if abs(img_center_y - y_key) < 80 or abs(pimg['img_bottom'] - y_key) < 30:
                if 60 < pimg['x0'] < 220:
                    if best_img is None or abs(pimg['img_bottom'] - y_key) < abs(best_img['img_bottom'] - y_key):
                        best_img = pimg

        if best_img:
            try:
                data = best_img['stream'].get_data()
                img = Image.open(io.BytesIO(data))
                sub_dir = os.path.join(images_dir, f"dsaza_{supplier_id}")
                os.makedirs(sub_dir, exist_ok=True)
                fname = f"{sku}.jpg"
                img.convert('RGB').save(os.path.join(sub_dir, fname), 'JPEG', quality=85)
                image_path = f"/images/dsaza_{supplier_id}/{fname}"
            except Exception:
                pass

        if not name or price <= 0:
            continue

        products.append({
            "sku": sku,
            "name": name[:300],
            "price": price,
            "category": "",  # 新格式无分类
            "image": image_path,
        })

    return products
