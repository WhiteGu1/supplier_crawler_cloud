# -*- coding: utf-8 -*-
import requests, sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')
r = requests.get('https://sfpanda.com.ar/producto/cama-de-mascotas-c-u', headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(r.text, 'html.parser')
form = soup.select_one('form[action*="cart"]')
if form:
    print('Form action:', form.get('action'))
    print('Form inputs:', [(i.get('name'), i.get('value'), i.get('type')) for i in form.select('input')])
    print('Form buttons:', [(b.get('name'), b.get('value'), b.get('type'), b.get_text(strip=True)) for b in form.select('button')])
else:
    print('No form found')
    # search for /cart/ in html
    import re
    print('Cart links:', re.findall(r'href=[\'"][^\'"]*cart[^\'"]*[\'"]', r.text))
