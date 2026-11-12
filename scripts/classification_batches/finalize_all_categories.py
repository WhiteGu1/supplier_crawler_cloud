# -*- coding: utf-8 -*-
import sys
import json
import pymysql
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'scripts/classification_batches')
from apply_standard_categories import classify_product, STD_SET

conn = pymysql.connect(
    host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)
cur_write = conn.cursor()

cur.execute("SELECT p.id, p.name, p.category, p.brand FROM products p")
rows = cur.fetchall()

non_cjk = [r for r in rows if not (r['category'] or '').strip() or not re.search(r'[\u4e00-\u9fff]', r['category'])]
print(f"Updating {len(non_cjk)} remaining products...")

for p in non_cjk:
    pid = p['id']
    cur.execute("SELECT category FROM product_categories WHERE product_id = %s", (pid,))
    pc_rows = [r['category'] for r in cur.fetchall() if r['category'] in STD_SET]
    if pc_rows:
        target_cat = pc_rows[0]
    else:
        cats = classify_product(p['name'], p['category'], p['brand'])
        target_cat = cats[0] if cats else '家居生活 > 日用杂货 > 其他杂货'
        for c in (cats or [target_cat]):
            cur_write.execute(
                "INSERT IGNORE INTO product_categories (product_id, category) VALUES (%s, %s)",
                (pid, c)
            )

    cur_write.execute(
        "UPDATE products SET category = %s, updated_at = updated_at WHERE id = %s",
        (target_cat, pid)
    )

conn.commit()

# 全表彻底核验
cur.execute("SELECT category FROM products")
all_cats = cur.fetchall()
non_cjk_cnt = sum(1 for r in all_cats if not re.search(r'[\u4e00-\u9fff]', (r['category'] or '')))
non_std_cnt = sum(1 for r in all_cats if (r['category'] or '').strip() not in STD_SET)

print(f"全库 53,584 件商品中:")
print(f"  - 非中文商品数: {non_cjk_cnt}")
print(f"  - 非标准路径商品数: {non_std_cnt}")

conn.close()
