"""清理测试数据"""
import requests
BASE = 'http://localhost:8100'
pid = 34142
# 删除测试添加的分类
for cat in ['美妆个护 > 化妆品 > 化妆包', '箱包皮具 > 箱包配件 > 化妆包', '厨房用品 > 餐具']:
    r = requests.delete(f'{BASE}/api/products/{pid}/categories/{cat}')
    print(f"删除 '{cat}': {r.json()}")

# 验证
r = requests.get(f'{BASE}/api/products/{pid}/categories')
print(f"最终分类: {r.json()}")
