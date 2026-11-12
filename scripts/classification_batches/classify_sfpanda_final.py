# -*- coding: utf-8 -*-
"""sfpanda 最后4条手动分类"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

final = {
    18870: '厨房炊具',    # PINCHE PARA PICAR - 切碎工具
    19588: '文具办公',    # BOLIGARFO BORRABLE - 可擦笔（拼写错误）
    19943: '卫浴用品',    # SET DE BAÑO
    20120: '美妆个护',    # SET DE BIJOTEURIE - 饰品套装
}

for pid, cat in final.items():
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
    print(f"  {pid} → {cat}")

conn.commit()
print(f"\n更新 {len(final)} 条")

cur.execute("""
    SELECT COUNT(*) FROM products
    WHERE supplier_id=1 AND (category IS NULL OR category='')
    AND image_local IS NOT NULL AND image_local != ''
""")
rem = cur.fetchone()[0]
print(f"sfpanda 剩余有图未分类: {rem}")

conn.close()
