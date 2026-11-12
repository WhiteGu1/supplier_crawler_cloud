"""
1. 回写 products.category = product_categories 表的第一条分类路径
2. 补跑16条无分类商品
"""
import pymysql, json, os, sys, requests
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'}
GATEWAY_URL = "http://127.0.0.1:61233/v1/chat/completions"
MODEL_HEADER = "qclaw/pool-minimax-m3"

with open(r"C:\Users\Administrator\.qclaw\openclaw.json", "r", encoding="utf-8") as f:
    GATEWAY_TOKEN = json.load(f)["gateway"]["auth"]["token"]

SYSTEM_PROMPT = """你是一个商品分类API。输入商品列表，输出JSON分类结果。

规则：
1. 分类格式：一级 > 二级 > 三级
2. 一级分类固定13个：厨房用品、家居生活、摆件礼品、文具、玩具、化妆品饰品、箱包皮具、电子电器、运动户外、母婴用品、宠物、五金、服装鞋帽
3. 优先从现有分类列表选择；不合适可在一级下创建新分类
4. 尽量分到三级；信息不足可止于二级；不得止于一级
5. 三级名2-6字
6. 一个商品可有多条分类（1-3条），全部并列平等
7. 多分类条件：商品确实跨品类（如玩具厨具、电子厨具、饰品箱包）
8. 不跨品类就只给1条，不凑数

输出格式（严格JSON，不要输出任何其他文字）：
{"assignments":[{"id":12345,"categories":["分类路径1","分类路径2"]}],"new_categories":[]}"""

conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()

# ========== Step 1: 回写 products.category ==========
print("=" * 60)
print("Step 1: 回写 products.category 与 product_categories 一致")
print("=" * 60)

# 对每个商品，取 product_categories 中第一条分类路径回写
cur.execute("""
    UPDATE products p
    INNER JOIN (
        SELECT product_id, category 
        FROM product_categories pc1
        WHERE id = (SELECT MIN(id) FROM product_categories pc2 WHERE pc2.product_id = pc1.product_id)
    ) first_cat ON p.id = first_cat.product_id
    SET p.category = first_cat.category
    WHERE p.category IS NULL OR p.category = '' OR p.category != first_cat.category
""")
updated = cur.rowcount
conn.commit()
print(f"回写完成: {updated} 条商品 category 已更新")

# 验证
cur.execute("""
    SELECT COUNT(*) FROM products p 
    WHERE p.category IS NOT NULL AND p.category != '' 
    AND NOT EXISTS (SELECT 1 FROM product_categories pc WHERE pc.product_id = p.id AND pc.category = p.category)
""")
mismatch = cur.fetchone()[0]
print(f"回写后不一致数: {mismatch}")

cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category = ''")
no_cat = cur.fetchone()[0]
print(f"无分类商品(products.category为空): {no_cat}")

# ========== Step 2: 补跑16条无分类商品 ==========
print("\n" + "=" * 60)
print("Step 2: 补跑无分类商品")
print("=" * 60)

cur.execute("SELECT id, name, sku, brand FROM products WHERE category IS NULL OR category = ''")
products = cur.fetchall()
print(f"无分类商品: {len(products)} 条")
for p in products:
    print(f"  id={p[0]} name={p[1]}")

if not products:
    print("全部已有分类，无需补跑")
    conn.close()
    sys.exit(0)

# 取现有分类列表
cur.execute("SELECT DISTINCT category FROM product_categories WHERE category != '' ORDER BY category")
cats = [r[0] for r in cur.fetchall()]
print(f"现有分类路径数: {len(cats)}")

# 调用AI分类
products_list = [{"id": p[0], "name": p[1], "sku": p[2], "brand": p[3]} for p in products]
products_json = json.dumps(products_list, ensure_ascii=False, indent=2)
cat_list_str = "\n".join(cats)
user_prompt = f"现有分类标签：\n{cat_list_str}\n\n商品数据（{len(products_list)}条）：\n{products_json}\n\n现在开始只输出JSON："

print(f"\n调用AI分类 (model={MODEL_HEADER})...")
try:
    r = requests.post(GATEWAY_URL, json={
        "model": "openclaw/main",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 4000, "temperature": 0.1
    }, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "x-openclaw-model": MODEL_HEADER
    }, timeout=120)
    
    if r.status_code != 200:
        print(f"HTTP {r.status_code}: {r.text[:300]}")
        conn.close()
        sys.exit(1)
    
    content = r.json()["choices"][0]["message"]["content"].strip()
    if content.startswith("```json"): content = content[7:]
    if content.startswith("```"): content = content[3:]
    if content.endswith("```"): content = content[:-3]
    content = content.strip()
    
    data = json.loads(content)
    assignments = data.get("assignments", [])
    print(f"AI返回: {len(assignments)} 条分类结果")
    
    for a in assignments:
        pid = a["id"]
        cat_list = a.get("categories", [])
        print(f"  id={pid}: {len(cat_list)} 条分类 -> {cat_list}")
        for cat in cat_list:
            cat = cat.strip()
            if not cat: continue
            cur.execute("INSERT IGNORE INTO product_categories (product_id, category) VALUES (%s, %s)", (pid, cat))
        # 回写 products.category
        if cat_list:
            cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat_list[0].strip(), pid))
    
    conn.commit()
    print(f"\n写入完成!")
    
except Exception as e:
    print(f"失败: {e}")
    conn.close()
    sys.exit(1)

# 最终验证
cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category = ''")
final_no_cat = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM product_categories")
pc_total = cur.fetchone()[0]
print(f"\n最终状态: 无分类商品={final_no_cat}, 多分类表={pc_total}")

conn.close()
