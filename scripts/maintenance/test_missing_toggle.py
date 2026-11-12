import requests, sys
sys.stdout.reconfigure(encoding='utf-8')
r1 = requests.get('http://127.0.0.1:8100/api/products', params={'page':1,'page_size':1}, timeout=60)
r2 = requests.get('http://127.0.0.1:8100/api/products', params={'page':1,'page_size':1,'include_missing':'true'}, timeout=60)
d1 = r1.json()
d2 = r2.json()
print(f"不含缺失: {d1['total']}")
print(f"含缺失: {d2['total']}")
