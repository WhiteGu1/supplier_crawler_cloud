# -*- coding: utf-8 -*-
import os
import fitz

def search_dir(d):
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.endswith('.pdf'):
                p = os.path.join(root, f)
                try:
                    doc = fitz.open(p)
                    for pidx, page in enumerate(doc):
                        text = page.get_text()
                        if 'C02109OR' in text:
                            print(f"FOUND 'C02109OR' in {p} page {pidx+1}")
                        if '8.305' in text or '8305' in text:
                            print(f"FOUND '8305' in {p} page {pidx+1}")
                except Exception:
                    pass

print("Searching D:/projects...")
search_dir(r"D:\projects\supplier_crawler")
print("Searching C:/Users/Administrator/Downloads...")
search_dir(r"C:\Users\Administrator\Downloads")
print("Done.")
