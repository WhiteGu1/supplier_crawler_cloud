# Modify db_manager.py to add sort and price filter support
import os

filepath = 'D:/projects/supplier_crawler/database/db_manager.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Change function signature
old_sig = "    def get_products(self, supplier_id=None, category=None, category_prefix=None,\n                     no_category=False, keyword=None, page=1, page_size=20) -> dict:"
new_sig = "    def get_products(self, supplier_id=None, category=None, category_prefix=None,\n                     no_category=False, keyword=None, page=1, page_size=20,\n                     sort=None, min_price=None, max_price=None) -> dict:"
assert old_sig in content, "Could not find old signature"
content = content.replace(old_sig, new_sig)

# 2. Add price filter after keyword condition
old_kw = '        if keyword:        conditions.append("p.name LIKE %s");   params.append(f"%{keyword}%")\n        where ='
new_kw = (
    '        if keyword:        conditions.append("p.name LIKE %s");   params.append(f"%{keyword}%")\n'
    '        if min_price is not None:\n'
    '            conditions.append("p.price * (1 + IFNULL(s.price_adjustment,0)/100) >= %s"); params.append(float(min_price))\n'
    '        if max_price is not None:\n'
    '            conditions.append("p.price * (1 + IFNULL(s.price_adjustment,0)/100) <= %s"); params.append(float(max_price))\n'
    '        where ='
)
assert old_kw in content, "Could not find keyword line"
content = content.replace(old_kw, new_kw)

# 3. Add order_clause and fix COUNT query
old_block = (
    '        where = "WHERE " + " AND ".join(conditions)\n'
    '        offset = (page - 1) * page_size\n'
    '        with self.connection() as conn:\n'
    '            cursor = conn.cursor(dictionary=True)\n'
    '            cursor.execute(f"SELECT COUNT(*) as total FROM products p {where}", params)'
)
new_block = (
    '        where = "WHERE " + " AND ".join(conditions)\n'
    '        offset = (page - 1) * page_size\n'
    '\n'
    '        # sort: price_asc / price_desc / name_asc / name_desc / default updated_at DESC\n'
    '        order_clause = "ORDER BY p.updated_at DESC"\n'
    '        if sort == \'price_asc\':\n'
    '            order_clause = "ORDER BY p.price * (1 + IFNULL(s.price_adjustment,0)/100) ASC"\n'
    '        elif sort == \'price_desc\':\n'
    '            order_clause = "ORDER BY p.price * (1 + IFNULL(s.price_adjustment,0)/100) DESC"\n'
    '        elif sort == \'name_asc\':\n'
    '            order_clause = "ORDER BY p.name ASC"\n'
    '        elif sort == \'name_desc\':\n'
    '            order_clause = "ORDER BY p.name DESC"\n'
    '\n'
    '        with self.connection() as conn:\n'
    '            cursor = conn.cursor(dictionary=True)\n'
    '            cursor.execute(f"SELECT COUNT(*) as total FROM products p JOIN suppliers s ON p.supplier_id=s.id {where}", params)'
)
assert old_block in content, "Could not find old block"
content = content.replace(old_block, new_block)

# 4. Change ORDER BY in SELECT query
old_order = '{where} ORDER BY p.updated_at DESC LIMIT %s OFFSET %s""",'
new_order = '{where} {order_clause} LIMIT %s OFFSET %s""",'
assert old_order in content, "Could not find old order"
content = content.replace(old_order, new_order)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("db_manager.py updated successfully")
