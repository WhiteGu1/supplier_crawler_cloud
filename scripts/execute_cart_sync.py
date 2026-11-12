import pymysql

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    # 1. 移除 31 件断货未下单的商品
    cur.execute('''
        DELETE c FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18 AND p.is_missing = 1
    ''')
    deleted_count = cur.rowcount
    print(f"Removed {deleted_count} out-of-stock items from cart.")

    # 2. 更新两件规格微调的商品数量
    # MASCARA DE PESTAÑAS 2 EN 1 (SKU 164435): 36 -> 6
    cur.execute('''
        UPDATE cart_items c
        JOIN products p ON c.product_id = p.id
        SET c.quantity = 6
        WHERE p.supplier_id = 18 AND p.sku = '164435'
    ''')
    # LABIAL MISS BETTY (SKU 13260): 28 -> 24
    cur.execute('''
        UPDATE cart_items c
        JOIN products p ON c.product_id = p.id
        SET c.quantity = 24
        WHERE p.supplier_id = 18 AND p.sku = '13260'
    ''')

    conn.commit()

    # 3. 核验同步后的购物车商品总数与总金额
    cur.execute('''
        SELECT COUNT(*) as item_count, SUM(c.quantity * p.price) as total_amount
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18
    ''')
    res = cur.fetchone()
    print(f"Sync complete! Bella cart now has {res['item_count']} items.")
    print(f"Total Amount: ${float(res['total_amount']):,.2f}")

conn.close()
