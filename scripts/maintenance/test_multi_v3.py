"""测试多分类v3 - 只跑10条"""
import sys, os
sys.path.insert(0, r'D:\projects\supplier_crawler')
sys.stdout.reconfigure(encoding='utf-8')

from reclassify_multi_v3 import (
    get_db, load_category_list, fetch_batch, call_ai_classify, write_db_multi,
    CACHE_DIR, MODEL_HEADER
)

os.makedirs(CACHE_DIR, exist_ok=True)

# 1. 加载分类列表
category_list = load_category_list()
print(f"分类路径数: {len(category_list)}")

# 2. 取10条商品
products = fetch_batch(0, 10)
print(f"取到 {len(products)} 条商品:")
for p in products:
    print(f"  {p['id']}: {p['name']}")

# 3. AI多分类
print(f"\n调用AI分类 (model={MODEL_HEADER})...")
assignments, new_cats = call_ai_classify(products, category_list)
if assignments is None:
    print("AI分类失败!")
    sys.exit(1)

print(f"\nAI返回 {len(assignments)} 条:")
for a in assignments:
    cats = a.get("categories", [])
    print(f"  {a['id']}: {len(cats)}条分类")
    for c in cats:
        print(f"    -> {c}")

if new_cats:
    print(f"\n新分类: {len(new_cats)}")
    for nc in new_cats:
        print(f"  {nc['category']}: {nc.get('reason','')}")

# 4. 写入数据库
print("\n写入数据库...")
for a in assignments:
    wrote = write_db_multi(a["id"], a.get("categories", []))
    if wrote:
        print(f"  {a['id']}: 新写入 {wrote} 条")

# 5. 验证
conn = get_db()
cur = conn.cursor()
for a in assignments:
    pid = a["id"]
    cur.execute("SELECT category FROM product_categories WHERE product_id=%s ORDER BY id", (pid,))
    cats = [r[0] for r in cur.fetchall()]
    print(f"  商品{pid} 分类: {cats}")
conn.close()
print("\n测试完成!")
