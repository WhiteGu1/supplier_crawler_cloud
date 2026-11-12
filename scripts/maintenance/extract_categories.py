# -*- coding: utf-8 -*-
import sys
import fitz
import re

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)

section_map = {}
current_category = "General"

for pidx, page in enumerate(doc):
    pno = pidx + 1
    text = page.get_text()
    
    # 检查是否有 DA 商品
    has_da = bool(re.search(r'\bDA\s*\d+\b', text, re.I))
    
    # 检查分类分割页
    # 分割页特征：无 DA 商品，且有明显的分类大标题
    if not has_da and pno > 1 and pno < 62:
        # 提取标题
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        # 过滤掉地址、电话、邮箱、DON ABRAHAM、D&A等噪音
        noise = {'D&A', 'DISTRIBUIDORA', 'DON ABRAHAM', 'CATÁLOGO DE', 'ARTÍCULOS', 'BAZAR • HOGAR • REGALERIA', '2026'}
        cat_lines = []
        for l in lines:
            if re.search(r'\d{4}', l) or '@' in l or re.search(r'\b\d{2}\s*\d{4}\b', l):
                continue
            if any(n in l.upper() for n in noise):
                continue
            cat_lines.append(l)
        if cat_lines:
            # 去重
            dedup = []
            for cl in cat_lines:
                if cl not in dedup:
                    dedup.append(cl)
            current_category = " ".join(dedup).strip().title()
            print(f"Page {pno:02d} [SECTION]: '{current_category}'")
    
    # 记录该页所属分类
    section_map[pno] = current_category

print("\n--- Product Pages to Category Mapping ---")
for pno in range(1, len(doc) + 1):
    page = doc[pno - 1]
    text = page.get_text()
    da_list = re.findall(r'\bDA\s*(\d+)\b', text, re.I)
    if da_list:
        print(f"Page {pno:02d} ({len(da_list)} items, DA {da_list[0]}..DA {da_list[-1]}): Category = '{section_map[pno]}'")

doc.close()
