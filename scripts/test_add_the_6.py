import urllib.request, json

cart_req = urllib.request.Request('https://bellacentral.com.ar/wp-json/wc/store/v1/cart', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(cart_req) as resp:
    nonce = resp.headers.get('Nonce')

# 14509: 14566 (caja 24u) -> qty 1
# 21183: 21235 (caja 48u or 55394 6u * 6) -> 55394 qty 6
# 164435: 164437 (caja 36u) -> qty 1
# 13260: 55342 (caja 28u) -> qty 1
# 42108: 42111 (caja 24u) -> qty 1
# 59882: 59886 (caja 24u) -> qty 1

candidates = [
    {'id': 14566, 'qty': 1, 'name': 'LABIAL LIP GLOSS BARBY (caja 24u)'},
    {'id': 55394, 'qty': 6, 'name': 'GLOSS DE ALOE VERA (pack 6u x 6 = 36u)'},
    {'id': 164437, 'qty': 1, 'name': 'MASCARA 2 EN 1 4ANGEL (caja 36u)'},
    {'id': 55342, 'qty': 1, 'name': 'LABIAL MISS BETTY (caja 28u)'},
    {'id': 42111, 'qty': 1, 'name': 'ILUMINADOR EN CREMA (caja 24u)'},
    {'id': 59886, 'qty': 1, 'name': 'ILUMINADOR LIQUIDO MISS LARA (caja 24u)'},
]

for c in candidates:
    add_req = urllib.request.Request('https://bellacentral.com.ar/wp-json/wc/store/v1/cart/add-item',
        data=json.dumps({'id': c['id'], 'quantity': c['qty']}).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'Nonce': nonce})
    try:
        res = urllib.request.urlopen(add_req)
        print(f"OK: {c['name']} added! status: {res.status}")
        nonce = res.headers.get('Nonce')
    except Exception as e:
        print(f"FAIL: {c['name']} err:", e)
