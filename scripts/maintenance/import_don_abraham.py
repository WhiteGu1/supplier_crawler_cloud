# -*- coding: utf-8 -*-
"""
导入 CATÁLOGO DON ABRAHAM (1) (2).pdf 到 Gaston 供应商 (supplier_id=16)
"""
import os
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"d:\projects\supplier_crawler"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pdf_parsers import get_parser

PDF_PATH = r"C:\Users\Administrator\Downloads\CATÁLOGO DON ABRAHAM (1) (2).pdf"
IMAGES_DIR = os.path.join(BASE_DIR, "images")
SUPPLIER_ID = 16

print(f"=== 开始解析 PDF: {PDF_PATH} ===")
parser = get_parser("gaston")
if not parser:
    print("错误: 未找到 gaston 解析器!")
    sys.exit(1)

products = parser.parse(PDF_PATH, IMAGES_DIR, SUPPLIER_ID)
print(f"解析完成，成功提取商品数: {len(products)}")

conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='admin123',
    database='supplier_crawler',
    charset='utf8mb4',
    autocommit=False
)

inserted = 0
updated = 0
refreshed = 0
price_changes = 0
errors = 0

try:
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name FROM suppliers WHERE id=%s", (SUPPLIER_ID,))
        sup = cursor.fetchone()
        if not sup:
            print(f"错误: 供应商 ID={SUPPLIER_ID} 不存在!")
            sys.exit(1)
        print(f"目标供应商: {sup[1]} (ID: {sup[0]})")
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE supplier_id=%s", (SUPPLIER_ID,))
        count_before = cursor.fetchone()[0]
        print(f"导入前 Gaston 商品总数: {count_before}")

        for p in products:
            sku = (p.get("sku") or "").strip()
            name = (p.get("name") or "").strip()
            price = float(p.get("price") or 0.0)
            category = (p.get("category") or "").strip()
            image = (p.get("image") or "").strip()
            desc = (p.get("description") or "").strip()
            brand = (p.get("brand") or "Don Abraham").strip()

            try:
                cursor.execute(
                    "SELECT id, price, category, image_url FROM products WHERE supplier_id=%s AND sku=%s LIMIT 1",
                    (SUPPLIER_ID, sku)
                )
                row = cursor.fetchone()

                if row:
                    prod_id, old_price, old_cat, old_img = row
                    old_price = float(old_price) if old_price is not None else 0.0

                    final_cat = old_cat if (old_cat and (not category or len(old_cat) > len(category))) else category
                    final_img = image or old_img or ""

                    if abs(old_price - price) > 0.01:
                        cursor.execute(
                            """UPDATE products 
                               SET name=%s, price=%s, category=%s, description=%s, brand=%s, image_url=%s, 
                                   is_available=1, is_missing=0, updated_at=NOW() 
                               WHERE id=%s""",
                            (name, price, final_cat, desc, brand, final_img, prod_id)
                        )
                        cursor.execute(
                            "INSERT INTO price_history (product_id, price, recorded_at) VALUES (%s, %s, NOW())",
                            (prod_id, price)
                        )
                        updated += 1
                        price_changes += 1
                    else:
                        cursor.execute(
                            """UPDATE products 
                               SET name=%s, category=%s, description=%s, brand=%s, image_url=%s, 
                                   is_available=1, is_missing=0, updated_at=NOW() 
                               WHERE id=%s""",
                            (name, final_cat, desc, brand, final_img, prod_id)
                        )
                        refreshed += 1
                else:
                    cursor.execute(
                        """INSERT INTO products 
                           (supplier_id, sku, name, price, category, description, brand, image_url, is_available, is_new, is_missing, created_at, updated_at) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, 1, 0, NOW(), NOW())""",
                        (SUPPLIER_ID, sku, name, price, category, desc, brand, image)
                    )
                    new_pid = cursor.lastrowid
                    if new_pid:
                        cursor.execute(
                            "INSERT INTO price_history (product_id, price, recorded_at) VALUES (%s, %s, NOW())",
                            (new_pid, price)
                        )
                        if category:
                            cursor.execute(
                                "INSERT INTO product_categories (product_id, category, created_at) VALUES (%s, %s, NOW())",
                                (new_pid, category)
                            )
                    inserted += 1

            except Exception as err:
                errors += 1
                print(f"处理商品失败 [{sku}] {name}: {err}")

        conn.commit()
        print("\n=== 导入数据库成功 ===")
        print(f"总解析商品: {len(products)}")
        print(f"新增商品数: {inserted}")
        print(f"价格更新数: {updated}")
        print(f"信息刷新数: {refreshed}")
        print(f"错误数:     {errors}")

        cursor.execute("SELECT COUNT(*) FROM products WHERE supplier_id=%s AND is_available=1 AND is_missing=0", (SUPPLIER_ID,))
        active_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products WHERE supplier_id=%s", (SUPPLIER_ID,))
        count_after = cursor.fetchone()[0]
        print(f"导入后 Gaston 商品总数: {count_after} (在售有效商品数: {active_count})")

except Exception as e:
    conn.rollback()
    print(f"导入过程中发生异常并已回滚: {e}")
    sys.exit(1)
finally:
    conn.close()
