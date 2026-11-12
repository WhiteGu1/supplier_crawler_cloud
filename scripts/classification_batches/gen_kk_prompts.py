import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 导出全量KK数据
cur.execute("""
    SELECT id, name, category 
    FROM products WHERE supplier_id=10 
    ORDER BY id
""")
rows = cur.fetchall()

# 分成50条一批
batch_size = 50
batches = []
for i in range(0, len(rows), batch_size):
    batch = [{"id": r[0], "name": r[1], "current_cat": r[2]} for r in rows[i:i+batch_size]]
    batches.append(batch)

print(f"总数据: {len(rows)} 条, 分 {len(batches)} 批")

# 生成prompt文件
prompt_template = """你是商品分类复查助手。以下是KK供应商的{count}条商品数据，每条包含id、name（西班牙语商品名）、current_cat（当前分类）。
请逐一检查分类是否正确，基于商品名称的语义判断。

可选标准分类（34个）：
厨房餐具 / 厨房炊具 / 厨房储物 / 餐饮用品 / 清洁用品 / 卫浴用品 / 装饰品 / 收纳整理 / 日用百货 / 文具办公 / 个人防护 / 电器电子 / 美妆个护 / 玩具游戏 / 派对用品 / 宠物用品 / 季节商品 / 婴幼儿用品 / 运动户外 / 其他 / 五金工具 / 照明灯具 / 鞋履护理 / 食品饮料 / 数码科技 / 箱包配件 / 家居纺织 / 家居家具 / 家居收纳 / 家居清洁 / 家居百货 / 家居装饰 / 旅行用品 / 时尚配饰 / 服装服饰 / 针线缝纫 / 园艺户外 / 圣诞用品

常见西班牙语关键词参考：
- TAZA/VASO/PLATO/BOTELLA/JARRA/VAJILLA/CRISTALERIA = 餐具杯壶 → 厨房餐具
- OLLA/SARTEN/UTENSILIOS/COCINA/MOLDES/CONDIMENTEROS = 炊具 → 厨房炊具
- FRASCO/TUPPERS/TERMICO/CONTENEDOR/LATA = 储物容器 → 厨房储物
- MOCHILA/BOLSO/BILLETERA/RIÑONERA/CARTERA = 包袋 → 箱包配件
- SILLA/MESA/BANQUETA/BAULERA/PUFF/MUEBLES = 家具 → 家居家具
- TOALLA/SABANA/ACOLCHADO/PIJAMA/MANTELERIA/MEDIAS/ROPA = 纺织品 → 家居纺织或服装服饰
- BOMBACHA/CULOTE/ROPA INTERIOR = 内衣 → 服装服饰
- FUNDAS = 套子 → 箱包配件
- GUANTE = 手套 → 五金工具（劳保）或个人防护
- PELOCHE/MUÑECA/JUEGO/CARROZA/XILOFON/SOLDADOS/AVIONES/VEHICULO = 玩具 → 玩具游戏
- LLAVERO/SOMBRERO/GORRO/SONAJERO/COTILLON = 派对 → 派对用品
- BOLSA REGALO = 礼品袋 → 派对用品
- BIROME/CUADERNO/CARTUCHERA/AGENDA/PIZARRA = 文具 → 文具办公
- PARLANTE/AURICULAR/CABLE/CARGADOR/CAMARA/TRANSFORMER = 电子 → 电器电子
- RELOJ = 钟表 → 时尚配饰
- BANO/JABONERA/SOPAPA = 浴室 → 卫浴用品
- LIMPIEZA/PLUMERO/CEPILLO = 清洁 → 家居清洁
- BEBE = 婴儿 → 婴幼儿用品
- DEPORTE/GUANTES GIMNASIO = 运动 → 运动户外
- HERRAMIENTAS = 工具 → 五金工具
- LUCES/LAMPARA = 灯 → 照明灯具（功能性）或家居装饰（装饰性）
- FLORERO = 花瓶 → 园艺户外
- ESPEJO/VELADOR/ADORNO/ALFOMBRA/DECORACION = 装饰 → 家居装饰
- ORGANIZADOR/CANASTA/CANASTO/CAJA = 收纳 → 家居收纳
- VIAJE = 旅行 → 旅行用品
- ACCESORIOS MODA = 时尚配饰

注意：
- LAMPARA DE MESA（台灯）如果是装饰性归"家居装饰"，如果是照明功能归"照明灯具"
- GUANTE（手套）如果是厨房用归"厨房炊具"，如果是劳保用归"五金工具"
- SET COCINA（厨房套装）归"厨房炊具"
- BOLSA（袋子）如果礼品袋归"派对用品"，如果购物袋归"日用百货"

数据：
{data}

请输出JSON数组，仅包含你认为分类有误的商品：
[{{"id": ID, "old_cat": "旧分类", "new_cat": "新分类", "reason": "原因"}}]

如果全部正确，输出空数组 []。"""

import os
os.makedirs('D:/projects/supplier_crawler/kk_prompts', exist_ok=True)

for i, batch in enumerate(batches):
    data_str = json.dumps(batch, ensure_ascii=False, indent=2)
    prompt = prompt_template.format(count=len(batch), data=data_str)
    with open(f'D:/projects/supplier_crawler/kk_prompts/batch_{i:03d}.txt', 'w', encoding='utf-8') as f:
        f.write(prompt)

print(f"已生成 {len(batches)} 个prompt文件到 kk_prompts/")
print(f"首批: batch_000.txt - batch_004.txt")

conn.close()
