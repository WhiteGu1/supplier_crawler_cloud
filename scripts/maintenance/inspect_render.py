# -*- coding: utf-8 -*-
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/dashboard.html', encoding='utf-8') as f:
    text = f.read()

# 1. 查找商品卡片渲染函数
for fn in ['renderProductCards', 'renderFavList', 'viewProduct', 'showPage']:
    idx = text.find(f'function {fn}')
    if idx != -1:
        print(f"=== Function {fn} ===")
        print(text[idx:idx+1500])
        print("="*60)
