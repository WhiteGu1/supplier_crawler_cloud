# -*- coding: utf-8 -*-
import sys
import pymysql
import re

sys.path.insert(0, r'C:\Users\Administrator\.gemini\antigravity\brain\62eb0323-a421-4a0e-89c8-9cfd1433dbec\scratch')
sys.stdout.reconfigure(encoding='utf-8')
from test_rule_engine import classify_product

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

fallbacks = []
for p in rows:
    cat = (p['category'] or '').strip()
    if not cat or not re.search(r'[\u4e00-\u9fff]', cat):
        c = classify_product(p['name'], p['category'])
        if c == ['家居生活 > 日用杂货 > 其他杂货']:
            fallbacks.append(p)

print(f'Total fallbacks: {len(fallbacks)}')

by_rc = {}
for p in fallbacks:
    by_rc.setdefault(p['category'] or '(empty)', []).append(p)

for rc, items in sorted(by_rc.items(), key=lambda x: -len(x[1])):
    print(f'=== Raw Cat: "{rc}" ({len(items)} items) ===')
    for item in items[:10]:
        print(f'   - [{item["id"]}] {item["name"]}')
