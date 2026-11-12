# -*- coding: utf-8 -*-
"""
Gaston 供应商 PDF 解析器
同一个供应商多份货单:
  - CATALOGO_SP_*.pdf  : A4, 3列网格, 图片在上, SKU: 代码 + 名称 + Empaque: Caja x N + $价格
  - GENERALES DA *.pdf : 半页高, 2列, 图片在中, 名称/Código在图片上方, Bulto/$/Minimo在图片下方
  - CATALOGO ROTACION  : A4, 3列网格, 图片在上, 代码 + 名称 + 描述 + Bulto + $价格
  - WhatsApp 图        : 母亲节电子目录 3x3=9 商品, "SBK-" 货号, 通过 gaston_wa.py 辅助脚本处理

支持从 PDF 内嵌图片提取商品图（优先 fitz/PyMuPDF，兼容 pdfplumber）。
"""

import re, io, os
from collections import defaultdict

PARSER_NAME = "gaston — Gaston 目录 (SKU/Código/ROTACION 网格)"
PARSER_DESC = "适用于 Gaston 家 CATALOGO_SP、GENERALES 与 ROTACION 等货单PDF，网格布局+内嵌图片"


def parse(pdf_path: str, images_dir: str, supplier_id: int) -> list:
    import pdfplumber
    try:
        import fitz
    except ImportError:
        fitz = None

    fitz_doc = fitz.open(pdf_path) if fitz else None
    if fitz_doc:
        first_pages_text = "".join(fitz_doc[min(i, len(fitz_doc)-1)].get_text() for i in range(min(5, len(fitz_doc))))
        if 'DA 01' in first_pages_text or 'DON ABRAHAM' in first_pages_text.upper():
            da_products = _parse_don_abraham_pdf(fitz_doc, images_dir, supplier_id)
            if da_products:
                fitz_doc.close()
                return da_products

    products, seen = [], set()
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for pidx, page in enumerate(pdf.pages):
                fitz_page = fitz_doc[pidx] if fitz_doc and pidx < len(fitz_doc) else None
                products.extend(_parse_page(page, fitz_page, fitz_doc, images_dir, supplier_id, seen))
    finally:
        if fitz_doc:
            fitz_doc.close()
    return products


def _clean_price(text: str) -> float:
    text = re.sub(r'[^\d\.,]', '', text)
    if re.search(r'\d\.\d{3},\d{2}', text):       # 55.587,26
        text = text.replace('.', '').replace(',', '.')
    elif re.search(r'\d,\d{2}$', text):           # 18.612,79
        text = text.replace(',', '.')
    elif re.search(r'\.\d{3}$', text):            # 20.146, 43.320, 1.430
        text = text.replace('.', '')
    elif text.count('.') > 1:                     # 1.875
        text = text.replace('.', '')
    nums = re.findall(r'\d+\.?\d*', text)
    return float(nums[0]) if nums else 0.0


def _parse_page(page, fitz_page, fitz_doc, images_dir: str, supplier_id: int, seen: set) -> list:
    words = page.extract_words(x_tolerance=2, y_tolerance=3)
    if not words:
        return []
    text = page.extract_text() or ""
    if 'SKU:' in text:
        fmt = 'catalogo'
    elif 'Código' in text:
        fmt = 'generales'
    elif 'Bulto:' in text or 'Bulo:' in text:
        fmt = 'rotacion'
    else:
        return []

    if fmt == 'rotacion':
        return _parse_rotacion(page, fitz_page, fitz_doc, words, images_dir, supplier_id, seen)

    img_list = [im for im in page.images if 40 <= im['width'] < 400]
    anchor_tok = 'SKU:' if fmt == 'catalogo' else 'Código'
    anchors = [w for w in words if w['text'] == anchor_tok]
    if not anchors:
        return []

    # 列聚类: anchor x0 (容差15px)
    raw_xs = sorted(set(round(a['x0']) for a in anchors))
    col_xs = [raw_xs[0]]
    for x in raw_xs[1:]:
        if x - col_xs[-1] > 15:
            col_xs.append(x)

    # 列 x 范围: [anchor_x0 - 15, 下一列 anchor_x0 - 15)，末列到页宽
    def col_range(i):
        lo = col_xs[i] - 15
        hi = (col_xs[i + 1] - 15) if i + 1 < len(col_xs) else page.width
        return lo, hi

    def col_of(x0):
        best, bd = 0, 1e9
        for i, c in enumerate(col_xs):
            d = abs(x0 - c)
            if d < bd:
                bd, best = d, i
        return best

    sorted_anchors = sorted(anchors, key=lambda w: (col_of(w['x0']), w['top']))
    col_anchors = defaultdict(list)
    for w in sorted_anchors:
        col_anchors[col_of(w['x0'])].append(w)

    out = []
    sub_dir = os.path.join(images_dir, f"gaston_{supplier_id}")
    os.makedirs(sub_dir, exist_ok=True)

    for col, alist in col_anchors.items():
        lo, hi = col_range(col)
        for idx, a in enumerate(alist):
            top = a['top']
            nxt = alist[idx + 1]['top'] if idx + 1 < len(alist) else page.height
            prev_top = alist[idx - 1]['top'] if idx > 0 else 0
            if fmt == 'catalogo':
                product = _parse_catalogo(words, a, nxt, lo, hi, img_list,
                                          sub_dir, supplier_id, idx, seen,
                                          prev_top=prev_top, fitz_page=fitz_page, fitz_doc=fitz_doc)
            else:
                product = _parse_generales(words, a, top, nxt, lo, hi, img_list,
                                           sub_dir, supplier_id, idx, seen)
            if product:
                out.append(product)
    return out


