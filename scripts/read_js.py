# -*- coding: utf-8 -*-
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')
t = requests.get('https://catalog.smartycart.com.ar/js/catalogs.js').text
idx = t.find('quantities.push')
print(t[idx:idx+400])
