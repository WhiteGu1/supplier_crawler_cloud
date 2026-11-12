import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT product_id, category FROM product_categories WHERE category NOT LIKE '%%>%%'")
rows = cur.fetchall()
print(f"无>分隔的分类: {len(rows)}条")
for r in rows:
    print(f"  商品{r[0]}: {r[1]}")

# 修正
for pid, cat in rows:
    if cat == "厨房储物":
        new_cat = "厨房用品 > 厨房储物 > 储物罐"
    elif cat == "收纳整理":
        new_cat = "家居生活 > 收纳整理 > 收纳工具"
    else:
        new_cat = f"家居生活 > {cat} > 其他"
    cur.execute("UPDATE product_categories SET category=%s WHERE product_id=%s AND category=%s", (new_cat, pid, cat))
    print(f"  修正: {cat} -> {new_cat}")
conn.commit()

# 同步 products.category
cur.execute("SELECT COUNT(*) FROM product_categories WHERE category NOT LIKE '%%>%%'")
remaining = cur.fetchone()[0]
print(f"\n剩余无>分隔: {remaining}条")
conn.close()
