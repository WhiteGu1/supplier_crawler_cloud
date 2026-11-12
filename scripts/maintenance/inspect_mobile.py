# -*- coding: utf-8 -*-
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/mobile.html', encoding='utf-8') as f:
    text = f.read()

print('Length of mobile.html:', len(text))
nav_matches = re.findall(r'<nav.*?</nav>', text, re.DOTALL)
if nav_matches:
    print("=== NAV ===")
    print(nav_matches[0])

funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\([^)]*\)', text)
print("Functions in mobile.html:", funcs)
