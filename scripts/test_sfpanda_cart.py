# -*- coding: utf-8 -*-
import requests, sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')
s = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
}
r1 = s.get('https://sfpanda.com.ar/productos', headers=headers)
print('Get /productos status:', r1.status_code, 'Cookies:', s.cookies.get_dict())
soup = BeautifulSoup(r1.text, 'html.parser')
card = soup.select_one('article.product-block[data-product-id]')
if card:
    pid = card.get('data-product-id')
    form = card.select_one('form')
    action = form.get('action') if form else f'/cart/add/{pid}'
    print('Target pid:', pid, 'action:', action)
    
    post_headers = {
        'User-Agent': headers['User-Agent'],
        'Referer': 'https://sfpanda.com.ar/productos',
        'Origin': 'https://sfpanda.com.ar',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    }
    r2 = s.post('https://sfpanda.com.ar' + action, data={'qty': '2'}, headers=post_headers)
    print('Add to cart status:', r2.status_code)
    print('Add response headers:', r2.headers.get('content-type'))
    print('Add response body preview:\n', r2.text[:400])
    
    # Check cart
    r3 = s.get('https://sfpanda.com.ar/cart', headers=headers)
    print('Cart page status:', r3.status_code, 'Found pid in cart:', pid in r3.text)
