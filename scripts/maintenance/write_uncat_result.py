# -*- coding: utf-8 -*-
"""
写入分类结果到数据库
用法: python write_uncat_result.py <result_json_file>
result_json_file 格式: [{"id": 35498, "categories": ["家居生活 > 收纳整理 > 装饰贴", ...]}, ...]
"""
import pymysql, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}

def write_results(results):
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    written = 0
    for r in results:
        pid = r["id"]
        cats = r.get("categories", [])
        if not cats:
            continue
        for cat in cats:
            cat = cat.strip()
            if not cat:
                continue
            cur.execute(
                "INSERT IGNORE INTO product_categories (product_id, category) VALUES (%s, %s)",
                (pid, cat)
            )
            written += cur.rowcount
        # 同步 products.category
        cur.execute("SELECT category FROM products WHERE id=%s", (pid,))
        row = cur.fetchone()
        if row and not row[0]:
            cur.execute("UPDATE products SET category=%s, updated_at=NOW() WHERE id=%s",
                        (cats[0].strip(), pid))
    conn.commit()
    conn.close()
    return written

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python write_uncat_result.py <result_json_file>")
        sys.exit(1)
    
    result_file = sys.argv[1]
    with open(result_file, "r", encoding="utf-8") as f:
        results = json.load(f)
    
    written = write_results(results)
    print(f"写入完成: {len(results)} 条商品, {written} 条新分类路径")
