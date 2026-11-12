import sys
sys.path.insert(0, 'd:/projects/supplier_crawler')
from database.db_manager import DatabaseManager
db = DatabaseManager('localhost', 3306, 'root', 'admin123', 'supplier_crawler')
with db.connection() as conn:
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*), COUNT(stock), MIN(stock), MAX(stock), SUM(CASE WHEN stock > 0 THEN 1 ELSE 0 END), SUM(CASE WHEN stock = 0 THEN 1 ELSE 0 END), SUM(CASE WHEN stock IS NULL THEN 1 ELSE 0 END) FROM products")
    print("--- STOCK STATS ---")
    print(cur.fetchone())

    cur.execute("SELECT is_missing, COUNT(*) FROM products GROUP BY is_missing")
    print("--- IS_MISSING STATS ---")
    for r in cur.fetchall():
        print(r)

    # Let's check how the crawlers write is_available or stock
    cur.execute("SELECT s.name, COUNT(*) as total, SUM(CASE WHEN p.stock > 0 THEN 1 ELSE 0 END) as stock_pos, SUM(CASE WHEN p.stock = 0 THEN 1 ELSE 0 END) as stock_zero, SUM(CASE WHEN p.stock IS NULL THEN 1 ELSE 0 END) as stock_null, SUM(p.is_available) as avail_sum, SUM(p.is_missing) as missing_sum FROM products p JOIN suppliers s ON p.supplier_id=s.id GROUP BY s.id, s.name")
    print("--- SUPPLIER STOCK STATS ---")
    for r in cur.fetchall():
        print(r)
