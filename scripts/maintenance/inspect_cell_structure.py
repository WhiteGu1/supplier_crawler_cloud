# -*- coding: utf-8 -*-
import sys
import fitz
import re

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)

for pno in [3, 4]:
    page = doc[pno - 1]
    print(f"\n================ Page {pno} ================")
    
    # 找本页分类 (一般在 top < 55)
    blocks = page.get_text("blocks")
    cat = ""
    for b in blocks:
        if b[1] < 55:
            # 排除 CATALOGO DE ARTICULOS 2026
            lines = [l.strip() for l in b[4].split('\n') if l.strip()]
            for l in lines:
                if 'CATÁLOGO' not in l.upper() and '2026' not in l and l:
                    cat = l
                    break
    print(f"Detected Category: {cat}")
    
    # 找所有 DA 锚点
    da_blocks = []
    for b in blocks:
        m = re.search(r'\bDA\s*(\d+)\b', b[4], re.I)
        if m:
            da_blocks.append({
                "num": int(m.group(1)),
                "sku": f"DA-{int(m.group(1)):02d}",
                "bbox": b[:4],
                "raw": b[4].strip()
            })
    da_blocks.sort(key=lambda d: d['num'])
    
    for d in da_blocks:
        print(f"\n--- Item {d['sku']} (bbox: {d['bbox']}) ---")
        bx0, by0, bx1, by1 = d['bbox']
        # 确定该 cell 的 x 和 y 范围
        # 列:
        if bx0 < 200:
            col_x = (20, 200)
        elif bx0 < 370:
            col_x = (200, 395)
        else:
            col_x = (395, 580)
            
        # 行: 
        if by0 < 250:
            row_y = (by0, by0 + 260)
        elif by0 < 500:
            row_y = (by0, by0 + 260)
        else:
            row_y = (by0, min(840, by0 + 260))
            
        # 收集该 cell 范围内的文字块
        cell_blocks = [b for b in blocks if col_x[0] <= (b[0]+b[2])/2 <= col_x[1] and row_y[0] <= (b[1]+b[3])/2 <= row_y[1]]
        cell_blocks.sort(key=lambda b: (b[1], b[0]))
        for cb in cell_blocks:
            print(f"   text (y={cb[1]:.1f}..{cb[3]:.1f}): {repr(cb[4].strip())}")

doc.close()
