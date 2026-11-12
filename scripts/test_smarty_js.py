# -*- coding: utf-8 -*-
import requests, re, sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://catalog.smartycart.com.ar/token/f1586b2aeb8fd7dbfe2630383b59f8a5613e5f4c'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(r.text, 'html.parser')

scripts = soup.select('script[src]')
print('Script tags count:', len(scripts))
for s in scripts:
    src = s.get('src')
    if 'cart' in src or 'catalog' in src or 'app' in src or 'main' in src:
        print('Checking JS:', src)
        try:
            full_src = src if src.startswith('http') else 'https://catalog.smartycart.com.ar' + src
            t = requests.get(full_src, timeout=10).text
            matches = re.findall(r'.{0,50}(?:add_item|quantity_data|Carts/).{0,50}', t)
            for m in matches[:5]:
                print('  Match:', m.strip())
        except Exception as e:
            print('  Err:', e)
