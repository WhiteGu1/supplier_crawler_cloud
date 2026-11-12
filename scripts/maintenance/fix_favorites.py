# Fix favorites: add batch query API + fix frontend refresh
import re

# === 1. DB layer: add get_products_by_ids ===
db_path = 'D:/projects/supplier_crawler/database/db_manager.py'
with open(db_path, 'r', encoding='utf-8') as f:
    db_content = f.read()

# Add get_products_by_ids method after get_favorite_ids
old_get_fav = '    def get_favorite_ids(self) -> list:'
new_method = '''    def get_products_by_ids(self, product_ids: list) -> list:
        """批量按ID获取商品数据（含供应商名）"""
        if not product_ids:
            return []
        with self.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            placeholders = ','.join(['%s'] * len(product_ids))
            cursor.execute(
                f"""SELECT p.*, s.name as supplier_name
                    FROM products p JOIN suppliers s ON p.supplier_id=s.id
                    WHERE p.id IN ({placeholders}) AND p.is_available=1""",
                product_ids
            )
            rows = cursor.fetchall()
        for r in rows:
            for f2 in ("created_at", "updated_at"):
                if isinstance(r.get(f2), datetime):
                    r[f2] = r[f2].strftime("%Y-%m-%d %H:%M:%S")
        return rows

    def get_favorite_ids(self) -> list:'''
assert old_get_fav in db_content, "Could not find get_favorite_ids"
db_content = db_content.replace(old_get_fav, new_method)

with open(db_path, 'w', encoding='utf-8') as f:
    f.write(db_content)
print("db_manager.py: added get_products_by_ids")

# === 2. API layer: add batch query endpoint + product_ids param ===
api_path = 'D:/projects/supplier_crawler/api/main.py'
with open(api_path, 'r', encoding='utf-8') as f:
    api_content = f.read()

# Add product_ids param to list_products
old_list = '    sort: Optional[str] = None,\n    min_price: Optional[float] = None,\n    max_price: Optional[float] = None,\n):'
new_list = '    sort: Optional[str] = None,\n    min_price: Optional[float] = None,\n    max_price: Optional[float] = None,\n    product_ids: Optional[str] = None,\n):'
assert old_list in api_content, "Could not find list_products params"
api_content = api_content.replace(old_list, new_list)

# Add product_ids filtering logic after sort/min/max handling
old_return = '    return db.get_products(\n        supplier_id=supplier_id,\n        category=cat,\n        category_prefix=cat_prefix,\n        no_category=(cat == \'__none__\'),\n        keyword=keyword, page=page, page_size=page_size,\n        sort=sort, min_price=min_price, max_price=max_price,\n    )'
new_return = '''    # 批量按ID查询
    if product_ids:
        ids = [int(x) for x in product_ids.split(',') if x.strip().isdigit()]
        rows = db.get_products_by_ids(ids)
        return {"total": len(rows), "page": 1, "page_size": len(rows), "data": rows}

    return db.get_products(
        supplier_id=supplier_id,
        category=cat,
        category_prefix=cat_prefix,
        no_category=(cat == '__none__'),
        keyword=keyword, page=page, page_size=page_size,
        sort=sort, min_price=min_price, max_price=max_price,
    )'''
assert old_return in api_content, "Could not find db.get_products call"
api_content = api_content.replace(old_return, new_return)

with open(api_path, 'w', encoding='utf-8') as f:
    f.write(api_content)
print("api/main.py: added product_ids batch query")

# === 3. Frontend: fix loadFavorites + toggleFavorite refresh ===
html_path = 'D:/projects/supplier_crawler/frontend/dashboard.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Replace slow loadFavorites with fast batch query
old_load_fav = '''async function loadFavorites() {
  await loadFavIds();
  const ids = [..._favIdSet];
  document.getElementById('fav-count').textContent = ids.length + ' 个商品';

  const content = document.getElementById('fav-content');
  const tabsEl = document.getElementById('fav-supplier-tabs');

  if (!ids.length) {
    tabsEl.innerHTML = '';
    content.innerHTML = '<div class="empty-state"><span class="icon">⭐</span><p>还没有收藏任何商品</p><p style="font-size:12px;color:var(--text3);margin-top:8px">在商品数据库里点击 ☆ 收藏</p></div>';
    return;
  }

  let products = [];
  try {
    const idSet = new Set(ids);
    for (let page = 1; page <= 20; page++) {
      const res = await api('GET', `/api/products?page=${page}&page_size=500`);
      const found = (res.data || []).filter(p => idSet.has(p.id));
      products = products.concat(found);
      if (products.length >= ids.length || !res.data || res.data.length < 500) break;
    }
  } catch(e) {
    content.innerHTML = '<div class="empty-state"><p>加载失败</p></div>';
    return;
  }'''

new_load_fav = '''async function loadFavorites() {
  await loadFavIds();
  const ids = [..._favIdSet];
  document.getElementById('fav-count').textContent = ids.length + ' 个商品';

  const content = document.getElementById('fav-content');
  const tabsEl = document.getElementById('fav-supplier-tabs');

  if (!ids.length) {
    tabsEl.innerHTML = '';
    content.innerHTML = '<div class="empty-state"><span class="icon">⭐</span><p>还没有收藏任何商品</p><p style="font-size:12px;color:var(--text3);margin-top:8px">在商品数据库里点击 ☆ 收藏</p></div>';
    return;
  }

  let products = [];
  try {
    const res = await api('GET', '/api/products?product_ids=' + ids.join(','));
    products = res.data || [];
  } catch(e) {
    content.innerHTML = '<div class="empty-state"><p>加载失败</p></div>';
    return;
  }'''

assert old_load_fav in html_content, "Could not find old loadFavorites"
html_content = html_content.replace(old_load_fav, new_load_fav)

# Fix toggleFavorite to refresh favorites page when active
old_toggle_end = "  } catch(e) { showToast('操作失败', 'error'); }\n}"
new_toggle_end = """  } catch(e) { showToast('操作失败', 'error'); }
  // 如果当前在收藏页面，自动刷新
  const favPage = document.getElementById('page-favorites');
  if (favPage && favPage.classList.contains('active')) {
    loadFavorites();
  }
}"""
assert old_toggle_end in html_content, "Could not find toggleFavorite end"
html_content = html_content.replace(old_toggle_end, new_toggle_end)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)
print("dashboard.html: fixed loadFavorites + toggleFavorite refresh")
print("\nAll fixes applied successfully!")