# CATALOGO: SKU: <code> <名称...> Empaque: Caja x N unidades $ <价格>
_CATALOGO_STOP = {'Empaque:', '$', 'SIN', 'STOCK', 'Artículos'}


def _parse_catalogo(words, anchor, nxt, lo, hi, img_list, sub_dir, sid, idx, seen,
                    prev_top=0, fitz_page=None, fitz_doc=None):
    top = anchor['top']
    band = [w for w in words if lo - 2 <= w['x0'] and w['x1'] <= hi + 2
            and top - 4 <= w['top'] < nxt]
    band.sort(key=lambda w: (w['top'], w['x0']))
    band_text = ' '.join(w['text'] for w in band)

    m = re.search(r'SKU:\s*([A-Za-z0-9][A-Za-z0-9\-]{2,})', band_text)
    if not m:
        return None
    code = m.group(1)

    # 价格
    price, price_str = 0.0, ''
    pm = re.search(r'\$\s*([\d\.,]+)', band_text)
    if pm:
        price_str = pm.group(1)
        if price_str != '-' and re.search(r'\d', price_str):
            price = _clean_price(price_str)

    # 名称: SKU: 之后, 跳过 code 本身, 到 Empaque:/$/SIN 停止
    name_parts, started, skipped_code = [], False, False
    for w in band:
        t = w['text']
        if t == 'SKU:':
            started = True
            continue
        if not started:
            continue
        if not skipped_code and t == code:
            skipped_code = True   # 跳过 SKU 代码，不 break
            continue
        if t in _CATALOGO_STOP:
            break
        if t == price_str:
            break
        name_parts.append(t)
    name = re.sub(r'\s+', ' ', ' '.join(name_parts).strip())
    if not name:
        return None

    # 图片提取：图片位于 SKU: 文字上方 [prev_top, top]
    img_path = None
    if fitz_page and fitz_doc:
        fitz_img_infos = fitz_page.get_image_info(xrefs=True)
        best_xref, best_d = None, 1e9
        cell_mid_x = (lo + hi) / 2
        cell_mid_y = (prev_top + top) / 2
        for info in fitz_img_infos:
            bbox = info.get('bbox')
            if not bbox or info.get('width', 0) < 60 or info.get('height', 0) < 60:
                continue
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            if (lo - 15 <= cx <= hi + 15) and (prev_top - 5 <= cy <= top + 10):
                d = (cx - cell_mid_x)**2 + (cy - cell_mid_y)**2
                if d < best_d:
                    best_d = d
                    best_xref = info.get('xref')
        if best_xref:
            try:
                from PIL import Image
                base_im = fitz_doc.extract_image(best_xref)
                im_obj = Image.open(io.BytesIO(base_im['image']))
                fname = f"{code}.jpg"
                fp = os.path.join(sub_dir, fname)
                im_obj.convert('RGB').save(fp, 'JPEG', quality=85)
                img_path = f"/images/gaston_{sid}/{fname}"
            except Exception:
                img_path = None

    if not img_path:
        img_path = _save_image(img_list, lo, hi, prev_top, top, sub_dir, sid, code, idx)

    key = (code, name[:30])
    if key in seen:
        return None
    seen.add(key)
    return {"sku": code, "name": name[:300], "price": price, "category": "", "image": img_path}


# GENERALES: 名称/Código 在图片上方, Bulto/$/Minimo 在图片下方
_SKIP_TOKENS = {'Código', 'T', 'D', 'BIFAZ', 'Bulto:', 'Minimo:', '$'}


