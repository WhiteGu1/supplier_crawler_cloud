"""测试多分类和二级筛选修复"""
import requests
import json

# 1. 测试二级分类筛选（之前有bug）
r = requests.get('http://localhost:8100/api/products', params={'category': '厨房用品 > 餐具', 'page': 1, 'page_size': 5})
data = r.json()
print(f"二级分类 '厨房用品 > 餐具' 查询结果: {data['total']}条")
for p in data['data'][:3]:
    print(f"  {p['id']}: {p['category']}")

# 2. 测试一级分类筛选
r2 = requests.get('http://localhost:8100/api/products', params={'category': '厨房用品', 'page': 1, 'page_size': 5})
data2 = r2.json()
print(f"\n一级分类 '厨房用品' 查询结果: {data2['total']}条")

# 3. 测试获取多分类
# 先找一个有多分类关联的商品
r3 = requests.get('http://localhost:8100/api/products', params={'page': 1, 'page_size': 1})
first_id = r3.json()['data'][0]['id']
r4 = requests.get(f'http://localhost:8100/api/products/{first_id}/categories')
data4 = r4.json()
print(f"\n商品{first_id}的多分类: {data4}")

# 4. 测试添加多分类
r5 = requests.post(f'http://localhost:8100/api/products/{first_id}/categories', json={'category': '玩具游戏 > 玩具游戏 > 其他玩具', 'is_primary': False})
print(f"\n添加分类结果: {r5.json()}")

# 5. 再查多分类
r6 = requests.get(f'http://localhost:8100/api/products/{first_id}/categories')
data6 = r6.json()
print(f"添加后多分类: {data6}")

# 6. 测试删除多分类
if len(data6) > 1:
    cat_to_delete = data6[-1]['category']
    r7 = requests.delete(f'http://localhost:8100/api/products/{first_id}/categories/{cat_to_delete}')
    print(f"\n删除分类 '{cat_to_delete}' 结果: {r7.json()}")
    r8 = requests.get(f'http://localhost:8100/api/products/{first_id}/categories')
    print(f"删除后多分类: {r8.json()}")

# 7. 恢复
requests.post(f'http://localhost:8100/api/products/{first_id}/categories', json={'category': '厨房用品 > 餐具', 'is_primary': True})
print("\n已恢复主分类")
