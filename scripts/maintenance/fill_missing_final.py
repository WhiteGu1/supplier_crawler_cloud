"""补跑缺失的7批: 0, 122-127 (使用modelroute_api模块)"""
import pymysql, json, os, sys, time
sys.path.insert(0, r"C:\Users\Administrator\Desktop\modelroute_api")
from modelroute_api import call_model
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}
CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache"
BATCH_SIZE = 100

def get_db():
    return pymysql.connect(**DB_CONFIG)

def get_products(offset, limit):
    conn = get_db()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""SELECT p.id, p.name, p.sku, p.brand, p.supplier_id, p.price,
                   p.category as current_category, p.image_local,
                   s.name as supplier_name
                   FROM products p 
                   LEFT JOIN suppliers s ON p.supplier_id = s.id
                   WHERE p.is_available=1 
                   ORDER BY p.id
                   LIMIT %s OFFSET %s""", (limit, offset))
    rows = cur.fetchall()
    conn.close()
    for r in rows:
        r['price'] = float(r['price']) if r['price'] else 0
        r['has_image'] = bool(r.get('image_local'))
    return rows

def load_category_list():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM products WHERE is_available=1 AND category IS NOT NULL AND category!='' ORDER BY category")
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

def process_batch(batch_num):
    offset = batch_num * BATCH_SIZE
    products = get_products(offset, BATCH_SIZE)
    if not products:
        print(f"  Batch {batch_num}: 无商品，跳过")
        return
    
    print(f"--- Batch {batch_num} (offset={offset}) ---")
    print(f"  取到 {len(products)} 条商品")
    
    try:
        category_list = load_category_list()
        cat_list_str = "\n".join(category_list)
        products_json = json.dumps(products, ensure_ascii=False, indent=2)
        
        prompt = PROMPT_TEMPLATE.format(
            category_list=cat_list_str,
            products_json=products_json
        )
        
        result = call_model(
            prompt=prompt,
            model="pool-glm-5.2",
            max_tokens=8000,
            temperature=0.1,
            timeout=300,
            base_url="http://127.0.0.1:52374/v1/chat/completions"
        )
        
        if result.get("error"):
            print(f"  [ERROR] AI调用失败: {result['error']}")
            return
        
        content = result["content"].strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        data = json.loads(content)
        assignments = data.get("assignments", [])
        new_cats = data.get("new_categories", [])
        print(f"  返回 {len(assignments)} 条分类, {len(new_cats)} 个新分类")
        
        # 比对并写入
        changed = 0
        same = 0
        diff_items = []
        
        conn = get_db()
        cur = conn.cursor()
        
        for a in assignments:
            pid = a["id"]
            new_cat = a["category"]
            old = next((p["current_category"] for p in products if p["id"] == pid), "")
            if new_cat != old:
                changed += 1
                img = next((p.get("image_local") for p in products if p["id"] == pid), "")
                if img:
                    diff_items.append({"id": pid, "old_category": old, "new_category": new_cat, "image_path": img})
                # 直接写入
                cur.execute("UPDATE products SET category = %s WHERE id = %s", (new_cat, pid))
            else:
                same += 1
        
        conn.commit()
        conn.close()
        
        print(f"  比对: changed={changed}, same={same}")
        
        # 缓存
        cache_file = os.path.join(CACHE_DIR, f"batch_{batch_num}.json")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"assignments": assignments, "new_categories": new_cats}, f, ensure_ascii=False, indent=2)
        
        if diff_items:
            diff_file = os.path.join(CACHE_DIR, f"batch_{batch_num}_diff.json")
            with open(diff_file, "w", encoding="utf-8") as f:
                json.dump(diff_items, f, ensure_ascii=False, indent=2)
            print(f"  有图差异: {len(diff_items)} (已写入)")
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()

# 补跑缺失批次
missing_batches = [0, 122, 123, 124, 125, 126, 127]
for bn in missing_batches:
    process_batch(bn)
    time.sleep(2)

print("\n补跑完成!")
