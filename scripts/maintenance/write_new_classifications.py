"""将所有分类结果写入数据库"""
import pymysql, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}

CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache\new_products"

# 收集所有结果文件
result_files = [
    "result_b0b1.json",       # batch 0-9 (100条, 文本分类)
    "result_10_11.json",      # batch 10-11 (20条)
    "result_12_13.json",      # batch 12-13 (20条)
    "result_14_15.json",      # batch 14-15 (20条)
    "result_16_17.json",      # batch 16-17 (20条)
    "result_18_19.json",      # batch 18-19 (20条)
    "result_20_21.json",      # batch 20-21 (20条)
    "result_22_23.json",      # batch 22-23 (20条)
    "result_24_25.json",      # batch 24-25 (20条)
    "result_26_27.json",      # batch 26-27 (20条)
    "result_28_29.json",      # batch 28-29 (20条)
    "result_30_31.json",      # batch 30-31 (20条)
    "result_32_33.json",      # batch 32-33 (20条)
    "result_34_35.json",      # batch 34-35 (20条)
    "result_36_37.json",      # batch 36-37 (20条)
    "result_38_39.json",      # batch 38-39 (20条)
    "result_40_41.json",      # batch 40-41 (20条)
    "result_42_43.json",      # batch 42-43 (20条)
    "result_44_45_46.json",   # batch 44-46 (27条)
]

all_assignments = []
for rf in result_files:
    path = os.path.join(CACHE_DIR, rf)
    if not os.path.exists(path):
        print(f"[缺失] {rf}")
        continue
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    all_assignments.extend(data)
    print(f"  {rf}: {len(data)}条")

print(f"\n总计: {len(all_assignments)}条分类")

# 写入数据库
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()
written = 0
errors = 0
for a in all_assignments:
    pid = a["id"]
    category = a["category"]
    cur.execute("UPDATE products SET category = %s WHERE id = %s", (category, pid))
    written += cur.rowcount
conn.commit()
conn.close()

print(f"写入数据库: {written}条")

# 验证
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM products WHERE (category IS NULL OR category='')")
remaining = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM products")
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(DISTINCT category) FROM products WHERE category IS NOT NULL AND category!=''")
distinct = cur.fetchone()[0]
conn.close()

print(f"\n=== 最终状态 ===")
print(f"总商品: {total}")
print(f"无分类: {remaining}")
print(f"去重分类数: {distinct}")
