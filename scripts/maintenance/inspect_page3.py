# -*- coding: utf-8 -*-
import sys
import fitz

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)
page = doc[2] # page 3 (0-indexed 2)

# 保存整页截图查看布局
pix = page.get_pixmap(dpi=150)
pix.save("scripts/maintenance/page3_preview.png")
print("Saved scripts/maintenance/page3_preview.png")

# 查看 fitz 提取的图片信息
img_infos = page.get_image_info(xrefs=True)
print(f"fitz img_infos count: {len(img_infos)}")
for idx, info in enumerate(img_infos):
    print(f"Img {idx}: xref={info.get('xref')}, bbox={info.get('bbox')}, w={info.get('width')}, h={info.get('height')}")

# 查看所有文字块 (blocks)
blocks = page.get_text("blocks")
print(f"\nText blocks ({len(blocks)}):")
for b in blocks:
    print(f"  bbox=({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}): {b[4].strip()[:60]}")

doc.close()
