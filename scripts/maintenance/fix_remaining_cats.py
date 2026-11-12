# -*- coding: utf-8 -*-
"""处理剩余3个未映射分类"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

fixes = [
    ('KITCHEN COLLECTION > UTILITARIOS', '厨房餐具'),  # 厨房实用工具
    ('KITCHEN COLLECTION > ESCURRIDOR DE VEGETALES', '厨房炊具'),  # 蔬菜沥水器
    ('文具办公 > 剪刀', '文具办公'),  # 剪刀属文具
]

for old_cat, new_cat in fixes:
    cur.execute("UPDATE products SET category=%s WHERE category=%s", (new_cat, old_cat))
    print(f"'{old_cat}' → '{new_cat}' ({cur.rowcount} 条)")

conn.commit()

# 最终统计
cur.execute("""
    SELECT category, COUNT(*) FROM products
    WHERE category IS NOT NULL AND category != ''
    GROUP BY category ORDER BY COUNT(*) DESC
""")
final_cats = cur.fetchall()
print(f"\n最终分类数: {len(final_cats)} 个")
for cat, cnt in final_cats:
    print(f"  {cat}: {cnt}")

# 未分类
cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category=''")
uncat = cur.fetchone()[0]
print(f"\n未分类: {uncat} 条")

conn.close()
