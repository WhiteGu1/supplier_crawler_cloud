# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

# 1. 获取所有 60 个收藏的 product_id 及其收藏时间
cur.execute("""
    SELECT f.id as fav_id, f.product_id, f.saved_at, p.id, p.name, p.price, p.created_at, p.updated_at
    FROM favorites f
    JOIN products p ON f.product_id = p.id
    WHERE p.supplier_id = 3
    ORDER BY f.id ASC
""")
fav_items = cur.fetchall()
fav_pids = {item['product_id']: item for item in fav_items}
print(f"Favorited items for Trapoman: {len(fav_pids)}")

# 检查收藏的时间顺序与商品特征
print("\n--- 收藏时间顺序前 5 和后 5 ---")
for it in fav_items[:5]:
    print(f"  Fav #{it['fav_id']} at {it['saved_at']}: [{it['id']}] {it['name']}")
print("  ...")
for it in fav_items[-5:]:
    print(f"  Fav #{it['fav_id']} at {it['saved_at']}: [{it['id']}] {it['name']}")

# 2. 测试不同的排序方式下，所有 Trapoman 商品的排列
# 常见的排序方式:
# 1) dashboard 默认: updated_at DESC (或 updated_at DESC, id DESC)
# 2) 爬虫入库顺序 / 网站页面原始顺序: id ASC (或 created_at ASC)
# 3) 网站页面倒序 / 最新抓取: id DESC
# 4) 名称 A-Z: name ASC
# 5) 价格升序 / 降序

sort_candidates = [
    ("updated_at DESC", "p.updated_at DESC, p.id DESC"),
    ("id ASC (网站原始抓取顺序)", "p.id ASC"),
    ("id DESC", "p.id DESC"),
    ("created_at ASC", "p.created_at ASC, p.id ASC"),
    ("created_at DESC", "p.created_at DESC, p.id DESC"),
    ("name ASC", "p.name ASC"),
]

for sort_label, order_sql in sort_candidates:
    # 考虑包含或不包含缺失商品
    for inc_missing in [False, True]:
        cond = "WHERE p.supplier_id = 3 AND p.is_available = 1"
        if not inc_missing:
            cond += " AND p.is_missing = 0"
        
        cur.execute(f"SELECT p.id FROM products p {cond} ORDER BY {order_sql}")
        all_ids = [r['id'] for r in cur.fetchall()]
        
        # 计算每个收藏商品的位次 (1-indexed rank)
        ranks = []
        for fav in fav_items:
            pid = fav['product_id']
            if pid in all_ids:
                rank = all_ids.index(pid) + 1
                ranks.append((rank, fav))
        
        if not ranks:
            continue
            
        rank_values = [r[0] for r in ranks]
        min_rank = min(rank_values)
        max_rank = max(rank_values)
        
        # 检查 ranks 是否与收藏时间顺序高度相关 (即浏览过程依次翻页收藏)
        # 计算秩与收藏顺序的相关性
        is_monotonic = all(rank_values[i] <= rank_values[i+1] for i in range(len(rank_values)-1))
        
        print(f"\n==================================================")
        print(f"排序: {sort_label} (含缺失={inc_missing}) | 总商品数: {len(all_ids)}")
        print(f"收藏命中数: {len(ranks)} / {len(fav_items)}")
        print(f"位次范围 (Rank): 最小第 {min_rank} 名, 最大第 {max_rank} 名")
        for page_size in [20, 24, 30, 48, 50]:
            min_page = (min_rank - 1) // page_size + 1
            max_page = (max_rank - 1) // page_size + 1
            print(f"  - 每页 {page_size} 条: 第 {min_page} 页 ~ 第 {max_page} 页 (跨度 {max_page - min_page + 1} 页)")
        
        # 打印收藏顺序对应位次的前10个和后10个
        print(f"  前 8 个收藏对应的位次: {[r[0] for r in ranks[:8]]}")
        print(f"  后 8 个收藏对应的位次: {[r[0] for r in ranks[-8:]]}")

conn.close()
