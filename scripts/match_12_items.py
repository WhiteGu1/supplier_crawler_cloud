import os
from database.db_manager import DatabaseManager

db = DatabaseManager(
    os.getenv('DB_HOST', 'localhost'),
    int(os.getenv('DB_PORT', 3306)),
    os.getenv('DB_USER', 'root'),
    os.getenv('DB_PASSWORD', 'admin123'),
    os.getenv('DB_NAME', 'supplier_crawler')
)

with db.connection() as conn:
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, sku, name, price, product_url
        FROM products
        WHERE supplier_id = 18
          AND (
              name LIKE '%19247%' OR sku LIKE '%19247%' OR product_url LIKE '%19247%'
              OR name LIKE '%VINCHA%'
              OR name LIKE '%3079%' OR name LIKE '%3080%'
              OR name LIKE '%BC1127%' OR name LIKE '%SFD%'
          )
    """)
    for r in cur.fetchall():
        print(f"ID={r['id']} | SKU={r['sku']} | Price={r['price']} | Name={r['name']} | URL={r['product_url']}")
