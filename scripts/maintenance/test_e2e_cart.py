# -*- coding: utf-8 -*-
import sys
import urllib.request
import json

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8100"

def request_json(url, data=None, method="GET"):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8') if data else None,
        headers={'Content-Type': 'application/json'} if data else {},
        method=method
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

# 1. 清空购物车
res = request_json(f"{BASE_URL}/api/cart", method="DELETE")
print("1. Clear cart:", res)

# 2. 批量添加测试 (使用用户先前提供的清单片段)
batch_text = """
C02109OR     4
C04539LI     12
DA-390      12
"""
res = request_json(f"{BASE_URL}/api/cart/batch", data={"text": batch_text}, method="POST")
print("2. Batch add:", res)

# 3. 获取购物车详情
cart = request_json(f"{BASE_URL}/api/cart")
print("3. Cart items count:", len(cart["items"]))
print("   Distinct count:", cart["distinct_count"])
print("   Total quantity:", cart["total_quantity"])
print(f"   Total Base Price: ${cart['total_base_price']:,.2f}")
print(f"   Total Adjusted Price (with 10.5% tax): ${cart['total_adjusted_price']:,.2f}")

for item in cart["items"]:
    print(f"   - [{item['sku']}] {item['name'][:25]} x {item['quantity']} | Base: ${item['price']} | Adj: ${item['adjusted_price']} | Subtotal: ${item['adj_subtotal']}")

# 4. 单件添加/修改测试
p_id = cart["items"][0]["product_id"]
res = request_json(f"{BASE_URL}/api/cart/{p_id}", data={"quantity": 20}, method="PUT")
print(f"4. Updated product {p_id} quantity to 20:", res)

# 5. 验证更新后总价
cart_updated = request_json(f"{BASE_URL}/api/cart")
print("5. After update total quantity:", cart_updated["total_quantity"])
print(f"   Updated Total Adjusted Price: ${cart_updated['total_adjusted_price']:,.2f}")

# 6. 测试导出 Excel
excel_url = f"{BASE_URL}/api/cart/export-xlsx"
req = urllib.request.Request(excel_url)
with urllib.request.urlopen(req) as resp:
    content = resp.read()
    print("6. Cart Excel export size:", len(content), "bytes", "Content-Type:", resp.headers.get("Content-Type"))

# 7. 清理
request_json(f"{BASE_URL}/api/cart", method="DELETE")
print("7. Test cleaned up successfully!")
