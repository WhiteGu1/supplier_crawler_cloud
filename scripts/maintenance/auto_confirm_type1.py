"""
自动确认Type1差异（二级补充到三级，同一二级分类），写入数据库
然后收集需要识图验证的项，用subagent批量识图
"""
import json, os, sys, pymysql
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}
CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache"
VERIFY_DIR = r"D:\projects\supplier_crawler\classify_cache\verify_results"
os.makedirs(VERIFY_DIR, exist_ok=True)


def get_db():
    return pymysql.connect(**DB_CONFIG)


def main():
    # 收集所有有图差异项
    type1_items = []  # 可自动确认
    need_verify_items = []  # 需识图

    for f in sorted(os.listdir(CACHE_DIR)):
        if f.endswith('.json') and '_diff' not in f and f.startswith('batch_'):
            with open(os.path.join(CACHE_DIR, f), 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                for item in data.get('assignments', []):
                    old = item.get('old_category', '')
                    new = item.get('new_category', '')
                    if old == new:
                        continue
                    if not item.get('has_image'):
                        continue  # 无图已写入
                    
                    old_parts = old.split(' > ')
                    new_parts = new.split(' > ')
                    
                    # Type1: 二级→三级，同一级+同一二级
                    if (len(old_parts) == 2 and len(new_parts) == 3 
                        and old_parts[0] == new_parts[0] 
                        and old_parts[1] == new_parts[1]):
                        type1_items.append(item)
                    else:
                        need_verify_items.append(item)

    print(f"Type1 (自动确认): {len(type1_items)}")
    print(f"需识图验证: {len(need_verify_items)}")

    # 写入Type1
    if type1_items:
        conn = get_db()
        cur = conn.cursor()
        updated = 0
        for item in type1_items:
            cur.execute(
                "UPDATE products SET category=%s, updated_at=NOW() WHERE id=%s",
                (item['new_category'], item['id'])
            )
            updated += cur.rowcount
        conn.commit()
        conn.close()
        print(f"Type1已写入数据库: {updated} 条")

    # 保存待识图验证列表
    verify_path = os.path.join(VERIFY_DIR, "need_verify.json")
    with open(verify_path, 'w', encoding='utf-8') as f:
        json.dump(need_verify_items, f, ensure_ascii=False, indent=2)
    print(f"待验证列表: {verify_path}")
    
    # 按类型分组输出统计
    type_counts = {}
    for item in need_verify_items:
        old_parts = item['old_category'].split(' > ')
        new_parts = item['new_category'].split(' > ')
        
        if len(old_parts) == 3 and len(new_parts) == 3 and old_parts[0] == new_parts[0] and old_parts[1] == new_parts[1]:
            t = "Type2_三级变化"
        elif len(old_parts) == 2 and len(new_parts) == 3 and old_parts[0] == new_parts[0] and old_parts[1] != new_parts[1]:
            t = "Type3_换二级"
        elif old_parts[0] != new_parts[0]:
            t = "Type5_换一级"
        else:
            t = "Type6_其他"
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"\n待验证分类:")
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")
    
    # 分批，每批20条，输出第一批供识图
    batch_size = 20
    total_batches = (len(need_verify_items) + batch_size - 1) // batch_size
    print(f"\n识图验证批次: {total_batches} 批 (每批{batch_size}条)")
    
    # 保存分批列表
    batches = []
    for i in range(0, len(need_verify_items), batch_size):
        batch = need_verify_items[i:i+batch_size]
        batches.append({"batch_idx": len(batches), "items": batch})
    
    batches_path = os.path.join(VERIFY_DIR, "verify_batches.json")
    with open(batches_path, 'w', encoding='utf-8') as f:
        json.dump(batches, f, ensure_ascii=False, indent=2)
    print(f"分批列表: {batches_path}")


if __name__ == "__main__":
    main()
