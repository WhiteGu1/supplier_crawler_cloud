import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from database.db_manager import DatabaseManager

db = DatabaseManager(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "admin123"),
    database=os.getenv("DB_NAME", "supplier_crawler"),
)
with db.connection() as conn:
    cursor = conn.cursor(buffered=True)

    # 1. 重复商品名
    cursor.execute("""
        SELECT name, COUNT(*) as cnt FROM products 
        WHERE is_available=1 
        GROUP BY name HAVING cnt > 1 
        ORDER BY cnt DESC
    """)
    rows = cursor.fetchall()
    if rows:
        print(f"=== 重复商品名: {len(rows)}组 ===")
        for r in rows[:30]:
            print(f"  [{r[1]}次] {r[0][:70]}")
    else:
        print("=== 没有重复商品名 ===")

    # 2. 重复URL
    cursor.execute("""
        SELECT product_url, COUNT(*) as cnt FROM products 
        WHERE is_available=1 AND product_url IS NOT NULL AND product_url != ''
        GROUP BY product_url HAVING cnt > 1 
        ORDER BY cnt DESC
    """)
    rows2 = cursor.fetchall()
    if rows2:
        print(f"\n=== 重复URL: {len(rows2)}组 ===")
        for r in rows2[:30]:
            print(f"  [{r[1]}次] {r[0][:90]}")
    else:
        print("\n=== 没有重复URL ===")

    # 3. 按供应商统计
    cursor.execute("""
        SELECT s.name, COUNT(p.id) as cnt 
        FROM suppliers s LEFT JOIN products p ON s.id=p.supplier_id AND p.is_available=1
        GROUP BY s.id, s.name ORDER BY cnt DESC
    """)
    print("\n=== 各供应商商品数 ===")
    for r in cursor.fetchall():
        print(f"  {r[0]}: {r[1]}")

    # 4. 总数
    cursor.execute("SELECT COUNT(*) FROM products WHERE is_available=1")
    print(f"\n商品总数: {cursor.fetchone()[0]}")
