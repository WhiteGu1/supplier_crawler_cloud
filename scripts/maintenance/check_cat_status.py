"""检查当前分类状态"""
import pymysql

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1 AND is_missing=0")
print(f"可用商品总数: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM products WHERE category IS NOT NULL AND category != ''")
print(f"有分类商品数: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM product_categories")
print(f"多分类表总数: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM (SELECT product_id, COUNT(*) as cnt FROM product_categories GROUP BY product_id HAVING cnt > 1) t")
print(f"已有多分类的商品数: {cur.fetchone()[0]}")

cur.execute("SELECT DISTINCT category FROM product_categories ORDER BY category")
cats = [r[0] for r in cur.fetchall()]
print(f"\n分类路径数: {len(cats)}")
print("所有一级分类:")
mains = sorted(set(c.split(' > ')[0] for c in cats))
for m in mains:
    cur.execute("SELECT COUNT(*) FROM product_categories WHERE category=%s OR category LIKE %s", (m, m + ' > %'))
    cnt = cur.fetchone()[0]
    print(f"  {m}: {cnt}条")

# 看看之前的分类提示词
import os
cache_dir = r'D:\projects\supplier_crawler\classify_cache'
if os.path.exists(cache_dir):
    files = os.listdir(cache_dir)
    print(f"\n缓存目录文件数: {len(files)}")
    # 找prompt文件
    for f in files:
        if 'prompt' in f.lower() or 'rule' in f.lower() or f.endswith('.txt'):
            print(f"  文本文件: {f}")
    # 看第一个batch
    for f in sorted(files):
        if f.startswith('batch_') and f.endswith('.json'):
            print(f"  示例batch: {f}")
            break

conn.close()
