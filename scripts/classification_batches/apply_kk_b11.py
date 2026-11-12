import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b11: 18条修正
b11_fixes = [
    # SERVILLETERO 餐巾架 → 餐饮用品 (10条)
    (28406, '餐饮用品'), (28407, '餐饮用品'), (28408, '餐饮用品'),
    (28409, '餐饮用品'), (28410, '餐饮用品'), (28411, '餐饮用品'),
    (28412, '餐饮用品'), (28413, '餐饮用品'), (28414, '餐饮用品'),
    (28415, '餐饮用品'),
    # INDIVIDUAL 餐垫 → 餐饮用品
    (28439, '餐饮用品'),
    # ORGANIZADOR FREGADERO 水槽收纳架 → 厨房储物 (3条)
    (28444, '厨房储物'), (28445, '厨房储物'), (28446, '厨房储物'),
    # ESCURRIDOR CUBIERTOS 餐具沥水架 → 厨房储物
    (28447, '厨房储物'),
    # DIVISOR PLAST 餐具分隔器 → 厨房储物
    (28451, '厨房储物'),
    # BALDE POCHOCLOS 爆米花桶 → 餐饮用品
    (28453, '餐饮用品'),
    # ESCARBADIENTES 牙签 → 餐饮用品
    (28454, '餐饮用品'),
]

for pid, cat in b11_fixes:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b11: {len(b11_fixes)}条写入完成")

conn.close()
