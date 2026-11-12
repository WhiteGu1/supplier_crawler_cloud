# -*- coding: utf-8 -*-
import sys
import fitz

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)
page = doc[2] # page 3

drawings = page.get_drawings()
print(f"Total drawings on page 3: {len(drawings)}")

for idx, d in enumerate(drawings):
    rect = d['rect']
    f = d.get('fill')
    c = d.get('color')
    # 只打印有 fill 的矩形
    if f:
        print(f"  Draw {idx:02d}: rect=({rect.x0:.1f}, {rect.y0:.1f}, {rect.x1:.1f}, {rect.y1:.1f}), fill={tuple(round(x, 2) for x in f)}")

doc.close()
