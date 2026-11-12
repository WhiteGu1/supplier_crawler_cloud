"""
商品分类执行脚本 v2
流程: AI分类(100条/批) → 缓存文件 → 比对数据库 → 识图验证差异 → 取优写入
"""
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
BATCH_SIZE = 100
MODEL = "pool-glm-5.2"
BASE_URL = "http://127.0.0.1:52374/v1/chat/completions"

PROMPT_TEMPLATE = r"""你是一个专业的商品分类专家。你的任务是将一批商品分配到最合适的分类标签中。

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

5. 分类精度要求：
   - 尽量分到三级（最精确）
   - 如果商品信息不足以判断三级，可以保留在二级
   - 不得只分到一级

## 现有分类标签列表

{category_list}

## 输入数据

每批100个商品，格式为JSON数组。

## 输出格式

返回JSON，包含两个部分：

```json
{{
  "assignments": [
    {{"id": 12345, "category": "厨房用品 > 餐具 > 刀叉勺"}}
  ],
  "new_categories": [
    {{"category": "厨房用品 > 餐具 > 封口夹", "reason": "现有列表无封口夹分类"}}
  ]
}}
```

## 分类原则

1. 以商品名称为主要依据
2. 参考SKU和品牌辅助判断
3. 不要过度细分，二级够精确就不强制到三级
4. 新分类要通用，能覆盖多件商品
5. 同类商品必须分到同一分类
6. 三级分类名2-6字，用"XX"或"XX/XX"格式
7. 每个商品必须分配分类，不允许跳过

## 商品数据

{products_json}

请输出JSON结果。只输出JSON，不要输出其他内容。"""


def get_db():
    return pymysql.connect(**DB_CONFIG)


