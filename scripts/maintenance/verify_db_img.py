# -*- coding: utf-8 -*-
"""验证：DB中图片相同的offer，其image_url是否来自列表页缩略图（而非SKU图）"""
import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')
import mysql.connector
from collections import defaultdict

conn = mysql.connector.connect(
    host="localhost", port=3306, user="root", password="admin123",
    database="supplier_crawler", charset="utf8mb4", use_pure=True,
)
cur = conn.cursor(dictionary=True)

# 查offer 1036501204912 的DB数据
cur.execute("""
    SELECT product_url, name, sku, price, image_url, image_local
    FROM products WHERE supplier_id=8 
    AND product_url LIKE '%1036501204912%'
""")
rows = cur.fetchall()
print("=== DB中 offer=1036501204912 (蚊香盒) ===")
for r in rows:
    print(f"  sku={r['sku']}")
    print(f"  price={r['price']}")
    print(f"  image_url={r['image_url'][:80]}")
    print(f"  image_local={r['image_local']}")
    print()

# 对比：刚才实时解析的正确图片
correct_imgs = {
    "不带盖款（200/PCS）": "O1CN01sz8Dzz1zMCNlzsOjD",
    "带盖款（200/PCS）": "O1CN01NVkfrL1zMCNmOqgKG",
    "爱心盖带提手钉子款（96/PCS）": "O1CN01EvACHf1zMCNm1ZvXm",
    "爱心盖带提手网格款（96/PCS）": "O1CN01ZDI0q01zMCNlzxEGY",
    "雪花盖钉子款（200/PCS）": "O1CN01tjxZVS1zMCNmGXmj6",
    "蚊香桶（随机色）": "O1CN01f1Wbrw1zMCNiG6Ias",
}

print("=== 对比 ===")
for r in rows:
    db_img = r['image_url']
    # 提取DB图片中的alicdn ID
    db_match = re.search(r'O1CN\w+', db_img) if db_img else None
    db_id = db_match.group(0) if db_match else 'N/A'
    
    # 找对应的正确图片
    name_suffix = r['name'].split(' - ')[-1] if ' - ' in r['name'] else ''
    correct_id = 'N/A'
    for k, v in correct_imgs.items():
        if name_suffix[:4] in k:
            correct_id = v
            break
    
    match = '✓' if db_id == correct_id else '✗'
    print(f"  {match} {name_suffix[:15]}: DB={db_id} vs 正确={correct_id}")

cur.close()
conn.close()
