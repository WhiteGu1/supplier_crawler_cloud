# -*- coding: utf-8 -*-
import sys
import json
import re
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/classification_batches/standard_categories.json', 'r', encoding='utf-8') as f:
    STD_SET = set(json.load(f))

conn = pymysql.connect(
    host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

# 1. 活跃商品分类检查
cur.execute("""
    SELECT p.id, p.supplier_id, s.name as sup_name, p.category
    FROM products p
    JOIN suppliers s ON s.id = p.supplier_id
    WHERE s.is_active = 1 AND p.is_available = 1 AND p.is_missing = 0
""")
active_rows = cur.fetchall()

non_chinese_active = []
non_std_active = []
for r in active_rows:
    c = (r['category'] or '').strip()
    if not c or not re.search(r'[\u4e00-\u9fff]', c):
        non_chinese_active.append(r)
    if c not in STD_SET:
        non_std_active.append(r)

print("=================================================================")
print(" 活跃在售商品分类与多路径覆盖核验报告")
print("=================================================================")
print(f"活跃商品总数: {len(active_rows)}")
print(f"非中文/空分类活跃商品: {len(non_chinese_active)}")
print(f"非标准库路径活跃商品: {len(non_std_active)}")

# 2. product_categories 覆盖度检查
cur.execute("""
    SELECT count(distinct p.id) as missing_pc_count
    FROM products p
    JOIN suppliers s ON s.id = p.supplier_id
    LEFT JOIN product_categories pc ON pc.product_id = p.id
    WHERE s.is_active = 1 AND p.is_available = 1 AND p.is_missing = 0 AND pc.product_id IS NULL
""")
missing_pc = cur.fetchone()['missing_pc_count']
print(f"缺少 product_categories 映射的活跃商品数: {missing_pc}")

# 3. 供应商逐个统计
cur.execute("""
    SELECT s.id, s.name,
           count(distinct p.id) as active_count,
           count(distinct pc.product_id) as pc_covered,
           count(pc.category) as total_pc_links
    FROM suppliers s
    JOIN products p ON p.supplier_id = s.id
    LEFT JOIN product_categories pc ON pc.product_id = p.id
    WHERE s.is_active = 1 AND p.is_available = 1 AND p.is_missing = 0
    GROUP BY s.id, s.name
    ORDER BY s.id
""")
print("\n=== 各供应商分类及多路径覆盖明细 ===")
for r in cur.fetchall():
    cov_pct = r['pc_covered'] * 100.0 / r['active_count'] if r['active_count'] else 0
    print(f"ID {r['id']:2d} | {r['name']:20s} | 活跃商品: {r['active_count']:5d} | 已归类: {r['pc_covered']:5d} ({cov_pct:6.2f}%) | 分类路径数: {r['total_pc_links']:5d}")

conn.close()
