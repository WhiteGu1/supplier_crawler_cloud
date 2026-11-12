# -*- coding: utf-8 -*-
import sys
import fitz
import re

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)

blue_count = 0
da_count = 0

for pidx, page in enumerate(doc):
    text = page.get_text()
    da_matches = re.findall(r'\bDA\s*(\d+)\b', text, re.I)
    if not da_matches:
        continue
    da_count += len(da_matches)
    
    # 查找该页中的蓝色矩形
    drawings = page.get_drawings()
    blue_rects = []
    for d in drawings:
        f = d.get('fill')
        if f and len(f) == 3:
            # 蓝色: r < 0.25, g < 0.35, b > 0.65
            if f[0] < 0.25 and f[1] < 0.35 and f[2] > 0.65:
                r = d['rect']
                # 过滤尺寸符合标题条的矩形: 宽 130..160, 高 15..25
                if 120 <= (r.x1 - r.x0) <= 165 and 12 <= (r.y1 - r.y0) <= 30:
                    blue_rects.append(r)
    blue_count += len(blue_rects)
    if len(blue_rects) != len(da_matches):
        print(f"Page {pidx+1}: {len(da_matches)} DA items, but found {len(blue_rects)} blue rects!")

print(f"Total DA items: {da_count}, Total matching blue header rects: {blue_count}")
doc.close()
