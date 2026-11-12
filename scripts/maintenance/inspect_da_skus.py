# -*- coding: utf-8 -*-
import sys
import fitz
import re

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)

found_skus = []
for pidx, page in enumerate(doc):
    text = page.get_text()
    for m in re.finditer(r'\b(DA\s*\d+[A-Za-z]?)\b', text, re.IGNORECASE):
        raw = m.group(1).strip()
        found_skus.append((pidx+1, raw))

doc.close()

# 统计不同格式
print(f"Total raw matches: {len(found_skus)}")
print("First 20 raw matches:")
for p, s in found_skus[:20]:
    print(f"  P.{p}: {repr(s)}")

# 检查是否有单数位 DA 1 还是都是 DA 01
single_digits = [s for p, s in found_skus if re.search(r'\bDA\s*[1-9]\b', s, re.I)]
print(f"Single digits (DA 1..9): {len(single_digits)}: {single_digits}")

double_digits_zero = [s for p, s in found_skus if re.search(r'\bDA\s*0[1-9]\b', s, re.I)]
print(f"Zero-padded (DA 01..09): {len(double_digits_zero)}: {double_digits_zero}")

# 检查是否有字母后缀
letter_suffix = [s for p, s in found_skus if re.search(r'[A-Za-z]$', s) and not s.upper().startswith('DA')]
print(f"Letter suffixes: {letter_suffix}")
