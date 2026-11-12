# -*- coding: utf-8 -*-
import fitz
import pdfplumber
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"C:\Users\Administrator\Downloads\gaston\CATALOGO_SP_compressed-DZa5fbhjobJkk1dEMLOaNalotdlOFL.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[13] # page 14
    words = page.extract_words(x_tolerance=2, y_tolerance=3)
    img_list = [im for im in page.images if 40 <= im['width'] < 400]
    
    anchors = [w for w in words if w['text'] == 'SKU:']
    raw_xs = sorted(set(round(a['x0']) for a in anchors))
    col_xs = [raw_xs[0]]
    for x in raw_xs[1:]:
        if x - col_xs[-1] > 15:
            col_xs.append(x)
            
    def col_range(i):
        lo = col_xs[i] - 15
        hi = (col_xs[i + 1] - 15) if i + 1 < len(col_xs) else page.width
        return lo, hi

    def col_of(x0):
        best, bd = 0, 1e9
        for i, c in enumerate(col_xs):
            d = abs(x0 - c)
            if d < bd:
                bd, best = d, i
        return best

    from collections import defaultdict
    col_anchors = defaultdict(list)
    for w in sorted(anchors, key=lambda w: (col_of(w['x0']), w['top'])):
        col_anchors[col_of(w['x0'])].append(w)
        
    for col, alist in col_anchors.items():
        lo, hi = col_range(col)
        print(f"\n=== COLUMN {col} (x: {lo:.1f} - {hi:.1f}) ===")
        for idx, a in enumerate(alist):
            prev_top = alist[idx - 1]['top'] if idx > 0 else 0
            curr_top = a['top']
            nxt_top = alist[idx + 1]['top'] if idx + 1 < len(alist) else page.height
            
            # 找到对应 SKU
            sku_w = [w for w in words if w['top'] >= curr_top - 2 and w['top'] <= curr_top + 10 and w['x0'] > a['x1']][:1]
            sku = sku_w[0]['text'] if sku_w else 'Unknown'
            
            # 原逻辑：[curr_top, nxt_top]
            old_mid = (curr_top + nxt_top) / 2
            old_best, old_bd = None, 1e9
            for im in img_list:
                cx = (im['x0'] + im['x1']) / 2
                if lo - 5 <= cx <= hi + 5:
                    d = abs((im['top'] + im['bottom']) / 2 - old_mid)
                    if d < old_bd: old_bd, old_best = d, im
            
            # 新逻辑（正确定位上方图片）：[prev_top, curr_top]
            new_mid = (prev_top + curr_top) / 2
            new_best, new_bd = None, 1e9
            for im in img_list:
                cx = (im['x0'] + im['x1']) / 2
                if lo - 5 <= cx <= hi + 5:
                    cy = (im['top'] + im['bottom']) / 2
                    # 图片应位于文字上方：prev_top <= cy <= curr_top
                    if prev_top <= cy <= curr_top:
                        d = abs(cy - new_mid)
                        if d < new_bd: new_bd, new_best = d, im
            
            print(f"Row {idx} | SKU: {sku:10s} (top={curr_top:.1f}):")
            print(f"   原逻辑选中的图片: top={old_best['top']:.1f}, bottom={old_best['bottom']:.1f} (位于当前文字下方!)")
            if new_best:
                print(f"   新逻辑选中的图片: top={new_best['top']:.1f}, bottom={new_best['bottom']:.1f} (位于当前文字上方 正确!)")
            else:
                print(f"   新逻辑: 未找到匹配图片")
