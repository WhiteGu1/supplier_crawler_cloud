import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b88: 18条修正
b88 = [
    # 5条 时尚配饰→服装服饰 (32271-32275)
    (32271, '服装服饰'), (32272, '服装服饰'), (32273, '服装服饰'),
    (32274, '服装服饰'), (32275, '服装服饰'),
    # 8条 运动户外→服装服饰 (32283,32284,32286-32291)
    (32283, '服装服饰'), (32284, '服装服饰'), (32286, '服装服饰'),
    (32287, '服装服饰'), (32288, '服装服饰'), (32289, '服装服饰'),
    (32290, '服装服饰'), (32291, '服装服饰'),
    # 1条 运动户外→家居纺织 (32285)
    (32285, '家居纺织'),
    # 4条 卫浴用品→婴幼儿用品 (32295,32296,32297,32301)
    (32295, '婴幼儿用品'), (32296, '婴幼儿用品'),
    (32297, '婴幼儿用品'), (32301, '婴幼儿用品')
]
for pid, cat in b88:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
conn.commit()
print(f"b88: {len(b88)}条写入完成")

# b90: 2条修正
b90 = [
    (32368, '家居纺织'), (32370, '家居纺织')
]
for pid, cat in b90:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
conn.commit()
print(f"b90: {len(b90)}条写入完成")
conn.close()
