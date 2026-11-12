# -*- coding: utf-8 -*-
import fitz

doc = fitz.open(r"C:\Users\Administrator\Downloads\CATALOGO CONTINUO.pdf")
print("Total pages:", len(doc))
for p in range(min(10, len(doc))):
    txt = doc[p].get_text()
    fl = txt.splitlines()[0] if txt.splitlines() else ''
    print(f"Page {p+1}: len={len(txt)}, SKU={'SKU:' in txt}, Codigo={'Código' in txt}, Bulto={'Bulto:' in txt} | {fl}")

print("\n--- Checking Page 18 specifically ---")
p18 = doc[17] # 0-indexed
print("Page 18 text:")
print(p18.get_text())

print("Page 18 images:")
for img_info in p18.get_images():
    print(img_info)
