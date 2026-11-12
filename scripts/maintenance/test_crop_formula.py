# -*- coding: utf-8 -*-
import sys
import fitz
import io
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)

# 渲染 Page 4 (pno=4, index=3)
page4 = doc[3]
scale = 2.0  # 144 DPI
pix = page4.get_pixmap(dpi=144)
img = Image.open(io.BytesIO(pix.tobytes("jpeg")))

# 检查 DA 10 (Col 0, Row 0 on Page 4)
# blue bar is roughly (69.0, 23.1, 214.5, 42.7)
# photo rect = (69.0, 42.7, 214.5, 42.7 + 145.5 = 188.2)
crop_rect = (int(69.0 * scale), int(42.7 * scale), int(214.5 * scale), int(188.2 * scale))
crop_da10 = img.crop(crop_rect)
crop_da10.save("scripts/maintenance/test_da10.jpg", "JPEG", quality=95)

# 检查 DA 01 (Col 0, Row 0 on Page 3)
page3 = doc[2]
pix3 = page3.get_pixmap(dpi=144)
img3 = Image.open(io.BytesIO(pix3.tobytes("jpeg")))
# blue bar on Page 3 is (69.2, 55.5, 214.6, 74.4)
# photo rect = (69.2, 74.4, 214.6, 74.4 + 145.5 = 219.9)
crop_rect3 = (int(69.2 * scale), int(74.4 * scale), int(214.6 * scale), int(219.9 * scale))
crop_da01 = img3.crop(crop_rect3)
crop_da01.save("scripts/maintenance/test_da01_exact.jpg", "JPEG", quality=95)

print("Saved test_da10.jpg and test_da01_exact.jpg")
doc.close()
