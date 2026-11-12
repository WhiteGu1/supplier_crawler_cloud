# -*- coding: utf-8 -*-
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('api/main.py', encoding='utf-8') as f:
    main_text = f.read()

fav_endpoints = []
for line in main_text.split('\n'):
    if 'favorite' in line.lower():
        fav_endpoints.append(line)

print("Favorites in api/main.py:")
for l in fav_endpoints:
    print("  ", l)

# Find favorite section in main.py
idx = main_text.find('/api/favorites')
if idx != -1:
    print("\n=== Endpoint block in main.py ===")
    print(main_text[idx-50:idx+1500])

with open('database/db_manager.py', encoding='utf-8') as f:
    db_text = f.read()

print("\n=== Favorites in db_manager.py ===")
for m in re.finditer(r'def\s+[a-zA-Z0-9_]*fav[a-zA-Z0-9_]*', db_text, re.I):
    st = m.start()
    print(db_text[st:st+400])
    print('='*40)
