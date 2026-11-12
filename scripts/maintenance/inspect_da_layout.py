# -*- coding: utf-8 -*-
import sys
import pdfplumber
import fitz

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

with pdfplumber.open(pdf_path) as pdf:
    for pidx in [2, 3, 4, 10, 20]:
        page = pdf.pages[pidx]
        print(f"\n==================== Page {pidx+1} size: {page.width} x {page.height} ====================")
        words = page.extract_words()
        da_words = [w for w in words if w['text'] == 'DA' or w['text'].startswith('DA')]
        print(f"DA tokens ({len(da_words)}):")
        for w in da_words:
            # 找到紧随其后的词
            idx = words.index(w)
            following = " ".join(words[j]['text'] for j in range(idx, min(idx+6, len(words))))
            print(f"  x0={w['x0']:.1f}, top={w['top']:.1f}: {following}")
            
        print(f"\nImages ({len(page.images)}):")
        for i, im in enumerate(page.images):
            print(f"  Img {i}: x0={im['x0']:.1f}, x1={im['x1']:.1f}, top={im['top']:.1f}, bottom={im['bottom']:.1f}, w={im['width']:.1f}, h={im['height']:.1f}")
