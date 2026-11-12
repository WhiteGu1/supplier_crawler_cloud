# -*- coding: utf-8 -*-
import sys
import fitz
import re

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)

for pno in [3, 4, 12, 31, 51]:
    page = doc[pno - 1]
    print(f"\n==================== Page {pno} ====================")
    blocks = page.get_text("blocks")
    
    # 打印前 3 个文本块（通常是页眉）
    print("--- Header Blocks ---")
    for b in blocks[:4]:
        print(f"  bbox=({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}): {repr(b[4].strip())}")
        
    # 打印所有包含 DA 的块和价格块
    print("\n--- Product Blocks Preview ---")
    for b in blocks:
        text = b[4].strip()
        if re.search(r'\bDA\s*\d+', text) or text.startswith('$') or 'Bulto' in text:
            print(f"  bbox=({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}): {repr(text)}")

doc.close()
