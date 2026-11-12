# -*- coding: utf-8 -*-
import sys
import fitz
import re

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

page_summary = []
all_da_skus = []

for pidx in range(len(doc)):
    page = doc[pidx]
    text = page.get_text()
    
    # 查找所有 DA 货号
    # 典型如 DA 01, DA 02, DA 123, DA 12B 等
    da_matches = re.findall(r'\b(DA\s*\d{1,4}[A-Za-z]?)\b', text, re.IGNORECASE)
    # 去重保留顺序
    unique_da = []
    for m in da_matches:
        norm = re.sub(r'\s+', ' ', m.strip().upper())
        if norm not in unique_da:
            unique_da.append(norm)
            
    # 查找价格 ($xxx)
    price_matches = re.findall(r'\$\s*(\d[\d\.,]*)', text)
    
    # 查找页内可能的分类名（通常在前几行）
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    first_few = " | ".join(lines[:4])
    
    page_summary.append({
        "page_num": pidx + 1,
        "width": page.rect.width,
        "height": page.rect.height,
        "da_count": len(unique_da),
        "da_list": unique_da,
        "price_count": len(price_matches),
        "preview": first_few
    })
    all_da_skus.extend(unique_da)

print(f"\nTotal unique DA SKUs found across document: {len(set(all_da_skus))}")
print(f"Total DA SKU occurrences: {len(all_da_skus)}")

print("\n--- Page Breakdown ---")
for p in page_summary:
    if p['da_count'] > 0:
        print(f"P.{p['page_num']:02d}: {p['da_count']} items: {p['da_list']}")
    else:
        print(f"P.{p['page_num']:02d}: [COVER/SECTION] Preview: {p['preview'][:60]}")

doc.close()
