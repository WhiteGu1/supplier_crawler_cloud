# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/dashboard.html', encoding='utf-8') as f:
    text = f.read()

import re
modals = re.findall(r'<div class="modal-overlay"[^>]*id="([^"]*)"', text)
print("Modals found:", modals)
for m in modals:
    idx = text.find(f'id="{m}"')
    print(f"\nModal: {m}")
    print(text[idx:idx+300])
