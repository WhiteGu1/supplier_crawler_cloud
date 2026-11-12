# -*- coding: utf-8 -*-
import sys
import fitz
import re

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)

# 分类映射
current_cat = "General"
section_noise = {'D&A', 'DISTRIBUIDORA', 'DON ABRAHAM', 'CATÁLOGO DE', 'ARTÍCULOS', 'BAZAR • HOGAR • REGALERIA', '2026'}

all_extracted = []

for pidx, page in enumerate(doc):
    pno = pidx + 1
    text = page.get_text()
    
    # 检查是否分类分割页
    has_da = bool(re.search(r'\bDA\s*\d+\b', text, re.I))
    if not has_da and 1 < pno < 62:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
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
    
    # 获取页面上所有文字块
    blocks = page.get_text("blocks")
    
    for r in blue_rects:
        rx0, ry0, rx1, ry1 = r.x0, r.y0, r.x1, r.y1
        card_w = rx1 - rx0
        
        # 1. 提取 SKU: 在蓝色矩形内或其微小容差范围内的文字
        sku = None
        for b in blocks:
            if rx0 - 5 <= (b[0]+b[2])/2 <= rx1 + 5 and ry0 - 5 <= (b[1]+b[3])/2 <= ry1 + 5:
                m = re.search(r'\bDA\s*(\d+)\b', b[4], re.I)
                if m:
                    num = int(m.group(1))
                    sku = f"DA-{num:02d}"
                    break
        if not sku:
            # 兜底查找
            for b in blocks:
                if rx0 - 10 <= (b[0]+b[2])/2 <= rx1 + 10 and ry0 - 15 <= (b[1]+b[3])/2 <= ry1 + 15:
                    m = re.search(r'\bDA\s*(\d+)\b', b[4], re.I)
                    if m:
                        num = int(m.group(1))
                        sku = f"DA-{num:02d}"
                        break
                        
        # 2. 图片范围
        photo_rect = (rx0 + 1.5, ry1 + 1.5, rx1 - 1.5, ry1 + card_w - 1.5)
        
        # 3. 文字区域: 从 photo 底部到 card 底部 (约 ry1 + card_w 到 ry1 + 250)
        text_y0 = ry1 + card_w - 2
        text_y1 = ry0 + 265
        
        cell_text_blocks = []
        for b in blocks:
            bcx = (b[0] + b[2]) / 2
            bcy = (b[1] + b[3]) / 2
            if rx0 - 8 <= bcx <= rx1 + 8 and text_y0 <= bcy <= text_y1:
                # 排除页眉等
                if 'CATÁLOGO DE' in b[4] or '2026' in b[4]:
                    continue
                cell_text_blocks.append(b)
                
        # 按 y 排序
        cell_text_blocks.sort(key=lambda b: (b[1], b[0]))
        
        # 提取价格和名称
        # 检查是否包含价格 ($xxx 或 CONSULTAR)
        price = 0.0
        name_parts = []
        desc_parts = []
        
        for b in cell_text_blocks:
            t = b[4].strip()
            pm = re.search(r'\$\s*([\d\.,]+)', t)
            if pm:
                p_clean = pm.group(1).replace('.', '').replace(',', '.')
                try:
                    price = float(p_clean)
                except:
                    price = 0.0
            elif 'CONSULTAR' in t.upper():
                price = 0.0
            else:
                # 区分品名和规格参数
                # 规格参数特征: Bulto, Medidas:, Altura:, Diámetro:, Capacidad:, xx CC, xx LT, xx ml
                lines = [l.strip() for l in t.split('\n') if l.strip()]
                for l in lines:
                    if re.search(r'\bBulto\b|\bMedidas?:|\bAltura:|\bDi[aá]metro:|\bCapacidad:|\b\d+\s*U\s*x\b', l, re.I):
                        desc_parts.append(l)
                    elif re.fullmatch(r'[\d\.,\s]+(?:LT|CC|ml|CM|MM|M)', l, re.I):
                        # 单独一行容量或尺寸，如 "750 LT", "1.5 LT" -> 归入品名描述
                        name_parts.append(l)
                    else:
                        name_parts.append(l)
                        
        name = " ".join(name_parts).strip()
        # 清理多余空格
        name = re.sub(r'\s+', ' ', name)
        desc = " | ".join(desc_parts).strip()
        
        all_extracted.append({
            "page": pno,
            "sku": sku,
            "name": name,
            "desc": desc,
            "price": price,
            "category": current_cat,
            "photo_rect": photo_rect
        })

doc.close()

print(f"Total extracted: {len(all_extracted)}")
# 统计检查
none_sku = [x for x in all_extracted if not x['sku']]
print(f"Items with None SKU: {len(none_sku)}")
empty_name = [x for x in all_extracted if not x['name']]
print(f"Items with Empty Name: {len(empty_name)}")
zero_price = [x for x in all_extracted if x['price'] == 0.0]
print(f"Items with $0 price: {len(zero_price)}")
for z in zero_price:
    print(f"  P.{z['page']} [{z['sku']}] {z['name']} (${z['price']})")

print("\n--- First 15 Samples ---")
for x in all_extracted[:15]:
    print(f"P.{x['page']:02d} [{x['sku']:6s}] ${x['price']:7.2f} | Cat: {x['category']:25s} | Name: {x['name'][:40]} | Desc: {x['desc']}")

print("\n--- Last 10 Samples ---")
for x in all_extracted[-10:]:
    print(f"P.{x['page']:02d} [{x['sku']:6s}] ${x['price']:7.2f} | Cat: {x['category']:25s} | Name: {x['name'][:40]} | Desc: {x['desc']}")
