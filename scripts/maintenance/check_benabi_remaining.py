import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 查询 benabi (supplier_id=4) 剩余未分类商品
cur.execute("""
    SELECT id, name, image_local 
    FROM products 
    WHERE supplier_id=4 AND (category IS NULL OR category='') 
    ORDER BY id 
    LIMIT 420
""")
rows = cur.fetchall()
print(f"剩余未分类: {len(rows)} 条")
for i, (pid, name, img) in enumerate(rows):
    if i < 5 or i % 50 == 0:
        print(f"  ID={pid}, name={name[:30] if name else 'NULL'}, img={img}")
    
# 输出前5条和最后5条的完整信息
print("\n前5条:")
for pid, name, img in rows[:5]:
    print(f"  ID={pid}, img={img}")
print("\n最后5条:")
for pid, name, img in rows[-5:]:
    print(f"  ID={pid}, img={img}")

conn.close()
