# -*- coding: utf-8 -*-
import sys
import fitz
import io
import os
import re
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

def parse_don_abraham_pdf(fitz_doc, images_dir: str, supplier_id: int) -> list:
    sub_dir = os.path.join(images_dir, f"gaston_{supplier_id}")
    os.makedirs(sub_dir, exist_ok=True)
    
    current_cat = "General"
    section_noise = {'D&A', 'DISTRIBUIDORA', 'DON ABRAHAM', 'CATÁLOGO DE', 'ARTÍCULOS', 'BAZAR • HOGAR • REGALERIA', '2026', 'D I S T R I B U I D O R A'}

    def clean_price(text: str) -> float:
        text = re.sub(r'[^\d\.,]', '', text)
        if not text:
            return 0.0
        if ',' in text and '.' in text:
            text = text.replace('.', '').replace(',', '.')
        elif ',' in text:
            text = text.replace(',', '.')
        elif '.' in text:
            text = text.replace('.', '')
        nums = re.findall(r'\d+\.?\d*', text)
        return float(nums[0]) if nums else 0.0

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
                    price = clean_price(lt)
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
                
            products.append({
                "sku": sku,
                "name": name[:300],
                "price": price,
                "category": current_cat,
                "image": img_path
            })
            
    return products

if __name__ == "__main__":
    pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"
    doc = fitz.open(pdf_path)
    prods = parse_don_abraham_pdf(doc, r"d:\projects\supplier_crawler\images", 16)
    doc.close()
    print(f"Extracted {len(prods)} products successfully!")
    print(f"Sample product: {prods[0]}")
    print(f"Sample product 200: {prods[200]}")
    print(f"Sample product 400: {prods[400]}")
