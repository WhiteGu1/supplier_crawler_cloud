# -*- coding: utf-8 -*-
import sys
import fitz
import io
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"

doc = fitz.open(pdf_path)
page = doc[2]

# 提取 xref 7779
try:
    img_data = doc.extract_image(7779)
    im1 = Image.open(io.BytesIO(img_data['image']))
    im1.save("scripts/maintenance/test_xref_7779.jpg")
    print(f"xref 7779 saved, size={im1.size}, format={img_data['ext']}")
except Exception as e:
    print("Error extracting xref 7779:", e)

# 从页面渲染图中切出 DA 01 的图片区域
# 页面尺寸为 595.5 x 842.25
# 测量 DA 01 的图片位置
# SKU 栏在 y ≈ 55..75, 名称在 y ≈ 224
# 宽度为列宽
pix = page.get_pixmap(dpi=200)
# dpi 200 下，scale = 200 / 72 = 2.7777777777777777
scale = 200 / 72.0
print(f"Pix size: {pix.width} x {pix.height}")

# DA 01 图片在 page 坐标系下的范围:
# x: 大约 68 到 215
# y: 大约 75 到 224
x0, y0, x1, y1 = 68 * scale, 75 * scale, 215 * scale, 224 * scale
page_img = Image.open(io.BytesIO(pix.tobytes("jpeg")))
crop1 = page_img.crop((int(x0), int(y0), int(x1), int(y1)))
crop1.save("scripts/maintenance/test_crop_da01.jpg", "JPEG", quality=95)
print(f"DA 01 crop saved, size={crop1.size}")

doc.close()
