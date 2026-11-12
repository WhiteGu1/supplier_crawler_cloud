# -*- coding: utf-8 -*-
"""
无分类新货多分类脚本
流程: 拉取无分类商品 → AI图片识别多分类 → 缓存 → 写入 product_categories + products.category
基于 reclassify_multi_v3.py 改造，针对 category IS NULL OR '' 的商品
"""
import pymysql, json, os, sys, time, requests
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}
CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache\uncategorized_20260819"
BATCH_SIZE = 10  # 图片识别每批10条
MODEL_HEADER = "qclaw/pool-minimax-m3"
GATEWAY_URL = "http://127.0.0.1:61866/v1/chat/completions"

# 从 openclaw.json 读取 token
with open(r"C:\Users\Administrator\.qclaw\openclaw.json", "r", encoding="utf-8") as f:
    _cfg = json.load(f)
GATEWAY_TOKEN = _cfg["gateway"]["auth"]["token"]

# 图片基础路径
IMAGE_BASE = r"D:\projects\supplier_crawler"

SYSTEM_PROMPT = """你是一个商品分类API。输入商品列表（含图片），输出JSON分类结果。

规则：
1. 分类格式：一级 > 二级 > 三级
2. 一级分类固定13个：厨房用品、家居生活、摆件礼品、文具、玩具、化妆品饰品、箱包皮具、电子电器、运动户外、母婴用品、宠物、五金、服装鞋帽
3. 优先从现有分类列表选择；不合适可在一级下创建新分类
4. 尽量分到三级；信息不足可止于二级；不得止于一级
5. 三级名2-6字
6. 一个商品可有多条分类（1-3条），全部并列平等
7. 多分类条件：商品确实跨品类（如玩具厨具、电子厨具、饰品箱包）
8. 不跨品类就只给1条，不凑数
9. 商品名称为西班牙语，结合图片内容判断分类

输出格式（严格JSON，不要输出任何其他文字）：
{"assignments":[{"id":12345,"categories":["分类路径1","分类路径2"]}],"new_categories":[]}"""


def get_db():
    return pymysql.connect(**DB_CONFIG)


def load_category_list():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT category FROM (
            SELECT category FROM products WHERE category IS NOT NULL AND category != ''
            UNION
            SELECT category FROM product_categories WHERE category != ''
        ) t ORDER BY category
    """)
    cats = [r[0] for r in cur.fetchall()]
    conn.close()
    return cats


def fetch_uncategorized_batch(offset, batch_size):
    """拉取无分类商品，包含图片本地路径"""
    conn = get_db()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""
        SELECT id, name, sku, brand, image_local
        FROM products
        WHERE (category IS NULL OR category = '')
        ORDER BY id
        LIMIT %s OFFSET %s
    """, (batch_size, offset))
    rows = cur.fetchall()
    conn.close()
    return rows


def call_ai_classify_with_images(products, category_list):
    """通过 Gateway OpenAI 兼容端点调用，带图片"""
    cat_list_str = "\n".join(category_list)
    
    # 构建商品信息（含图片）
    products_info = []
    for p in products:
        info = {"id": p["id"], "name": p["name"], "sku": p["sku"]}
        if p.get("brand"):
            info["brand"] = p["brand"]
        img_path = p.get("image_local", "")
        if img_path:
            full_path = os.path.join(IMAGE_BASE, img_path)
            if os.path.exists(full_path):
                info["image_path"] = full_path
            else:
                info["image_path"] = None
                info["note"] = "图片文件不存在"
        else:
            info["image_path"] = None
            info["note"] = "无图片"
        products_info.append(info)

    # 构建带图片的消息
    content_parts = []
    content_parts.append({
        "type": "text",
        "text": f"现有分类标签：\n{cat_list_str}\n\n商品数据（{len(products)}条，含图片）：\n"
    })

    for p in products_info:
        content_parts.append({
            "type": "text",
            "text": f"--- 商品 id={p['id']} ---\n名称: {p['name']}\nSKU: {p['sku']}"
        })
        if p.get("brand"):
            content_parts.append({"type": "text", "text": f"品牌: {p['brand']}"})
        
        if p.get("image_path"):
            # 使用 file URI 读取本地图片
            img_path = p["image_path"]
            try:
                import base64
                with open(img_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                # 判断图片类型
                ext = os.path.splitext(img_path)[1].lower()
                mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", 
                           ".webp": "image/webp", ".gif": "image/gif"}
                mime = mime_map.get(ext, "image/jpeg")
                content_parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{img_b64}"}
                })
            except Exception as e:
                content_parts.append({"type": "text", "text": f"图片读取失败: {e}"})
        else:
            content_parts.append({"type": "text", "text": "无图片，请根据名称判断分类"})

    content_parts.append({
        "type": "text",
        "text": "\n现在开始只输出JSON："
    })

    payload = {
        "model": "openclaw/main",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content_parts}
        ],
        "max_tokens": 8000,
        "temperature": 0.1
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "x-openclaw-model": MODEL_HEADER,
    }

    try:
        r = requests.post(GATEWAY_URL, json=payload, headers=headers, timeout=300)
        if r.status_code != 200:
            print(f"  [ERROR] HTTP {r.status_code}: {r.text[:200]}")
            return None, None
        resp = r.json()
        content = resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  [ERROR] 请求失败: {e}")
        return None, None

    # 去除markdown代码块
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
        print(f"  内容前300字: {content[:300]}")
        return None, None


