"""将所有待验证的有图差异项全部写入新分类。
已抽查85条，准确率95.3%（>95%阈值），决定全部写入。
4条错误项保留旧分类。
"""
import json, sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}
CACHE = r"D:\projects\supplier_crawler\classify_cache"
VERIFY_DIR = os.path.join(CACHE, "verify_results")

# 加载所有待验证项
with open(os.path.join(VERIFY_DIR, "need_verify.json"), "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"待验证项总数: {len(items)}")

# 4条验证错误的id保留旧分类
wrong_ids = {13497, 13512, 13514, 13532}

# 连接MySQL
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

written = 0
skipped = 0
errors = 0

for item in items:
    pid = item['id']
    new_cat = item['new_category']
    
    if pid in wrong_ids:
        skipped += 1
        continue
    
    try:
        cursor.execute("UPDATE products SET category = %s WHERE id = %s", (new_cat, pid))
        written += cursor.rowcount
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f"  错误 id={pid}: {e}")

conn.commit()
conn.close()

print(f"\n写入完成:")
print(f"  写入新分类: {written}")
print(f"  保留旧分类(验证错误): {skipped}")
print(f"  错误: {errors}")
print(f"  总计: {written + skipped + errors}")
