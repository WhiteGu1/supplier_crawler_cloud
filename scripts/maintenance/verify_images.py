"""
识图验证脚本
对有图差异项，用image工具验证AI分类是否正确，取优写入数据库。

策略：
1. 按batch读取缓存，收集所有有图差异项
2. 每批取一个子集（如20条），用image工具看图判断
3. 如果AI分类正确 → 用新分类
4. 如果AI分类错误 → 保留旧分类
5. 无图差异项直接信任AI
"""
import json, os, sys, time
import pymysql
from datetime import datetime

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


def load_all_diff_items():
    """加载所有有图差异项"""
    items = []
    for f in sorted(os.listdir(CACHE_DIR)):
        if f.endswith('.json') and '_diff' not in f and f.startswith('batch_'):
            with open(os.path.join(CACHE_DIR, f), 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                for item in data.get('assignments', []):
                    if item.get('new_category') != item.get('old_category') and item.get('has_image'):
                        item['batch_id'] = data['batch_id']
                        items.append(item)
    return items


def load_no_img_diff_items():
    """加载所有无图差异项"""
    items = []
    for f in sorted(os.listdir(CACHE_DIR)):
        if f.endswith('.json') and '_diff' not in f and f.startswith('batch_'):
            with open(os.path.join(CACHE_DIR, f), 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                for item in data.get('assignments', []):
                    if item.get('new_category') != item.get('old_category') and not item.get('has_image'):
                        item['batch_id'] = data['batch_id']
                        items.append(item)
    return items


def write_no_img_to_db():
    """无图差异项直接写入数据库"""
    items = load_no_img_diff_items()
    print(f"无图差异项: {len(items)} 条")

    if not items:
        return 0

    conn = get_db()
    cur = conn.cursor()
    updated = 0
    for item in items:
        cur.execute(
            "UPDATE products SET category=%s, updated_at=NOW() WHERE id=%s",
            (item['new_category'], item['id'])
        )
        updated += cur.rowcount
    conn.commit()
    conn.close()
    print(f"已写入数据库: {updated} 条")
    return updated


def prepare_verify_batches(items, batch_size=20):
    """将待验证项分成小批，每批20条"""
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i+batch_size])
    return batches


def save_verify_result(batch_idx, results):
    """保存识图验证结果"""
    path = os.path.join(VERIFY_DIR, f"verify_{batch_idx}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return path


def apply_verified_to_db(results):
    """将验证结果写入数据库"""
    conn = get_db()
    cur = conn.cursor()
    updated = 0
    for r in results:
        final_cat = r.get('final_category')
        if final_cat and final_cat != r.get('old_category'):
            cur.execute(
                "UPDATE products SET category=%s, updated_at=NOW() WHERE id=%s",
                (final_cat, r['id'])
            )
            updated += cur.rowcount
    conn.commit()
    conn.close()
    return updated


def main():
    # 阶段1: 写入无图差异项
    print("=" * 60)
    print("阶段1: 写入无图差异项（直接信任AI）")
    print("=" * 60)
    no_img_count = write_no_img_to_db()

    # 阶段2: 准备有图差异项验证
    print("\n" + "=" * 60)
    print("阶段2: 准备识图验证")
    print("=" * 60)
    items = load_all_diff_items()
    print(f"有图差异项: {len(items)} 条")

    # 分批，每批20条
    verify_batches = prepare_verify_batches(items, 20)
    print(f"验证批次: {len(verify_batches)} 批 (每批20条)")

    # 保存待验证列表
    all_verify = []
    for i, batch in enumerate(verify_batches):
        all_verify.append({"batch_idx": i, "items": batch})

    verify_list_path = os.path.join(VERIFY_DIR, "verify_list.json")
    with open(verify_list_path, 'w', encoding='utf-8') as f:
        json.dump(all_verify, f, ensure_ascii=False, indent=2)
    print(f"验证列表: {verify_list_path}")

    # 输出第一批的前20条供识图
    if verify_batches:
        print(f"\n第一批待验证 (20条):")
        for item in verify_batches[0]:
            print(f"  id={item['id']} | {item['old_category']} -> {item['new_category']}")
            print(f"    name: {item.get('name','')[:40]}")
            print(f"    img: {item.get('image_path','')}")

    # 统计
    print(f"\n汇总:")
    print(f"  无图差异(已写入): {no_img_count}")
    print(f"  有图差异(待验证): {len(items)}")
    print(f"  验证批次: {len(verify_batches)}")


if __name__ == "__main__":
    main()
