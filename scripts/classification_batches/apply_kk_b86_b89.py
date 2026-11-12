import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# b86修正
b86 = [
    # 32193 玩具游戏 (VOLANTE c/sonido, 与32173-32175一致)
    (32193, '玩具游戏'),
    # 32194 婴幼儿用品 (BEBE a cuerda gatea, 爬行婴儿玩具)
    (32194, '婴幼儿用品'),
    # 32195 派对用品 (CARRITOS X12PCS PIÑATA, piñata填充物)
    (32195, '派对用品'),
    # 32196 玩具游戏 (MUÑECO futbol player)
    (32196, '玩具游戏'),
    # 32197 玩具游戏 (PELOTAS SALTARINAS bouncy balls)
    (32197, '玩具游戏'),
    # 32198 派对用品 (PINBALL X12PCS PIÑATA)
    (32198, '派对用品'),
    # 32199-32205 服装服饰 (GUANTES INVIERNO winter gloves from 五金工具)
    (32199, '服装服饰'), (32200, '服装服饰'), (32201, '服装服饰'),
    (32202, '服装服饰'), (32203, '服装服饰'), (32204, '服装服饰'),
    (32205, '服装服饰')
]

for pid, cat in b86:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
conn.commit()
print(f"b86: {len(b86)}条写入完成")

# b89修正
b89 = [
    (32306, '家居纺织'), (32307, '家居纺织'), (32308, '家居纺织'),
    (32309, '家居纺织'), (32310, '家居纺织'),
    (32311, '家居清洁')
]

for pid, cat in b89:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
conn.commit()
print(f"b89: {len(b89)}条写入完成")
conn.close()
