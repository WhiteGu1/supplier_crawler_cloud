import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 1. 补标记KK今日导入的新商品 is_new=1
cur.execute("UPDATE products SET is_new=1 WHERE supplier_id=10 AND created_at > NOW() - INTERVAL 1 DAY AND is_new=0")
print(f"补标记 is_new=1: {cur.rowcount} 条")
conn.commit()

# 2. 模拟爬虫的缺失标记逻辑：
#    PDF导入的全量SKU集合 = 本次的商品
#    已有商品不在本次集合中的 = 缺失
# 先获取KK本次导入的所有 SKU+name 组合
cur.execute("SELECT sku, name FROM products WHERE supplier_id=10 AND created_at > NOW() - INTERVAL 1 DAY")
imported = set()
for r in cur.fetchall():
    imported.add((r[0].strip() if r[0] else '', r[1].strip() if r[1] else ''))

# 获取KK所有已有商品
cur.execute("SELECT id, sku, name FROM products WHERE supplier_id=10")
missing_ids = []
for r in cur.fetchall():
    pid, sku, name = r
    key = (sku.strip() if sku else '', name.strip() if name else '')
    if key not in imported:
        missing_ids.append(pid)

print(f"KK总商品中不在本次导入的: {len(missing_ids)} 条")

# 清除旧缺失标记，再标记新的
cur.execute("UPDATE products SET is_missing=0 WHERE supplier_id=10")
print(f"清除旧缺失标记: {cur.rowcount} 条")

if missing_ids:
    # 批量标记
    placeholders = ','.join(['%s'] * len(missing_ids))
    cur.execute(f"UPDATE products SET is_missing=1 WHERE id IN ({placeholders})", missing_ids)
    print(f"标记缺失: {cur.rowcount} 条")

conn.commit()

# 验证
cur.execute("SELECT COUNT(*), SUM(is_new), SUM(is_missing), SUM(is_available) FROM products WHERE supplier_id=10")
r = cur.fetchone()
print(f"\n最终状态: 总数={r[0]} 新商品={r[1]} 缺失={r[2]} 可用={r[3]}")

conn.close()
