# -*- coding: utf-8 -*-
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = r"d:\projects\supplier_crawler"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.db_manager import DatabaseManager

db = DatabaseManager(
    host="localhost",
    port=3306,
    user="root",
    password="admin123",
    database="supplier_crawler"
)

# 清空测试
db.clear_cart()
print("Cart cleared, stats:", db.get_cart_stats())

# 测试按 product_id 添加
db.add_to_cart(38892, 2, "add") # DA-01
print("Added DA-01 (qty:2), stats:", db.get_cart_stats())
db.add_to_cart(38892, 3, "add") # 累加
print("Added DA-01 (qty:3), items:", db.get_cart_items())

# 测试批量添加 (按 SKU)
batch_res = db.batch_add_to_cart([
    {"sku": "C02109OR", "quantity": 4},
    {"sku": "DA-390", "quantity": 12}
])
print("Batch add result:", batch_res)

# 查看购物车详情
items = db.get_cart_items()
print(f"Total items in cart: {len(items)}")
for it in items:
    print(f"  [{it['sku']}] x {it['quantity']} | Price:${it['price']} | Name:{it['name'][:30]}")

# 测试更新数量
db.update_cart_quantity(38892, 10)
print("Updated DA-01 to 10")

# 清空
db.clear_cart()
print("Cleaned up cart for fresh use, stats:", db.get_cart_stats())
