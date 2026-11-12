# -*- coding: utf-8 -*-
import fitz
import re, io, os
import sys
from collections import defaultdict
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"C:\Users\Administrator\Downloads\gaston\CATALOGO_SP_compressed-DZa5fbhjobJkk1dEMLOaNalotdlOFL.pdf"
doc = fitz.open(pdf_path)

# 测试 Page 14
page = doc[13]
words = []
# 获取单词
for b in page.get_text("words"):
    words.append({'x0': b[0], 'top': b[1], 'x1': b[2], 'bottom': b[3], 'text': b[4]})

anchors = [w for w in words if w['text'] == 'SKU:']
raw_xs = sorted(set(round(a['x0']) for a in anchors))
col_xs = [raw_xs[0]]
for x in raw_xs[1:]:
    if x - col_xs[-1] > 15:
        col_xs.append(x)

def col_range(i):
    lo = col_xs[i] - 15
    hi = (col_xs[i + 1] - 15) if i + 1 < len(col_xs) else page.rect.width
    return lo, hi

def col_of(x0):
    best, bd = 0, 1e9
    for i, c in enumerate(col_xs):
        d = abs(x0 - c)
        if d < bd:
            bd, best = d, i
    return best

col_anchors = defaultdict(list)
for w in sorted(anchors, key=lambda w: (col_of(w['x0']), w['top'])):
    col_anchors[col_of(w['x0'])].append(w)

fitz_img_infos = page.get_image_info(xrefs=True)

test_dir = r"d:\projects\supplier_crawler\scripts\temp\test_images"
os.makedirs(test_dir, exist_ok=True)

for col, alist in col_anchors.items():
    lo, hi = col_range(col)
    for idx, a in enumerate(alist):
        top = a['top']
        prev_top = alist[idx - 1]['top'] if idx > 0 else 0
        
        # 获取 SKU
        band = [w for w in words if lo - 2 <= w['x0'] and w['x1'] <= hi + 2 and top - 4 <= w['top'] < (alist[idx+1]['top'] if idx+1 < len(alist) else page.rect.height)]
        band.sort(key=lambda w: (w['top'], w['x0']))
        band_text = ' '.join(w['text'] for w in band)
        m = re.search(r'SKU:\s*([A-Za-z0-9][A-Za-z0-9\-]{2,})', band_text)
        code = m.group(1) if m else "UNKNOWN"
        
        # 匹配图片
        best_xref, best_d = None, 1e9
        cell_mid_x = (lo + hi) / 2
        cell_mid_y = (prev_top + top) / 2
        for info in fitz_img_infos:
            bbox = info.get('bbox')
            if not bbox or info.get('width', 0) < 60 or info.get('height', 0) < 60:
                continue
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            if (lo - 15 <= cx <= hi + 15) and (prev_top - 5 <= cy <= top + 10):
                d = (cx - cell_mid_x)**2 + (cy - cell_mid_y)**2
                if d < best_d:
                    best_d = d
                    best_xref = info.get('xref')
        
        if best_xref:
            base_im = doc.extract_image(best_xref)
            im_obj = Image.open(io.BytesIO(base_im['image']))
            out_fp = os.path.join(test_dir, f"{code}.jpg")
            im_obj.convert('RGB').save(out_fp, 'JPEG', quality=85)
            print(f"Col {col} Row {idx}: SKU={code:10s} -> Extracted xref {best_xref}, size {im_obj.size}, saved to {code}.jpg")
        else:
            print(f"Col {col} Row {idx}: SKU={code:10s} -> NO IMAGE FOUND")
