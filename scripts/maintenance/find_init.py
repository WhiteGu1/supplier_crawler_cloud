# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('database/db_manager.py', encoding='utf-8') as f:
    text = f.read()

idx = text.find('init_')
if idx != -1:
    print(text[idx:idx+1500])
else:
    idx2 = text.find('create table')
    if idx2 != -1:
        print(text[idx2:idx2+1500])
