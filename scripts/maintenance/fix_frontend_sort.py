# Modify frontend/dashboard.html to add sort dropdown and backend price filter
filepath = 'D:/projects/supplier_crawler/frontend/dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add sort dropdown after max price input
old_filter = (
    '      <input type="number" class="filter-input" placeholder="最低价" id="filter-min" style="width:90px" oninput="debounceFilter()">\n'
    '      <input type="number" class="filter-input" placeholder="最高价" id="filter-max" style="width:90px" oninput="debounceFilter()">\n'
    '    </div>'
)
new_filter = (
    '      <input type="number" class="filter-input" placeholder="最低价" id="filter-min" style="width:90px" oninput="debounceFilter()">\n'
    '      <input type="number" class="filter-input" placeholder="最高价" id="filter-max" style="width:90px" oninput="debounceFilter()">\n'
    '      <select class="filter-input" id="filter-sort" onchange="loadProducts()" style="width:120px"><option value="">默认排序</option><option value="price_asc">价格 ↑</option><option value="price_desc">价格 ↓</option><option value="name_asc">名称 A-Z</option><option value="name_desc">名称 Z-A</option></select>\n'
    '    </div>'
)
assert old_filter in content, "Could not find old filter area"
content = content.replace(old_filter, new_filter)

# 2. Modify loadProducts() to use backend sort and price filter
# Replace the URL building section
old_url = (
    "  let url = '/api/products?page=' + currentPage + '&page_size=' + PAGE_SIZE;\n"
    "  if (kw)  url += '&keyword=' + encodeURIComponent(kw);\n"
    "  if (sup) url += '&supplier_id=' + sup;\n"
    "  var catVal = catSub || catMain;\n"
    "  if (catVal === '__none__') {\n"
    "    url += '&category=__none__';\n"
    "  } else if (catVal) {\n"
    "    url += '&category=' + encodeURIComponent(catVal);\n"
    "  }"
)
new_url = (
    "  let url = '/api/products?page=' + currentPage + '&page_size=' + PAGE_SIZE;\n"
    "  if (kw)  url += '&keyword=' + encodeURIComponent(kw);\n"
    "  if (sup) url += '&supplier_id=' + sup;\n"
    "  var catVal = catSub || catMain;\n"
    "  if (catVal === '__none__') {\n"
    "    url += '&category=__none__';\n"
    "  } else if (catVal) {\n"
    "    url += '&category=' + encodeURIComponent(catVal);\n"
    "  }\n"
    "  if (min) url += '&min_price=' + encodeURIComponent(min);\n"
    "  if (max) url += '&max_price=' + encodeURIComponent(max);\n"
    "  var sortVal = document.getElementById('filter-sort').value;\n"
    "  if (sortVal) url += '&sort=' + encodeURIComponent(sortVal);"
)
assert old_url in content, "Could not find old URL building"
content = content.replace(old_url, new_url)

# 3. Remove client-side price filtering (since backend does it now)
old_client_filter = (
    "    // Filter by price client side (backend doesn't have price filter)\n"
    "    const minP = parseFloat(min) || 0;\n"
    "    const maxP = parseFloat(max) || Infinity;\n"
    "    const filtered = rows.filter(function(p) { return parseFloat(p.price) >= minP && parseFloat(p.price) <= maxP; });"
)
new_client_filter = (
    "    // Price filtering now done on backend\n"
    "    const filtered = rows;"
)
assert old_client_filter in content, "Could not find old client filter"
content = content.replace(old_client_filter, new_client_filter)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("dashboard.html updated successfully")
