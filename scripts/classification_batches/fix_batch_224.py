"""补跑缺失的batch 224"""
import pymysql, json, os, sys, time, requests
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'}
CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache\multi_v3"
MODEL_HEADER = "qclaw/pool-minimax-m3"
GATEWAY_URL = "http://127.0.0.1:61233/v1/chat/completions"

with open(r"C:\Users\Administrator\.qclaw\openclaw.json", "r", encoding="utf-8") as f:
    _cfg = json.load(f)
GATEWAY_TOKEN = _cfg["gateway"]["auth"]["token"]

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
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("SELECT DISTINCT category FROM product_categories WHERE category != '' ORDER BY category")
cats = [r['category'] for r in cur.fetchall()]
print(f"分类路径数: {len(cats)}")

# Batch 224 = offset 22300
offset = 22300
cur.execute("SELECT p.id, p.name, p.sku, p.brand FROM products p WHERE p.is_available=1 AND p.is_missing=0 ORDER BY p.id LIMIT 100 OFFSET %s", (offset,))
products = cur.fetchall()
print(f"取到 {len(products)} 条商品 (offset={offset})")

cat_list_str = "\n".join(cats)
products_json = json.dumps(products, ensure_ascii=False, indent=2)
user_prompt = f"现有分类标签：\n{cat_list_str}\n\n商品数据（{len(products)}条）：\n{products_json}\n\n现在开始只输出JSON："

r = requests.post(GATEWAY_URL, json={
    "model": "openclaw/main",
    "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
    "max_tokens": 8000, "temperature": 0.1
}, headers={"Content-Type": "application/json", "Authorization": f"Bearer {GATEWAY_TOKEN}", "x-openclaw-model": MODEL_HEADER}, timeout=300)

print(f"HTTP {r.status_code}")
content = r.json()["choices"][0]["message"]["content"].strip()
if content.startswith("```json"): content = content[7:]
if content.startswith("```"): content = content[3:]
if content.endswith("```"): content = content[:-3]
content = content.strip()

data = json.loads(content)
assignments = data.get("assignments", [])
multi_count = sum(1 for a in assignments if len(a.get("categories", [])) > 1)
print(f"AI返回: {len(assignments)} 商品, {multi_count} 多分类")

# 写入
cur2 = conn.cursor()
wrote = 0
for a in assignments:
    pid = a["id"]
    for cat in a.get("categories", []):
        cat = cat.strip()
        if not cat: continue
        cur2.execute("INSERT IGNORE INTO product_categories (product_id, category) VALUES (%s, %s)", (pid, cat))
        wrote += cur2.rowcount
conn.commit()
print(f"写入: {wrote} 条新分类路径")

# 缓存
cache = {"batch_id": 224, "timestamp": datetime.now().isoformat(timespec='seconds'), "total": len(products), "assignments": assignments}
with open(os.path.join(CACHE_DIR, "batch_224.json"), "w", encoding="utf-8") as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)
print("缓存已保存: batch_224.json")

conn.close()