def _parse_generales(words, anchor, top, nxt, lo, hi, img_list, sub_dir, sid, idx, seen):
    upper = [w for w in words if lo - 2 <= w['x0'] and w['x1'] <= hi + 2
             and top - 80 <= w['top'] <= top + 3]
    upper.sort(key=lambda w: (w['top'], w['x0']))
    upper_text = ' '.join(w['text'] for w in upper)

    m = re.search(r'Código\s+([A-Za-z]{1,4}-?\d{2,5}[A-Za-z]?)', upper_text)
    if not m:
        return None
    code = m.group(1)

    lower = [w for w in words if lo - 2 <= w['x0'] and w['x1'] <= hi + 2
             and top + 5 <= w['top'] < nxt]
    lower.sort(key=lambda w: (w['top'], w['x0']))
    lower_text = ' '.join(w['text'] for w in lower)

    price = 0.0
    pm = re.search(r'\$\s*([\d\.,]+)', lower_text)
    if pm and pm.group(1) != '-' and re.search(r'\d', pm.group(1)):
        price = _clean_price(pm.group(1))

    name_parts = []
    for w in upper:
        t = w['text']
        if t in _SKIP_TOKENS:
            continue
        if t == code:
            continue
        if t.startswith('$') or re.fullmatch(r'[\d\.,]+', t):
            continue
        name_parts.append(t)

    deduped = []
    for p in name_parts:
        if not deduped or deduped[-1] != p:
            deduped.append(p)
    name = re.sub(r'\s+', ' ', ' '.join(deduped).strip())
    if not name:
        return None

    img_path = _save_image(img_list, lo, hi, top, nxt, sub_dir, sid, code, idx)
    key = (code, name[:30])
    if key in seen:
        return None
    seen.add(key)
    return {"sku": code, "name": name[:300], "price": price, "category": "", "image": img_path}


# ROTACION: 3列网格，图片在上，下方依序为 SKU / 名称 / 描述 / Bulto / $价格
def _parse_rotacion(page, fitz_page, fitz_doc, words, images_dir: str, supplier_id: int, seen: set) -> list:
    sub_dir = os.path.join(images_dir, f"gaston_{supplier_id}")
    os.makedirs(sub_dir, exist_ok=True)

    # 提取顶部分类
    top_words = [w for w in words if w['top'] < 30]
    cat_raw = ''.join(w['text'] for w in sorted(top_words, key=lambda w: w['x0']))
    cat_clean = re.sub(r'\s+', '', cat_raw).capitalize()

    col_bounds = [(15, 205), (205, 395), (395, 585)]
    row_configs = [
        {"row": 0, "img_y": (25, 220), "sku_y": (190, 205), "name_y": (208, 235), "desc_y": (235, 255), "price_y": (268, 290)},
        {"row": 1, "img_y": (290, 485), "sku_y": (455, 472), "name_y": (475, 502), "desc_y": (502, 522), "price_y": (535, 560)},
        {"row": 2, "img_y": (560, 755), "sku_y": (725, 742), "name_y": (745, 770), "desc_y": (770, 790), "price_y": (805, 830)},
    ]

    fitz_img_infos = fitz_page.get_image_info(xrefs=True) if fitz_page else []
    page_images = [im for im in page.images if 40 <= im['width'] < 400] if hasattr(page, 'images') else []

    out = []
    for r_cfg in row_configs:
        for c_idx, (lo_x, hi_x) in enumerate(col_bounds):
            sku_words = [w for w in words if lo_x <= w['x0'] < hi_x and r_cfg['sku_y'][0] <= w['top'] <= r_cfg['sku_y'][1]]
            if not sku_words:
                continue
            sku = ''.join(w['text'] for w in sku_words).strip()
            if not re.match(r'^[A-Za-z0-9\-]{4,}$', sku):
                continue

            name_words = [w for w in words if lo_x <= w['x0'] < hi_x and r_cfg['name_y'][0] <= w['top'] <= r_cfg['name_y'][1]]
            name = ' '.join(w['text'] for w in sorted(name_words, key=lambda w: (w['top'], w['x0']))).strip()
            if not name:
                continue

            price_words = [w for w in words if lo_x <= w['x0'] < hi_x and r_cfg['price_y'][0] <= w['top'] <= r_cfg['price_y'][1]]
            price_str = ' '.join(w['text'] for w in sorted(price_words, key=lambda w: w['x0'])).strip()
            price = _clean_price(price_str)

            # 图片提取：优先用 fitz
            img_path = None
            if fitz_page and fitz_doc and fitz_img_infos:
                best_xref, best_d = None, 1e9
                cell_mid_x = (lo_x + hi_x) / 2
                cell_mid_y = (r_cfg['img_y'][0] + r_cfg['img_y'][1]) / 2
                for info in fitz_img_infos:
                    bbox = info.get('bbox')
                    if not bbox:
                        continue
                    cx = (bbox[0] + bbox[2]) / 2
                    cy = (bbox[1] + bbox[3]) / 2
                    if lo_x <= cx <= hi_x and r_cfg['img_y'][0] <= cy <= r_cfg['img_y'][1]:
                        d = (cx - cell_mid_x)**2 + (cy - cell_mid_y)**2
                        if d < best_d:
                            best_d = d
                            best_xref = info.get('xref')
                if best_xref:
                    try:
                        from PIL import Image
                        base_im = fitz_doc.extract_image(best_xref)
                        im_data = base_im['image']
                        im_obj = Image.open(io.BytesIO(im_data))
                        fname = f"{sku}.jpg"
                        fp = os.path.join(sub_dir, fname)
                        im_obj.convert('RGB').save(fp, 'JPEG', quality=85)
                        img_path = f"/images/gaston_{supplier_id}/{fname}"
                    except Exception:
                        img_path = None

            # 兜底：使用 pdfplumber 图片
            if not img_path and page_images:
                img_path = _save_image(page_images, lo_x, hi_x, r_cfg['img_y'][0], r_cfg['img_y'][1], sub_dir, supplier_id, sku, c_idx)

            key = (sku, name[:30])
            if key in seen:
                continue
            seen.add(key)

            out.append({
                "sku": sku,
                "name": name[:300],
                "price": price,
                "category": cat_clean,
                "image": img_path
            })
    return out


