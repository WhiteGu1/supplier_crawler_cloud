# -*- coding: utf-8 -*-
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# Check Trapoman uncategorized
cur.execute("""
    SELECT id, name, image_local FROM products
    WHERE supplier_id=3 AND (category IS NULL OR category='')
    ORDER BY id LIMIT 20
""")
rows = cur.fetchall()
print(f"Trapoman uncategorized sample (showing 20 of 2400):")
for r in rows:
    print(f"  {r[0]}\t{r[1][:50]}\timg={'Y' if r[2] else 'N'}")

# Check if these are the old data that was reset
cur.execute("""
    SELECT COUNT(*) FROM products
    WHERE supplier_id=3 AND (category IS NULL OR category='')
    AND image_local IS NOT NULL AND image_local != ''
""")
img_uncat = cur.fetchone()[0]
print(f"\nTrapoman uncategorized with image: {img_uncat}")

cur.execute("""
    SELECT COUNT(*) FROM products
    WHERE supplier_id=3 AND (category IS NULL OR category='')
    AND (image_local IS NULL OR image_local = '')
""")
no_img = cur.fetchone()[0]
print(f"Trapoman uncategorized without image: {no_img}")

# Now get osa and sfpanda lists
for sid, name in [(5, 'osa'), (1, 'sfpanda')]:
    cur.execute("""
        SELECT id, image_local, name FROM products
        WHERE supplier_id=%s AND (category IS NULL OR category='')
        AND image_local IS NOT NULL AND image_local != ''
        ORDER BY id
    """, (sid,))
    rows = cur.fetchall()
    print(f"\n{name}: {len(rows)} items with image")
    if sid == 5:  # osa, show all
        for r in rows:
            img = r[1]
            if img.startswith('./'):
                full = 'D:/projects/supplier_crawler/' + img[2:]
            elif img.startswith('images/'):
                full = 'D:/projects/supplier_crawler/' + img
            else:
                full = img
            print(f"  {r[0]}\t{full}\t{r[2][:40]}")

conn.close()
