# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='admin123',
    database='supplier_crawler',
    charset='utf8mb4'
)

try:
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT id, name FROM suppliers WHERE name LIKE '%Gaston%'")
        sup = cur.fetchone()
        if not sup:
            print("未找到 Gaston 供应商！")
            sys.exit(1)
            
        sid = sup['id']
        print(f"目标供应商: {sup['name']} (ID: {sid})")

        # 更新前
        cur.execute("""
            SELECT COUNT(*) as total, 
                   COALESCE(SUM(is_missing=1), 0) as missing_count, 
                   COALESCE(SUM(is_missing=0), 0) as normal_count 
            FROM products 
            WHERE supplier_id=%s
        """, (sid,))
        before = cur.fetchone()
        print(f"更新前: 总商品 {before['total']} 件，缺失商品 {before['missing_count']} 件，正常商品 {before['normal_count']} 件")

        # 执行清除缺失标记
        affected = cur.execute("UPDATE products SET is_missing=0 WHERE supplier_id=%s", (sid,))
        conn.commit()
        print(f"执行更新: 影响行数 {affected}")

        # 更新后
        cur.execute("""
            SELECT COUNT(*) as total, 
                   COALESCE(SUM(is_missing=1), 0) as missing_count, 
                   COALESCE(SUM(is_missing=0), 0) as normal_count 
            FROM products 
            WHERE supplier_id=%s
        """, (sid,))
        after = cur.fetchone()
        print(f"更新后: 总商品 {after['total']} 件，缺失商品 {after['missing_count']} 件，正常商品 {after['normal_count']} 件")
finally:
    conn.close()