def load_category_list():
    """从数据库加载现有分类标签列表"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM products WHERE is_available=1 AND category IS NOT NULL AND category!='' ORDER BY category")
    cats = [r[0] for r in cur.fetchall()]
    conn.close()
    return cats


def fetch_batch(offset, batch_size):
    """取一批商品"""
    conn = get_db()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute(f"""
        SELECT p.id, p.name, p.sku, p.brand, p.supplier_id, p.price, 
               p.category as current_category, p.image_local,
               s.name as supplier_name
        FROM products p 
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.is_available=1 
        ORDER BY p.id
        LIMIT %s OFFSET %s
    """, (batch_size, offset))
    rows = cur.fetchall()
    conn.close()
    # 格式化
    for r in rows:
        r['price'] = float(r['price']) if r['price'] else 0
        r['has_image'] = bool(r.get('image_local'))
    return rows


def call_ai_classify(products, category_list):
    """调用AI模型分类"""
    cat_list_str = "\n".join(category_list)
    products_json = json.dumps(products, ensure_ascii=False, indent=2)
    
    prompt = PROMPT_TEMPLATE.format(
        category_list=cat_list_str,
        products_json=products_json
    )
    
    result = call_model(
        prompt=prompt,
        model=MODEL,
        max_tokens=8000,
        temperature=0.1,
        timeout=300,
        base_url=BASE_URL
    )
    
    if result.get("error"):
        print(f"  [ERROR] AI调用失败: {result['error']}")
        return None, None
    
    content = result["content"].strip()
    # 去除可能的markdown代码块标记
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    try:
        data = json.loads(content)
        return data.get("assignments", []), data.get("new_categories", [])
    except json.JSONDecodeError as e:
        print(f"  [ERROR] JSON解析失败: {e}")
        print(f"  内容前200字: {content[:200]}")
        return None, None


def build_cache(batch_num, products, assignments, new_cats):
    """构建缓存数据"""
    # 创建 id→assignment 映射
    assign_map = {a["id"]: a["category"] for a in assignments}
    
    items = []
    for p in products:
        pid = p["id"]
        new_cat = assign_map.get(pid, p.get("current_category", ""))
        old_cat = p.get("current_category", "") or ""
        items.append({
            "id": pid,
            "name": p.get("name", ""),
            "sku": p.get("sku", ""),
            "brand": p.get("brand", ""),
            "supplier": p.get("supplier_name", ""),
            "old_category": old_cat,
            "new_category": new_cat,
            "image_local": p.get("image_local", ""),
            "has_image": p.get("has_image", False),
            "image_path": (f"D:/projects/supplier_crawler/{p['image_local']}" if p.get("image_local") else ""),
        })
    
    changed = sum(1 for i in items if i["new_category"] != i["old_category"])
    same = len(items) - changed
    
    return {
        "batch_id": batch_num,
        "timestamp": datetime.now().isoformat(timespec='seconds'),
        "total": len(items),
        "model": MODEL,
        "assignments": items,
        "new_categories": new_cats or [],
        "diff": {
            "changed": changed,
            "same": same,
            "new_l2": sum(1 for nc in (new_cats or []) if nc["category"].count(" > ") == 1),
            "new_l3": sum(1 for nc in (new_cats or []) if nc["category"].count(" > ") == 2),
        }
    }


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_db(assignments):
    """批量更新数据库"""
    conn = get_db()
    cur = conn.cursor()
    updated = 0
    for item in assignments:
        if item.get("final_category") and item["final_category"] != item.get("old_category"):
            cur.execute(
                "UPDATE products SET category=%s, updated_at=NOW() WHERE id=%s",
                (item["final_category"], item["id"])
            )
            updated += cur.rowcount
    conn.commit()
    conn.close()
    return updated


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # 加载分类列表
    category_list = load_category_list()
    print(f"初始分类数: {len(category_list)}")
    print(f"模型: {MODEL}")
    print(f"批次大小: {BATCH_SIZE}")
    print(f"缓存目录: {CACHE_DIR}")
    print("=" * 60)
    
    # 检查已完成的批次（支持断点续传）
    done_batches = set()
    for f in os.listdir(CACHE_DIR):
        if f.startswith("batch_") and f.endswith(".json") and "_diff" not in f:
            try:
                num = int(f.replace("batch_", "").replace(".json", ""))
                done_batches.add(num)
            except ValueError:
                pass
    
    if done_batches:
        print(f"已完成批次: {sorted(done_batches)}")
        start_batch = max(done_batches) + 1
        offset = (start_batch - 1) * BATCH_SIZE
        print(f"断点续传: 从批次 {start_batch} 开始 (offset={offset})")
    else:
        start_batch = 1
        offset = 0
    
    total_products = 23601
    batch_num = start_batch
    
    while offset < total_products:
        print(f"\n--- Batch {batch_num} (offset={offset}) ---")
        
        # 阶段1: 取数据 + AI分类
        products = fetch_batch(offset, BATCH_SIZE)
        if not products:
            print("没有更多商品了")
            break
        
        print(f"  取到 {len(products)} 条商品")
        
        assignments, new_cats = call_ai_classify(products, category_list)
        if assignments is None:
            print(f"  Batch {batch_num} 失败，跳过")
            offset += BATCH_SIZE
            batch_num += 1
            time.sleep(2)
            continue
        
        print(f"  AI返回 {len(assignments)} 条分类, {len(new_cats)} 个新分类")
        
        # 构建缓存
        cache = build_cache(batch_num, products, assignments, new_cats)
        cache_path = os.path.join(CACHE_DIR, f"batch_{batch_num}.json")
        write_json(cache_path, cache)
        
        # 阶段2: 比对（已在build_cache中完成）
        diff = cache["diff"]
        print(f"  比对: changed={diff['changed']}, same={diff['same']}, new_l2={diff['new_l2']}, new_l3={diff['new_l3']}")
        
        # 阶段3: 识图验证（标记，待后续执行）
        need_verify = [i for i in cache["assignments"] if i["new_category"] != i["old_category"] and i["has_image"]]
        no_img_changed = [i for i in cache["assignments"] if i["new_category"] != i["old_category"] and not i["has_image"]]
        print(f"  需识图验证: {len(need_verify)} 条, 无图差异: {len(no_img_changed)} 条")
        
        # 阶段4: 写入数据库
        # 无图差异: 直接信任AI
        # 有图差异: 标记为待验证，暂不写入
        # 未变化: 不需要写入
        to_write = []
        for item in cache["assignments"]:
            if item["new_category"] == item["old_category"]:
                item["final_category"] = item["old_category"]
            elif not item["has_image"]:
                item["final_category"] = item["new_category"]
                to_write.append(item)
            else:
                # 有图差异：暂不写入，等识图验证
                item["final_category"] = None  # 待验证
        
        # 写入无图商品的分类
        updated = update_db(to_write)
        if updated:
            print(f"  已写入数据库: {updated} 条 (无图商品)")
        
        # 保存diff文件
        diff_path = os.path.join(CACHE_DIR, f"batch_{batch_num}_diff.json")
        write_json(diff_path, cache)
        
        # 新分类加入列表
        for nc in new_cats:
            if nc["category"] not in category_list:
                category_list.append(nc["category"])
        
        print(f"  分类列表更新: {len(category_list)} 个")
        print(f"  缓存: {cache_path}")
        
        offset += BATCH_SIZE
        batch_num += 1
        
        # 短暂等待
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"全部完成! 共处理 {batch_num - start_batch} 批")
    print(f"最终分类数: {len(category_list)}")
    
    # 统计待验证
    total_verify = 0
    for f in os.listdir(CACHE_DIR):
        if f.endswith("_diff.json"):
            with open(os.path.join(CACHE_DIR, f), "r", encoding="utf-8") as fh:
                data = json.load(fh)
                total_verify += sum(1 for i in data["assignments"] if i.get("final_category") is None)
    print(f"待识图验证: {total_verify} 条")


if __name__ == "__main__":
    main()
