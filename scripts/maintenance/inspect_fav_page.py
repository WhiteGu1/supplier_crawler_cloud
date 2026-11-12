# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/dashboard.html', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="page-favorites"')
if idx != -1:
    print(text[idx-50:idx+1500])
