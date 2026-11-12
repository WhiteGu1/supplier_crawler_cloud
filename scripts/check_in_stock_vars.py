import urllib.request, json

vids = [55483, 14566, 55394, 21235, 164439, 164437, 55342, 55568, 42111, 59885, 59886]
for vid in vids:
    req = urllib.request.Request(f'https://bellacentral.com.ar/wp-json/wc/store/v1/products/{vid}', headers={'User-Agent': 'Mozilla/5.0'})
    v = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    print(f"ID {vid}: name={v.get('name')[:30]} | attrs={v.get('attributes')} | price={v.get('prices',{}).get('price')}")
