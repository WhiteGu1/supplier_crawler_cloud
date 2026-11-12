# -*- coding: utf-8 -*-
import sys
import fitz
import re

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)

current_cat = "General"
section_noise = {'D&A', 'DISTRIBUIDORA', 'DON ABRAHAM', 'CATÁLOGO DE', 'ARTÍCULOS', 'BAZAR • HOGAR • REGALERIA', '2026', 'D I S T R I B U I D O R A'}

def clean_price(text: str) -> float:
    text = re.sub(r'[^\d\.,]', '', text)
    if not text:
        return 0.0
    # 阿根廷格式: 52.433 -> 52433, 1.081 -> 1081, 14.946 -> 14946
    # 如果有逗号如 1.234,50
    if ',' in text and '.' in text:
        text = text.replace('.', '').replace(',', '.')
    elif ',' in text:
        # 1234,50
        text = text.replace(',', '.')
    elif '.' in text:
        # 在该 PDF 中，千位分隔符都是点，如 $52.433, $14.946, $1.081
        text = text.replace('.', '')
    nums = re.findall(r'\d+\.?\d*', text)
    return float(nums[0]) if nums else 0.0

all_products = []

for pidx, page in enumerate(doc):
    pno = pidx + 1
    page_text = page.get_text()
    
    # 检查是否分类页
    has_da = bool(re.search(r'\bDA\s*\d+\b', page_text, re.I))
    if not has_da and 1 < pno < 62:
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

    # 获取蓝色矩形
    drawings = page.get_drawings()
    blue_rects = []
    for d in drawings:
        f = d.get('fill')
        if f and len(f) == 3:
            if f[0] < 0.25 and f[1] < 0.35 and f[2] > 0.65:
                r = d['rect']
                if 120 <= (r.x1 - r.x0) <= 165 and 12 <= (r.y1 - r.y0) <= 30:
                    blue_rects.append(r)
                    
    # 按从上到下、从左到右排序
    blue_rects.sort(key=lambda r: (round(r.y0 / 100) * 100, r.x0))
    
    # 获取页面所有词
    words = page.get_text("words")
    
    for r in blue_rects:
        rx0, ry0, rx1, ry1 = r.x0, r.y0, r.x1, r.y1
        card_w = rx1 - rx0
        col_x0 = rx0 - 6
        col_x1 = rx1 + 6
        
        # 1. 查找当前蓝色条内的文字（SKU）
        header_words = [w for w in words if col_x0 <= (w[0]+w[2])/2 <= col_x1 and ry0 - 6 <= (w[1]+w[3])/2 <= ry1 + 6]
        header_words.sort(key=lambda w: (w[1], w[0]))
        header_text = " ".join(w[4] for w in header_words)
        
        m = re.search(r'DA\s*(\d+)', header_text, re.I)
        if m:
            num = int(m.group(1))
            sku = f"DA-{num:02d}"
        else:
            sku = None
            
        # 2. 图片范围
        photo_rect = (rx0 + 1.5, ry1 + 1.5, rx1 - 1.5, ry1 + card_w - 1.5)
        
        # 3. 文字区域: 从 photo 底部到 card 底部
        text_y0 = ry1 + card_w - 2
        text_y1 = ry0 + 265
        
        cell_words = [w for w in words if col_x0 <= (w[0]+w[2])/2 <= col_x1 and text_y0 <= (w[1]+w[3])/2 <= text_y1]
        
        # 将词聚类为行
        # 按 y 排序
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
        desc = " | ".join(desc_parts).strip()
        
        all_products.append({
            "page": pno,
            "sku": sku,
            "name": name,
            "desc": desc,
            "price": price,
            "category": current_cat,
            "photo_rect": photo_rect
        })

doc.close()

print(f"Total products extracted: {len(all_products)}")
none_sku = [p for p in all_products if not p['sku']]
print(f"None SKU count: {len(none_sku)}")
empty_name = [p for p in all_products if not p['name']]
print(f"Empty Name count: {len(empty_name)}")
for en in empty_name:
    print("  Empty name item:", en)

# 检查 SKU 集合是否正好是 DA-01 到 DA-401
sku_set = {p['sku'] for p in all_products if p['sku']}
expected_skus = {f"DA-{i:02d}" for i in range(1, 402)}
diff = expected_skus - sku_set
print(f"Missing SKUs compared to DA-01..DA-401: {diff}")
print(f"Extra SKUs: {sku_set - expected_skus}")

print("\nCheck Page 43 & 44 items specifically:")
for p in all_products:
    if p['sku'] in ('DA-272', 'DA-273', 'DA-274', 'DA-281', 'DA-282', 'DA-283'):
        print(f"  [{p['sku']}] ${p['price']} | Name: {p['name']} | Desc: {p['desc']}")
