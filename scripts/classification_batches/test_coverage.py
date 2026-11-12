# -*- coding: utf-8 -*-
import sys
import json
import pymysql
import re

sys.path.insert(0, r'C:\Users\Administrator\.gemini\antigravity\brain\62eb0323-a421-4a0e-89c8-9cfd1433dbec\scratch')
sys.stdout.reconfigure(encoding='utf-8')
from test_rule_engine_v2 import classify_item as classify_product, STD_SET

conn = pymysql.connect(
    host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute('''
    SELECT p.id, p.supplier_id, s.name as sup_name, p.name, p.category, p.sku
    FROM products p
    JOIN suppliers s ON s.id = p.supplier_id
    WHERE s.is_active = 1 AND p.is_available = 1 AND p.is_missing = 0
''')
rows = cur.fetchall()
conn.close()

unclassified = []
for r in rows:
    cat = (r['category'] or '').strip()
    if not cat or not re.search(r'[\u4e00-\u9fff]', cat):
        unclassified.append(r)

print(f'Total unclassified: {len(unclassified)}')

results = {}
empty_matches = []
fallback_matches = []

for p in unclassified:
    cats = classify_product(p['name'], p['category'])
    if not cats:
        empty_matches.append(p)
    elif cats == ['家居生活 > 日用杂货 > 其他杂货']:
        fallback_matches.append(p)
    else:
        results[p['id']] = cats

print(f'Matched specific categories: {len(results)}')
print(f'Empty matches: {len(empty_matches)}')
print(f'Fallback matches (其他杂货): {len(fallback_matches)}')

if fallback_matches:
    print('\nSample 30 Fallback matches:')
    for p in fallback_matches[:30]:
        print(f"  [{p['sup_name']}] [raw: {p['category']}] {p['name']}")
