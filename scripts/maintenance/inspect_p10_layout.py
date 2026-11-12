# -*- coding: utf-8 -*-
import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = fitz.open(r"C:\Users\Administrator\Downloads\CATALOGO CONTINUO.pdf")
p10 = doc[9] # page 10 (0-indexed 9)

print("--- Page 10 text blocks ---")
for b in sorted(p10.get_text("blocks"), key=lambda x: (x[1], x[0])):
    print(f"Bbox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) -> {repr(b[4].strip())[:80]}")

print("\n--- Page 10 images ---")
for idx, info in enumerate(p10.get_image_info(xrefs=True)):
    print(f"Img {idx}: xref={info['xref']}, bbox={info['bbox']}, width={info['width']}, height={info['height']}")
