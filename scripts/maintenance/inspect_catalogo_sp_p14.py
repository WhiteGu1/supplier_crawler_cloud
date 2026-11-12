# -*- coding: utf-8 -*-
import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"C:\Users\Administrator\Downloads\gaston\CATALOGO_SP_compressed-DZa5fbhjobJkk1dEMLOaNalotdlOFL.pdf"
doc = fitz.open(pdf_path)
page = doc[13] # page 14 (0-indexed 13)

print("=== Page 14 text blocks ===")
for b in sorted(page.get_text("blocks"), key=lambda x: (x[1], x[0])):
    print(f"Bbox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) -> {repr(b[4].strip())}")

print("\n=== Page 14 images ===")
for idx, info in enumerate(page.get_image_info(xrefs=True)):
    print(f"Img {idx}: xref={info['xref']}, bbox={info['bbox']}, width={info['width']}, height={info['height']}")
