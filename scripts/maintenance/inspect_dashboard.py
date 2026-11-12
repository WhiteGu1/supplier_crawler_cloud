# -*- coding: utf-8 -*-
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/dashboard.html', encoding='utf-8') as f:
    text = f.read()

print('Length of dashboard.html:', len(text))

# Search for navigation items
nav_matches = re.findall(r'<nav.*?</nav>', text, re.DOTALL)
if nav_matches:
    print("=== NAV ===")
    print(nav_matches[0])

# Search for menu / tabs
menu_items = re.findall(r'<button[^>]*onclick="[^"]*"[^>]*>.*?</button>', text)
for b in menu_items[:20]:
    if any(k in b for k in ['switch', 'tab', 'page', 'show', 'fav', '收藏', 'Cart', 'cart']):
        print("Menu button:", b)

# Search for favorite-related functions or endpoints
print("\n=== JS Functions for favorites or products ===")
funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\([^)]*\)', text)
for fn in funcs:
    if any(k in fn.lower() for k in ['fav', 'product', 'cart', 'order', 'render', 'modal', 'price']):
        print("Function:", fn)

# Check how favorites work in JS
fav_js = [line for line in text.split('\n') if 'favorite' in line.lower() or '收藏' in line]
print(f"\nFavorites lines count: {len(fav_js)}")
for l in fav_js[:10]:
    print("  ", l.strip()[:100])
