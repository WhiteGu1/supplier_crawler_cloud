import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b21: 16条修正
fixes = [
    (28906, '厨房餐具'),   # TAZA 杯子
    (28907, '厨房炊具'),   # CUCHARA 勺子
    (28908, '婴幼儿用品'), # CUBIERTOS BEBE 婴儿餐具
    (28909, '厨房炊具'),   # CUCHARA 勺子
    (28910, '婴幼儿用品'), # SET BEBE 婴儿套装
    (28911, '婴幼儿用品'), # SET BEBE 竹纤维婴儿餐具
    (28912, '厨房餐具'),   # VASO PLASTICO 塑料杯
    (28913, '厨房餐具'),   # TAZA C/ASAS 带把手杯
    (28915, '厨房餐具'),   # TAZA METAL 金属杯
    (28916, '婴幼儿用品'), # PLATO P/BEBE 婴儿餐盘
    (28917, '厨房储物'),   # SET TAPPER 保鲜盒
    (28918, '厨房餐具'),   # SET PLATOS 盘子套装
    (28919, '厨房储物'),   # SET TAPPER 保鲜盒
    (28920, '厨房餐具'),   # SET PLATOS 盘子套装
    (28921, '厨房餐具'),   # SET PLATOS 盘子套装
    (28922, '厨房餐具'),   # SET PLATOS 盘子套装
]

for pid, cat in fixes:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))

conn.commit()
print(f"b21: {len(fixes)}条写入完成")
conn.close()
