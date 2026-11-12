# -*- coding: utf-8 -*-
import sys, requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

cookies = {'PHPSESSID': '5pk36qcku3uph1f9lggbq6mlft'}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

res = requests.get('https://distrinimay.com.ar/cat/', headers=headers, cookies=cookies, timeout=10)
print('Status:', res.status_code, 'Final URL:', res.url)
soup = BeautifulSoup(res.text, 'html.parser')
cards = soup.select('div.divprod, div.divprodnuevos, div.divprodofer')
print('Cards count:', len(cards))
if cards:
    for c in cards[:3]:
        print('--- CARD ---')
        print(c.prettify()[:600])
else:
    print('First 500 chars of body:', soup.get_text()[:500])
