# -*- coding: utf-8 -*-
import fitz
import hashlib
import io
from PIL import Image

target_fp = r"images\gaston_16\C02109OR_0.jpg"
target_data = open(target_fp, 'rb').read()
target_im = Image.open(io.BytesIO(target_data))
print("Target image size:", target_im.size, target_im.mode)

doc = fitz.open(r"C:\Users\Administrator\Downloads\CATALOGO CONTINUO.pdf")
found = False

# 检查该 PDF 中所有图片
for pidx in range(len(doc)):
    page = doc[pidx]
    img_list = page.get_images()
    for img_info in img_list:
        xref = img_info[0]
        base_im = doc.extract_image(xref)
        im_bytes = base_im['image']
        try:
            im = Image.open(io.BytesIO(im_bytes)).convert('RGB')
            # 存为同样的 JPEG 测试
            buf = io.BytesIO()
            im.save(buf, 'JPEG', quality=85)
            h = hashlib.md5(buf.getvalue()).hexdigest()
            if h == hashlib.md5(target_data).hexdigest():
                print(f"EXACT MATCH on Page {pidx+1}, xref={xref}, bbox in page:")
                for info in page.get_image_info(xrefs=True):
                    if info['xref'] == xref:
                        print("  bbox:", info['bbox'])
                found = True
                break
        except Exception:
            pass
    if found:
        break

if not found:
    print("Not found with exact jpeg quality 85, comparing dimensions and pixels...")
    for pidx in range(len(doc)):
        page = doc[pidx]
        for img_info in page.get_images():
            xref = img_info[0]
            base_im = doc.extract_image(xref)
            if base_im['width'] == target_im.width and base_im['height'] == target_im.height:
                print(f"Dimension match ({base_im['width']}x{base_im['height']}): Page {pidx+1}, xref={xref}")
                for info in page.get_image_info(xrefs=True):
                    if info['xref'] == xref:
                        print("  bbox:", info['bbox'])
