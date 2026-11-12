# -*- coding: utf-8 -*-
import fitz

doc = fitz.open(r"C:\Users\Administrator\Downloads\CATALOGO CONTINUO.pdf")
page = doc[17] # page 18 (0-indexed 17)

print("Page rect:", page.rect)
img_infos = page.get_image_info(xrefs=True)
print(f"Total image bboxes on page 18: {len(img_infos)}")
for idx, info in enumerate(img_infos):
    print(f"Img {idx}: xref={info['xref']}, bbox={info['bbox']}, width={info['width']}, height={info['height']}")

print("\n--- Text blocks on page 18 ---")
blocks = page.get_text("blocks")
for b in sorted(blocks, key=lambda x: (x[1], x[0])):
    print(f"Bbox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) -> {b[4].strip()[:60]}...")
