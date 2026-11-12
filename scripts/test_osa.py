# -*- coding: utf-8 -*-
import requests, re, sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

urls = [
    'https://www.osadistribuidora.com.ar/productos/plato-fenix-durax/',
    'https://www.osadistribuidora.com.ar/productos/cubiertos-new-kolor-negro/',
    'https://www.osadistribuidora.com.ar/productos/copa-windsord-nadir/'
]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for u in urls:
    r = requests.get(u, headers=headers, timeout=10)
    print(f'URL: {u} | Status: {r.status_code}')
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Check form
    forms = soup.select('form[action*="comprar"]')
    print(f'  Comprar forms found: {len(forms)}')
    for f in forms:
        inputs = f.select('input')
        print('    Inputs:', [(inp.get('name'), inp.get('value'), inp.get('min'), inp.get('step')) for inp in inputs])
    
    # Check description
    desc_el = soup.select_one('.user-content, .js-product-description, #product-description')
    if desc_el:
        desc_text = desc_el.get_text('\n', strip=True)
        print('    Desc text preview:\n', desc_text[:400])
        # Look for bulto
        m_bulto = re.findall(r'(?:unidades\s*por\s*bulto|bulto\s*cerrado|bulto|pack|caja)[\s:]*(\d+)?', desc_text, re.I)
        print('    Bulto regex matches:', m_bulto)
    print('---')
