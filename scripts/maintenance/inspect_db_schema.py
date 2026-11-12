# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('database/db_manager.py', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'CREATE TABLE IF NOT EXISTS [a-zA-Z0-9_]+[^;]+;', text, re.I)
for m in matches:
    print(m)
    print("="*40)
