# -*- coding: utf-8 -*-
import requests, sys
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')
url = 'https://catalog.smartycart.com.ar/token/f1586b2aeb8fd7dbfe2630383b59f8a5613e5f4c?keyword=360356'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(r.text, 'html.parser')
btn = soup.select_one('.addQuantityToCart, button[data-product-id]')
print('Button attrs:', btn.attrs if btn else 'No button')
inputs = soup.select('div.item input')
for inp in inputs:
    print('Input:', inp.attrs)
