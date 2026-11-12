# -*- coding: utf-8 -*-
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

for path in ['/', '/mobile']:
    resp = urllib.request.urlopen('http://localhost:8100' + path)
    html = resp.read().decode('utf-8')
    print(f"{path}: status {resp.status}, length {len(html)} bytes, has 'cart': {'page-cart' in html}")
