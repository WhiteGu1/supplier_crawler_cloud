# Modify api/main.py to add sort/price params to list_products
filepath = 'D:/projects/supplier_crawler/api/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add sort/min_price/max_price params to list_products
old_api = (
    '@app.get("/api/products")\n'
    'async def list_products(\n'
    '    supplier_id: Optional[int] = None,\n'
    '    category: Optional[str] = None,\n'
    '    category_prefix: Optional[str] = None,\n'
    '    keyword: Optional[str] = None,\n'
    '    page: int = 1,\n'
    '    page_size: int = 20,\n'
    '):'
)
new_api = (
    '@app.get("/api/products")\n'
    'async def list_products(\n'
    '    supplier_id: Optional[int] = None,\n'
    '    category: Optional[str] = None,\n'
    '    category_prefix: Optional[str] = None,\n'
    '    keyword: Optional[str] = None,\n'
    '    page: int = 1,\n'
    '    page_size: int = 20,\n'
    '    sort: Optional[str] = None,\n'
    '    min_price: Optional[float] = None,\n'
    '    max_price: Optional[float] = None,\n'
    '):'
)
assert old_api in content, "Could not find old API signature"
content = content.replace(old_api, new_api)

# Add sort/min_price/max_price to db.get_products call
old_call = (
    '    return db.get_products(\n'
    '        supplier_id=supplier_id,\n'
    '        category=cat,\n'
    '        category_prefix=cat_prefix,\n'
    '        no_category=(cat == \'__none__\'),\n'
    '        keyword=keyword, page=page, page_size=page_size,\n'
    '    )'
)
new_call = (
    '    return db.get_products(\n'
    '        supplier_id=supplier_id,\n'
    '        category=cat,\n'
    '        category_prefix=cat_prefix,\n'
    '        no_category=(cat == \'__none__\'),\n'
    '        keyword=keyword, page=page, page_size=page_size,\n'
    '        sort=sort, min_price=min_price, max_price=max_price,\n'
    '    )'
)
assert old_call in content, "Could not find old db call"
content = content.replace(old_call, new_call)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("api/main.py updated successfully")
