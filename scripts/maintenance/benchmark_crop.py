# -*- coding: utf-8 -*-
import sys, time, os, io
import fitz
from PIL import Image
import test_perfect_extract as pe

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"
out_dir = r"d:\projects\supplier_crawler\images\gaston_16"
os.makedirs(out_dir, exist_ok=True)

t0 = time.time()
doc = fitz.open(pdf_path)

# 按页分组
by_page = {}
for p in pe.all_products:
    by_page.setdefault(p['page'], []).append(p)

scale = 150.0 / 72.0  # 150 DPI

saved_count = 0
for pno in sorted(by_page.keys())[:3]: # 测试前3个商品页
    page = doc[pno - 1]
    pix = page.get_pixmap(dpi=150)
    page_img = Image.open(io.BytesIO(pix.tobytes("jpeg")))
    
    for item in by_page[pno]:
        r = item['photo_rect']
        crop_box = (int(r[0] * scale), int(r[1] * scale), int(r[2] * scale), int(r[3] * scale))
        cropped = page_img.crop(crop_box)
        fp = os.path.join(out_dir, f"{item['sku']}.jpg")
        cropped.save(fp, "JPEG", quality=90)
        saved_count += 1

doc.close()
t1 = time.time()
print(f"Cropped and saved {saved_count} images in {t1 - t0:.2f} seconds.")
