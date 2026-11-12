"""对467条无分类新商品进行AI分类
批次大小: 50条/批，共10批
使用modelroute_api的call_model，已验证95%+准确率，直接写入
"""
import sys, os, json, pymysql, time
sys.path.insert(0, r"C:\Users\Administrator\Desktop\modelroute_api")
from modelroute_api import call_model
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}
CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache\new_products"
os.makedirs(CACHE_DIR, exist_ok=True)
BATCH_SIZE = 50

def get_db():
    return pymysql.connect(**DB_CONFIG)

def get_uncategorized(limit, offset):
    conn = get_db()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""SELECT p.id, p.name, p.sku, p.brand, p.supplier_id, p.price,
                   p.category as current_category, p.image_local,
                   s.name as supplier_name
                   FROM products p LEFT JOIN suppliers s ON p.supplier_id = s.id
                   WHERE (p.category IS NULL OR p.category='')
                   ORDER BY p.id LIMIT %s OFFSET %s""", (limit, offset))
    rows = cur.fetchall()
    conn.close()
    for r in rows:
        r['price'] = float(r['price']) if r['price'] else 0
        r['has_image'] = bool(r.get('image_local'))
    return rows

def load_category_list():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category!='' ORDER BY category")
    cats = [r[0] for r in cur.fetchall()]
    conn.close()
    return cats

PROMPT_TEMPLATE = """你是一个专业的商品分类专家。你的任务是将一批商品分配到最合适的分类标签中。

## 分类标签列表
{category_list}

## 分类原则
1. 以商品名称为主要判断依据，SKU/品牌作为辅助参考
2. 不要过度细分，选择最匹配的现有分类
3. 如果需要新分类，确保分类名简洁通用（2-6个字）
4. 同类商品必须使用相同的分类名
5. 三级分类名控制在2-6个字
6. 每条商品必须分配一个分类

## 商品数据

{products_json}

请输出JSON结果，格式如下：
{{"assignments": [{{"id": 商品ID, "category": "分类名"}}], "new_categories": ["新分类1"]}}

只输出JSON，不要输出其他内容。"""

# 主流程
total_uncategorized = 467
total_batches = (total_uncategorized + BATCH_SIZE - 1) // BATCH_SIZE
print(f"开始分类: {total_uncategorized}条无分类商品, {total_batches}批, 每批{BATCH_SIZE}条")
print()

category_list = load_category_list()
cat_list_str = "\n".join(category_list)
print(f"现有分类数: {len(category_list)}")
print()

for batch_num in range(total_batches):
    offset = batch_num * BATCH_SIZE
    products = get_uncategorized(BATCH_SIZE, offset)
    if not products:
        print(f"Batch {batch_num}: 无商品，跳过")
        break
    
    print(f"--- Batch {batch_num} (offset={offset}) ---")
    print(f"  取到 {len(products)} 条商品")
    
    try:
        products_json = json.dumps(products, ensure_ascii=False, indent=2)
        prompt = PROMPT_TEMPLATE.format(
            category_list=cat_list_str,
            products_json=products_json
        )
        
        result = call_model(
            prompt=prompt, model="pool-glm-5.2",
            max_tokens=8000, temperature=0.1, timeout=300,
            base_url="http://127.0.0.1:52374/v1/chat/completions"
        )
        
        if result.get("error"):
            print(f"  [ERROR] {result['error']}")
            continue
        
        content = result["content"].strip()
        if content.startswith("```json"): content = content[7:]
        if content.startswith("```"): content = content[3:]
        if content.endswith("```"): content = content[:-3]
        content = content.strip()
        
        data = json.loads(content)
        assignments = data.get("assignments", [])
        new_cats = data.get("new_categories", [])
        print(f"  返回 {len(assignments)} 条分类, {len(new_cats)} 个新分类")
        if new_cats:
            print(f"  新分类: {new_cats}")
        
        # 写入数据库
        conn = get_db()
        cur = conn.cursor()
        written = 0
        for a in assignments:
            pid = a["id"]
            new_cat = a["category"]
            cur.execute("UPDATE products SET category = %s WHERE id = %s", (new_cat, pid))
            written += cur.rowcount
        conn.commit()
        conn.close()
        print(f"  写入: {written}条")
        
        # 缓存
        cache_file = os.path.join(CACHE_DIR, f"new_batch_{batch_num}.json")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"assignments": assignments, "new_categories": new_cats}, f, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
    
    time.sleep(2)

print(f"\n全部完成! 共{total_batches}批")
