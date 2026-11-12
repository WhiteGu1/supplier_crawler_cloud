import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b99修正（从子agent分析提取）
# 32833-32835: SILLA COMEDOR P/BEBE → 婴幼儿用品
# 32836-32841: SILLA P/NIÑO / BANQUITO P/NIÑOS → 婴幼儿用品
# 32842-32843: BANQUETA PLAST 小塑料凳 → 家居家具
# 32844-32852: PANTALLA DE LUZ C/PORTA LAMPARA 灯罩+灯座 → 照明灯具
b99 = [
    (32833, '婴幼儿用品'), (32834, '婴幼儿用品'), (32835, '婴幼儿用品'),
    (32836, '婴幼儿用品'), (32837, '婴幼儿用品'), (32838, '婴幼儿用品'),
    (32839, '婴幼儿用品'), (32840, '婴幼儿用品'), (32841, '婴幼儿用品'),
    (32842, '家居家具'), (32843, '家居家具'),
    (32844, '照明灯具'), (32845, '照明灯具'), (32846, '照明灯具'),
    (32847, '照明灯具'), (32848, '照明灯具'), (32849, '照明灯具'),
    (32850, '照明灯具'), (32851, '照明灯具'), (32852, '照明灯具')
]

# b99中32829-32832: 小塑料椅无明确儿童标识，尺寸为儿童尺寸，保守起见归婴幼儿用品
b99_extra = [
    (32829, '婴幼儿用品'), (32830, '婴幼儿用品'), (32831, '婴幼儿用品'), (32832, '婴幼儿用品')
]
b99_all = b99 + b99_extra
for pid, cat in b99_all:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
conn.commit()
print(f"b99: {len(b99_all)}条写入完成")

# b100: 10条修正
b100 = [
    (32858, '家居家具'),
    (32862, '运动户外'), (32863, '运动户外'), (32864, '运动户外'),
    (32865, '运动户外'), (32866, '运动户外'), (32867, '运动户外'),
    (32868, '园艺户外'), (32869, '园艺户外'), (32870, '园艺户外')
]
for pid, cat in b100:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
conn.commit()
print(f"b100: {len(b100)}条写入完成")
conn.close()
