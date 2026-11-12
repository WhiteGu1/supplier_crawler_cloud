# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/dashboard.html', encoding='utf-8') as f:
    text = f.read()

# 查找 CSS 根变量
idx = text.find(':root')
if idx != -1:
    print("=== CSS ROOT ===")
    print(text[idx:idx+800])

# 查找 modal 相关的 CSS
modal_css = [line for line in text.split('\n') if '.modal' in line]
print("\n=== Modal CSS classes ===")
for m in modal_css[:10]:
    print("  ", m.strip())