def _save_image(img_list, lo, hi, y0, y1, sub_dir, sid, code, idx):
    try:
        from PIL import Image
    except ImportError:
        return None
    band_mid = (y0 + y1) / 2
    best, best_d = None, 1e9
    for im in img_list:
        cx = (im['x0'] + im['x1']) / 2
        if not (lo - 5 <= cx <= hi + 5):
            continue
        ic = (im['top'] + im['bottom']) / 2
        d = abs(ic - band_mid)
        if d < best_d:
            best_d, best = d, im
    if not best:
        return None
    try:
        data = best['stream'].get_data()
        try:
            img = Image.open(io.BytesIO(data))
        except Exception:
            filt = best['stream'].attrs.get('Filter')
            if filt == '/FlateDecode':
                w = best['stream'].attrs.get('Width', int(best['width']))
                h = best['stream'].attrs.get('Height', int(best['height']))
                img = Image.frombytes('RGB', (w, h), data)
            else:
                return None
        fname = f"{code}.jpg"
        fp = os.path.join(sub_dir, fname)
        if os.path.exists(fp):
            fname = f"{code}_{idx}.jpg"
            fp = os.path.join(sub_dir, fname)
        img.convert('RGB').save(fp, 'JPEG', quality=85)
        return f"/images/gaston_{sid}/{fname}"
    except Exception:
        return None


