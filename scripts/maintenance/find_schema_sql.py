# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('database/db_manager.py', encoding='utf-8') as f:
    text = f.read()

idx = text.find('SCHEMA_SQL')
if idx != -1:
    print(text[idx:idx+2500])
