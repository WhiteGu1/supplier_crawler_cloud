"""测试扁平多分类（无主次）"""
import requests

BASE = 'http://localhost:8100'

# 1. 获取一个商品
r = requests.get(f'{BASE}/api/products', params={'page': 1, 'page_size': 1})
pid = r.json()['data'][0]['id']
print(f"测试商品ID: {pid}")

# 2. 获取当前分类
r2 = requests.get(f'{BASE}/api/products/{pid}/categories')
print(f"当前分类: {r2.json()}")

# 3. 添加分类路径1
r3 = requests.post(f'{BASE}/api/products/{pid}/categories', json={'category': '美妆个护 > 化妆品 > 化妆包'})
print(f"添加分类路径1: {r3.json()}")

# 4. 添加分类路径2
r4 = requests.post(f'{BASE}/api/products/{pid}/categories', json={'category': '箱包皮具 > 箱包配件 > 化妆包'})
print(f"添加分类路径2: {r4.json()}")

# 5. 查看所有分类
r5 = requests.get(f'{BASE}/api/products/{pid}/categories')
cats = r5.json()
print(f"所有分类路径({len(cats)}条):")
for c in cats:
    print(f"  {c['category']}")

# 6. 验证没有is_primary字段
if cats and 'is_primary' not in cats[0]:
    print("✓ 无is_primary字段，所有分类并列")
else:
    print("✗ 仍有is_primary字段!")

# 7. 测试筛选：用添加的分类路径筛选
r6 = requests.get(f'{BASE}/api/products', params={'category': '箱包皮具 > 箱包配件', 'page': 1, 'page_size': 3})
data6 = r6.json()
print(f"\n筛选 '箱包皮具 > 箱包配件': {data6['total']}条")
for p in data6['data'][:2]:
    print(f"  {p['id']}: {p['category']}")

# 8. 清理：删除测试分类
for c in cats:
    if c['category'] not in ['厨房用品 > 炊具 > 压泥器'] and '厨房' not in c['category']:
        requests.delete(f'{BASE}/api/products/{pid}/categories/{c["category"]}')
        print(f"已删除测试分类: {c['category']}")

# 9. 恢复
r7 = requests.get(f'{BASE}/api/products/{pid}/categories')
print(f"\n恢复后分类: {r7.json()}")
