# -*- coding: utf-8 -*-
import sys
import re
import pymysql

sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute('SELECT id, sku, name, price, category FROM products WHERE supplier_id = 16')
gaston = cur.fetchall()

keywords = [
    'percha', 'cepillo', 'escoba', 'pala', 'guante', 'paño', 'trapo', 'microfibra', 'mopa',
    'toalla', 'repasador', 'organizador', 'canasto', 'cesto', 'jabonera', 'vaso', 'jarro',
    'jarrito', 'taza', 'hermetico', 'contenedor', 'tupper', 'vianda', 'bowl', 'rociador',
    'pulverizador', 'esponja', 'fibra', 'embudo', 'colador', 'vertedor', 'molde', 'salero',
    'pimentero', 'salsero', 'gancho', 'tapon', 'mamadera'
]

for kw in keywords:
    matches = [g for g in gaston if kw in g['name'].lower()]
    if matches:
        print(f"=== KEYWORD: {kw} ({len(matches)} items) ===")
        for m in matches:
            print(f"   [{m['id']}] {m['sku']}: {m['name']} (${float(m['price']):.2f})")

conn.close()
