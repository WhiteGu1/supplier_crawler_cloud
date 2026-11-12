# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/dashboard.html', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'viewProduct(' in l:
        print(f"Line {i+1}: {l.strip()[:100]}")