def _parse_don_abraham_pdf(fitz_doc, images_dir: str, supplier_id: int) -> list:
    """
    解析 CATÁLOGO DON ABRAHAM (DA 01 ~ DA 401)
    - 3列 x 3行 网格布局
    - 蓝色矩形标题条内含 DA 货号
    - 标题条下方为正方形实物图片
    - 图片下方为品名、包装规格参数及药丸价格
    """
    try:
        from PIL import Image
    except ImportError:
        Image = None

    sub_dir = os.path.join(images_dir, f"gaston_{supplier_id}")
    os.makedirs(sub_dir, exist_ok=True)
    
    current_cat = "General"
    section_noise = {'D&A', 'DISTRIBUIDORA', 'DON ABRAHAM', 'CATÁLOGO DE', 'ARTÍCULOS', 'BAZAR • HOGAR • REGALERIA', '2026', 'D I S T R I B U I D O R A'}

    products = []
    seen = set()
    scale = 150.0 / 72.0  # 150 DPI

    for pidx in range(len(fitz_doc)):
        page = fitz_doc[pidx]
        pno = pidx + 1
        page_text = page.get_text()
        
        # 1. 检查分类分割页
        has_da = bool(re.search(r'\bDA\s*\d+\b', page_text, re.I))
        if not has_da and 1 < pno < len(fitz_doc):
            lines = [l.strip() for l in page_text.split('\n') if l.strip()]
            cat_lines = []
            for l in lines:
                if re.search(r'\d{4}', l) or '@' in l or re.search(r'\b\d{2}\s*\d{4}\b', l):
                    continue
                if any(n in l.upper() for n in section_noise) or 'D I S T R I B U I D O R A' in l.upper():
                    continue
                cat_lines.append(l)
            if cat_lines:
                dedup = []
                for cl in cat_lines:
                    if cl not in dedup:
                        dedup.append(cl)
                current_cat = " ".join(dedup).strip().title()
            continue

        if not has_da:
            continue

        # 2. 查找蓝色卡片标题条
        drawings = page.get_drawings()
        blue_rects = []
        for d in drawings:
            f = d.get('fill')
            if f and len(f) == 3:
                if f[0] < 0.25 and f[1] < 0.35 and f[2] > 0.65:
                    r = d['rect']
                    if 120 <= (r.x1 - r.x0) <= 165 and 12 <= (r.y1 - r.y0) <= 30:
                        blue_rects.append(r)
                        
        blue_rects.sort(key=lambda r: (round(r.y0 / 100) * 100, r.x0))
        if not blue_rects:
            continue

        # 渲染当前页图像（用于切图）
        page_img = None
        if Image:
            pix = page.get_pixmap(dpi=150)
            page_img = Image.open(io.BytesIO(pix.tobytes("jpeg")))
        
        words = page.get_text("words")

        for r in blue_rects:
            rx0, ry0, rx1, ry1 = r.x0, r.y0, r.x1, r.y1
            card_w = rx1 - rx0
            col_x0 = rx0 - 6
            col_x1 = rx1 + 6
            
            # 提取 SKU
            header_words = [w for w in words if col_x0 <= (w[0]+w[2])/2 <= col_x1 and ry0 - 6 <= (w[1]+w[3])/2 <= ry1 + 6]
            header_words.sort(key=lambda w: (w[1], w[0]))
            header_text = " ".join(w[4] for w in header_words)
            m = re.search(r'DA\s*(\d+)', header_text, re.I)
            if not m:
                continue
            num = int(m.group(1))
            sku = f"DA-{num:02d}"
            
            if sku in seen:
                continue
            seen.add(sku)

            # 切图并保存
            img_path = None
            if page_img:
                photo_rect = (rx0 + 1.5, ry1 + 1.5, rx1 - 1.5, ry1 + card_w - 1.5)
                crop_box = (
                    max(0, int(photo_rect[0] * scale)),
                    max(0, int(photo_rect[1] * scale)),
                    min(page_img.width, int(photo_rect[2] * scale)),
                    min(page_img.height, int(photo_rect[3] * scale))
                )
                cropped = page_img.crop(crop_box)
                fname = f"{sku}.jpg"
                fp = os.path.join(sub_dir, fname)
                cropped.save(fp, "JPEG", quality=90)
                img_path = f"/images/gaston_{supplier_id}/{fname}"

            # 提取文字
            text_y0 = ry1 + card_w - 2
            text_y1 = ry0 + 265
            cell_words = [w for w in words if col_x0 <= (w[0]+w[2])/2 <= col_x1 and text_y0 <= (w[1]+w[3])/2 <= text_y1]
            
            # 聚类为行
            cell_words.sort(key=lambda w: (w[1], w[0]))
            lines = []
            cur_line = []
            cur_y = None
            for w in cell_words:
                if cur_y is None or abs(w[1] - cur_y) < 5:
                    cur_line.append(w)
                    cur_y = w[1]
                else:
                    lines.append(cur_line)
                    cur_line = [w]
                    cur_y = w[1]
            if cur_line:
                lines.append(cur_line)
                
            line_texts = [" ".join(w[4] for w in ln).strip() for ln in lines if ln]
            
            price = 0.0
            name_parts = []
            desc_parts = []
            
            for lt in line_texts:
                if '$' in lt:
                    price = _clean_price(lt)
                elif 'CONSULTAR' in lt.upper():
                    price = 0.0
                elif re.search(r'\bBulto\b|\bMedidas?:|\bAltura:|\bDi[aá]metro:|\bCapacidad:|\b\d+\s*U\s*x\b', lt, re.I):
                    desc_parts.append(lt)
                else:
                    name_parts.append(lt)
                    
            name = " ".join(name_parts).strip()
            name = re.sub(r'\s+', ' ', name)
            if not name:
                name = f"ARTÍCULO {sku}"
            desc = " | ".join(desc_parts).strip()

            products.append({
                "sku": sku,
                "name": name[:300],
                "price": price,
                "category": current_cat,
                "image": img_path,
                "description": desc,
                "brand": "Don Abraham"
            })
            
    return products
