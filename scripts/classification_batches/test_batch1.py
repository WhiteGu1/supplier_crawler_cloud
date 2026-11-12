"""测试第1批分类"""
import pymysql, json, os, sys, time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"C:\Users\Administrator\Desktop\modelroute_api")
from modelroute_api import call_model

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}
CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache"
MODEL = "pool-glm-5.2"
BASE_URL = "http://127.0.0.1:52374/v1/chat/completions"

PROMPT_TEMPLATE = """你是一个专业的商品分类专家。你的任务是将一批商品分配到最合适的分类标签中。

## 分类规则

1. 分类格式为三级结构：一级分类 > 二级分类 > 三级分类
2. 必须从现有分类标签列表中选择；如果列表中没有合适的分类，可以创建新分类
3. 创建新分类时，必须在现有的一级分类体系内创建，不得新建一级分类
4. 一级分类固定为以下13个，不可修改：
   - 厨房用品
   - 家居生活
   - 摆件礼品
   - 文具
   - 玩具
   - 化妆品饰品
   - 箱包皮具
   - 电子电器
   - 运动户外
   - 母婴用品
   - 宠物
   - 五金
   - 服装鞋帽

5. 尽量分到三级；信息不足可保留二级；不得只分到一级

## 现有分类标签列表

{category_list}

## 输出格式

返回JSON：
```json
{{
  "assignments": [{{"id": 12345, "category": "厨房用品 > 餐具 > 刀叉勺"}}],
  "new_categories": [{{"category": "厨房用品 > 餐具 > 封口夹", "reason": "原因"}}]
}}
```

## 分类原则

1. 以商品名称为主要依据
2. 不过度细分，二级够精确就不强制到三级
3. 新分类要通用，能覆盖多件商品
4. 三级分类名2-6字
5. 每个商品必须分配分类

## 商品数据

{products_json}

只输出JSON，不要输出其他内容。"""


def get_db():
    return pymysql.connect(**DB_CONFIG)


def load_category_list():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM products WHERE is_available=1 AND category IS NOT NULL AND category!='' ORDER BY category")
    cats = [r[0] for r in cur.fetchall()]
    conn.close()
    return cats


def fetch_batch(offset, size):
    conn = get_db()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""
        SELECT p.id, p.name, p.sku, p.brand, p.supplier_id, p.price,
               p.category as current_category, p.image_local,
               s.name as supplier_name
        FROM products p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.is_available=1
        ORDER BY p.id
        LIMIT %s OFFSET %s
    """, (size, offset))
    rows = cur.fetchall()
    conn.close()
    for r in rows:
        r['price'] = float(r['price']) if r['price'] else 0
        r['has_image'] = bool(r.get('image_local'))
    return rows


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)

    category_list = load_category_list()
    print(f"初始分类: {len(category_list)} 个")

    # 取第1批
    products = fetch_batch(0, 100)
    print(f"取到 {len(products)} 条商品")

    # 构建输入数据（精简字段）
    input_products = []
    for p in products:
        input_products.append({
            "id": p["id"],
            "name": p["name"],
            "sku": p.get("sku", ""),
            "brand": p.get("brand", ""),
            "supplier": p.get("supplier_name", ""),
            "price": p["price"],
            "current_category": p.get("current_category", "")
        })

    cat_str = "\n".join(category_list)
    prod_json = json.dumps(input_products, ensure_ascii=False, indent=2)

    prompt = PROMPT_TEMPLATE.format(category_list=cat_str, products_json=prod_json)
    print(f"Prompt长度: {len(prompt)} 字符")

    # 调用AI
    print("调用AI分类中...")
    t0 = time.time()
    result = call_model(prompt=prompt, model=MODEL, max_tokens=8000, temperature=0.1, timeout=300, base_url=BASE_URL)
    elapsed = time.time() - t0
    err = result.get("error")
    print(f"耗时: {elapsed:.1f}s, 错误: {err}")

    if err:
        print(f"失败: {err}")
        return

    content = result["content"].strip()
    # 清理markdown
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    try:
        data = json.loads(content)
        assignments = data.get("assignments", [])
        new_cats = data.get("new_categories", [])
        print(f"返回: {len(assignments)} 条分类, {len(new_cats)} 个新分类")

        # 比对
        assign_map = {}
        for a in assignments:
            assign_map[a["id"]] = a["category"]
        
        changed = 0
        same = 0
        for p in products:
            new = assign_map.get(p["id"], p.get("current_category", ""))
            old = p.get("current_category", "") or ""
            if new != old:
                changed += 1
            else:
                same += 1

        print(f"比对: changed={changed}, same={same}")

        if new_cats:
            print("新分类:")
            for nc in new_cats:
                print(f"  - {nc['category']}: {nc.get('reason', '')}")

        # 写缓存
        cache_items = []
        for p in products:
            pid = p["id"]
            new_cat = assign_map.get(pid, p.get("current_category", ""))
            old_cat = p.get("current_category", "") or ""
            img = p.get("image_local", "")
            cache_items.append({
                "id": pid,
                "name": p.get("name", ""),
                "old_category": old_cat,
                "new_category": new_cat,
                "image_local": img,
                "has_image": bool(img),
                "image_path": f"D:/projects/supplier_crawler/{img}" if img else "",
            })

        cache = {
            "batch_id": 1,
            "timestamp": datetime.now().isoformat(timespec='seconds'),
            "total": len(products),
            "model": MODEL,
            "assignments": cache_items,
            "new_categories": new_cats,
            "diff": {"changed": changed, "same": same}
        }

        cache_path = os.path.join(CACHE_DIR, "batch_1.json")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print(f"缓存已写入: {cache_path}")

        # 显示前5条变化
        shown = 0
        for item in cache_items:
            if item["new_category"] != item["old_category"] and shown < 5:
                print(f"  变化: id={item['id']} | {item['old_category']} -> {item['new_category']} | 图={item['has_image']}")
                shown += 1

    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"内容前500字: {content[:500]}")


if __name__ == "__main__":
    main()
