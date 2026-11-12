# -*- coding: utf-8 -*-
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

# 经过 Gaston 10.5% 价格调整（额外税）验证后，严格满足 <= Trapoman * 1.10 的对标清单
# 剔除了税后超出上限的：38034 (米色植绒衣架, +20.2%) 与 37817 (二合一调料壶, +18.1%)
MATCH_LIST = [
    # (gaston_id, trapoman_id, category_note)
    (38032, 17670, "黑色植绒衣架 (Percha Terciopelo)"),
    (38025, 17670, "金属夹衣架 (Percha Metal Broches)"),
    (38033, 17670, "金属衣架 (Perchas Metálicas)"),
    (38035, 9392,  "金属衣架 (Perchas Metálicas)"),
    (38037, 9392,  "金属挂衣架 (Perchero de Metal)"),
    (37975, 9392,  "吸盘挂钩 (Ganchos Ventosa)"),
    (38391, 7413,  "乳胶手套 (Guantes de Latex)"),
    (37954, 34151, "超细纤维清洁抹布3件套 (Set Paños Microfibra)"),
    (37956, 34151, "超细纤维拖把替换头 (Repuesto Mopa Microfibra)"),
    (38393, 7373,  "小型清洁塑料刷 (Cepillo Plástico Chico)"),
    (38394, 7264,  "小型清洁刷带簸箕 (Cepillo y Pala Chico)"),
    (37937, 7373,  "短柄清洁刷 (Cepillo Mango Corto)"),
    (37941, 7373,  "长柄清洁刷 (Cepillo Mango Largo)"),
    (38007, 7264,  "扫把挂架 (Soporte de Escoba)"),
    (38170, 7257,  "干发毛巾 (Toalla de Cabeza)"),
    (37926, 9759,  "密胺水杯 (Vaso de Melamina)"),
    (37877, 9751,  "搪瓷马克杯 (Jarrito Enlozado)"),
    (37985, 9376,  "塑料收纳盒 (Organizador)"),
    (37988, 9376,  "塑料收纳盒 (Organizador)"),
    (37886, 9376,  "冰箱收纳盒 (Organizador de Heladera)"),
    (37979, 9376,  "多功能收纳盒 (Organizador)"),
    (37982, 9376,  "多功能收纳架 (Organizador)"),
    (37960, 9376,  "白色透明收纳箱 (Caja Organizadora)"),
    (37984, 9376,  "多功能收纳盒 (Organizador)"),
    (37980, 9376,  "多功能收纳盒 (Organizador)"),
    (37996, 9376,  "布艺悬挂收纳袋 (Organizador Colgante de Tela)"),
    (37983, 9376,  "多功能收纳盒 (Organizador)"),
    (38139, 9399,  "防撞门碰/门挡 (Tope para Puerta)"),
    (38402, 9399,  "防撞保护贴4只装 (Aplique Adhesivo x4)")
]

if __name__ == '__main__':
    conn = pymysql.connect(
        host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
    )
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # 1. 确保删除税后超标的 38034 和 37817
    cur.execute("DELETE FROM favorites WHERE product_id IN (38034, 37817)")
    conn.commit()

    gaston_ids = list(dict.fromkeys([m[0] for m in MATCH_LIST]))
    print(f"验证合格的 Gaston 商品数: {len(gaston_ids)}")

    # 检查已在 favorites 的 Gaston 商品
    cur.execute("SELECT product_id FROM favorites WHERE product_id IN %s", (tuple(gaston_ids),))
    existing = {row['product_id'] for row in cur.fetchall()}

    to_insert = [pid for pid in gaston_ids if pid not in existing]
    if to_insert:
        insert_sql = "INSERT INTO favorites (product_id, saved_at) VALUES (%s, NOW())"
        cur.executemany(insert_sql, [(pid,) for pid in to_insert])
        conn.commit()
        print(f"新增 {cur.rowcount} 个合格商品至收藏夹。")
    else:
        print("所有 29 个严格合格的商品均在收藏夹中。")

    # 查询当前 Gaston 收藏商品
    cur.execute("""
        SELECT f.id as fav_id, p.id as product_id, p.sku, p.name, p.price
        FROM favorites f
        JOIN products p ON f.product_id = p.id
        WHERE p.supplier_id = 16
        ORDER BY f.id DESC
    """)
    rows = cur.fetchall()
    print(f"\n当前 Gaston 在 favorites 表中的全部收藏数: {len(rows)}")
    conn.close()
