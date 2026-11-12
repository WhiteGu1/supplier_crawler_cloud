# -*- coding: utf-8 -*-
"""生成无分类商品的批次JSON文件，供subagent并行图片分类"""
import pymysql, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}

conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("""
    SELECT id, name, sku, brand, image_local
    FROM products
    WHERE (category IS NULL OR category = '')
    ORDER BY id
""")
rows = cur.fetchall()
print(f"无分类商品总数: {len(rows)}")

# 加载现有分类列表
cur2 = conn.cursor()
cur2.execute("""
    SELECT DISTINCT category FROM (
        SELECT category FROM products WHERE category IS NOT NULL AND category != ''
        UNION
        SELECT category FROM product_categories WHERE category != ''
    ) t ORDER BY category
""")
cats = [r[0] for r in cur2.fetchall()]
conn.close()

BATCH_SIZE = 10
output_dir = r"D:\projects\supplier_crawler\uncat_batches"
os.makedirs(output_dir, exist_ok=True)

# 生成批次
total_batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
for i in range(total_batches):
    start = i * BATCH_SIZE
    end = min(start + BATCH_SIZE, len(rows))
    batch = rows[start:end]
    
    batch_data = {
        "batch_id": i,
        "total": len(batch),
        "products": []
    }
    for p in batch:
        batch_data["products"].append({
            "id": p["id"],
            "name": p["name"],
            "sku": p["sku"],
            "brand": p["brand"] or "",
            "image_local": p["image_local"] or ""
        })
    
    path = os.path.join(output_dir, f"batch_{i}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(batch_data, f, ensure_ascii=False, indent=2)

# 保存分类列表
with open(os.path.join(output_dir, "category_list.json"), "w", encoding="utf-8") as f:
    json.dump(cats, f, ensure_ascii=False, indent=2)

print(f"生成 {total_batches} 个批次文件到 {output_dir}")
print(f"分类列表: {len(cats)} 条")
