# -*- coding: utf-8 -*-
import sys
import fitz
import re

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)

check_pages = [16, 20, 33, 39, 46, 47, 58, 61] # 1-based

for pno in check_pages:
    page = doc[pno - 1]
    print(f"\n================ Page {pno} ================")
    # 保存一页预览图看看少于9个商品时是怎么排版的
    pix = page.get_pixmap(dpi=100)
    pix.save(f"scripts/maintenance/page_{pno}_preview.png")
    
    # 打印所有的 text blocks
    blocks = page.get_text("blocks")
    da_blocks = [b for b in blocks if re.search(r'\bDA\s*\d+', b[4])]
    for b in da_blocks:
        print(f"  DA block: bbox=({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) -> {repr(b[4].strip())}")

doc.close()