def write_db_multi(pid, categories):
    conn = get_db()
    cur = conn.cursor()
    wrote = 0
    for cat in categories:
        cat = cat.strip()
        if not cat:
            continue
        cur.execute(
            "INSERT IGNORE INTO product_categories (product_id, category) VALUES (%s, %s)",
            (pid, cat)
        )
        wrote += cur.rowcount
    # 同步 products.category（如果当前为空，取第一条）
    cur.execute("SELECT category FROM products WHERE id=%s", (pid,))
    row = cur.fetchone()
    if row and not row[0]:
        if categories:
            cur.execute("UPDATE products SET category=%s, updated_at=NOW() WHERE id=%s",
                        (categories[0].strip(), pid))
    conn.commit()
    conn.close()
    return wrote


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)

    category_list = load_category_list()
    print(f"初始分类路径数: {len(category_list)}")
    print(f"模型: {MODEL_HEADER}")
    print(f"批次大小: {BATCH_SIZE}")
    print(f"缓存目录: {CACHE_DIR}")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category = ''")
    total_products = cur.fetchone()[0]
    conn.close()
    print(f"无分类商品数: {total_products}")
    print("=" * 60)

    # 断点续传
    done_batches = set()
    if os.path.exists(CACHE_DIR):
        for f in os.listdir(CACHE_DIR):
            if f.startswith("batch_") and f.endswith(".json"):
                try:
                    num = int(f.replace("batch_", "").replace(".json", ""))
                    done_batches.add(num)
                except ValueError:
                    pass

    if done_batches:
        print(f"已完成批次: {min(done_batches)}-{max(done_batches)} ({len(done_batches)}批)")
        start_batch = max(done_batches) + 1
        offset = (start_batch - 1) * BATCH_SIZE
        print(f"断点续传: 从批次 {start_batch} 开始 (offset={offset})")
    else:
        start_batch = 1
        offset = 0

    batch_num = start_batch
    total_written = 0
    total_multi = 0
    errors = 0

    while offset < total_products:
        print(f"\n--- Batch {batch_num} (offset={offset}) ---")

        products = fetch_uncategorized_batch(offset, BATCH_SIZE)
        if not products:
            print("没有更多商品了")
            break
        print(f"  取到 {len(products)} 条商品")

        assignments, new_cats = call_ai_classify_with_images(products, category_list)
        if assignments is None:
            print(f"  Batch {batch_num} 失败，跳过")
            errors += 1
            offset += BATCH_SIZE
            batch_num += 1
            time.sleep(2)
            continue

        multi_count = sum(1 for a in assignments if len(a.get("categories", [])) > 1)
        total_cats = sum(len(a.get("categories", [])) for a in assignments)
        print(f"  AI返回: {len(assignments)} 商品, {total_cats} 条分类路径, {multi_count} 商品有多分类")

        # 打印分类详情
        for a in assignments:
            pid = a["id"]
            cats = a.get("categories", [])
            print(f"    id={pid}: {cats}")

        # 写入数据库
        batch_written = 0
        for a in assignments:
            pid = a["id"]
            cats = a.get("categories", [])
            if not cats:
                continue
            wrote = write_db_multi(pid, cats)
            batch_written += wrote

        total_written += batch_written
        total_multi += multi_count
        print(f"  写入: {batch_written} 条新分类路径")

        # 缓存
        cache = {
            "batch_id": batch_num,
            "timestamp": datetime.now().isoformat(timespec='seconds'),
            "total": len(products),
            "model": MODEL_HEADER,
            "assignments": assignments,
            "new_categories": new_cats or [],
            "stats": {
                "multi_category_products": multi_count,
                "total_paths": total_cats,
                "new_writes": batch_written,
            }
        }
        cache_path = os.path.join(CACHE_DIR, f"batch_{batch_num}.json")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

        # 新分类加入列表
        for nc in (new_cats or []):
            if isinstance(nc, dict) and nc.get("category") and nc["category"] not in category_list:
                category_list.append(nc["category"])

        print(f"  分类路径总数: {len(category_list)}")
        print(f"  累计写入: {total_written}, 多分类商品: {total_multi}")

        offset += BATCH_SIZE
        batch_num += 1
        time.sleep(1)

    print("\n" + "=" * 60)
    print(f"全部完成! 共处理 {batch_num - start_batch} 批")
    print(f"总写入: {total_written} 条新分类路径")
    print(f"多分类商品: {total_multi}")
    print(f"错误批次: {errors}")
    print(f"最终分类路径数: {len(category_list)}")

    # 统计
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category = ''")
    remaining = cur.fetchone()[0]
    print(f"剩余无分类商品: {remaining}")
    conn.close()


if __name__ == "__main__":
    main()
