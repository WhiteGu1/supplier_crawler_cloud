# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests, base64, json, os

img_path = r'D:\projects\supplier_crawler\images\Diego\1515ad414407f17c103b747ece1748cd.jpg'
with open(img_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

resp = requests.post(
    'http://127.0.0.1:19002/v1/chat/completions',
    json={
        'model': 'pool-minimax-m3',
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': '这张图里是什么商品？用中文简要回答。'},
                {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}}
            ]
        }],
        'max_tokens': 200
    },
    timeout=120
)
print(f"Status: {resp.status_code}")
print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
