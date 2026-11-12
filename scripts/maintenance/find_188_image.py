# -*- coding: utf-8 -*-
import fitz
import os

dl = r"C:\Users\Administrator\Downloads"
for fn in os.listdir(dl):
    if fn.endswith('.pdf'):
        fp = os.path.join(dl, fn)
        try:
            doc = fitz.open(fp)
            for p in range(len(doc)):
                page = doc[p]
                for info in page.get_image_info(xrefs=True):
                    if info['width'] == 188 and info['height'] == 188:
                        print(f"Match 188x188 in {fn} page {p+1}, xref={info['xref']}, bbox={info['bbox']}")
                        # 打印此页文本
                        print("Page text snippet:")
                        print(page.get_text()[:300])
                        print("-" * 50)
                        break
        except Exception:
            pass
