import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# Total products
cur.execute("SELECT COUNT(*) FROM products")
print(f"Total products: {cur.fetchone()[0]}")

# Check toys - use hex to avoid encoding issues
# 玩具 in UTF-8: E7 8E A9 E5 85 B7
cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%')")
total_toys = cur.fetchone()[0]
print(f"Total toys: {total_toys}")

# Toys with 3-level (has > > pattern)
cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%>%>%')")
three_level = cur.fetchone()[0]
print(f"Toys with 3-level classification: {three_level}")

# Toys needing sub-classification (base level only, no > >)
cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%'")
base_level = cur.fetchone()[0]
print(f"Toys needing sub-classification (base level): {base_level}")

# Those with images
cur.execute("SELECT COUNT(*) FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != ''")
base_with_image = cur.fetchone()[0]
print(f"Base-level toys with image: {base_with_image}")

# Sample
cur.execute("SELECT id, name, category, image_local FROM products WHERE category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != '' LIMIT 20")
rows = cur.fetchall()
print(f"\nSample needing sub-classification (first 20):")
for r in rows:
    print(f"  id={r[0]}, name={r[1]}, cat={r[2]}, img={r[3]}")

# Also check NULL/empty
cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category = ''")
print(f"\nNULL/empty category: {cur.fetchone()[0]}")

# Check supplier 11 (panda) specifically
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11")
print(f"Supplier 11 (panda) total: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND category LIKE CONCAT(CHAR(0xE7,0x8E,0xA9,0xE5,0x85,0xB7), '%') AND category NOT LIKE '%>%>%' AND image_local IS NOT NULL AND image_local != ''")
print(f"Supplier 11 needing sub-classification with image: {cur.fetchone()[0]}")

conn.close()
