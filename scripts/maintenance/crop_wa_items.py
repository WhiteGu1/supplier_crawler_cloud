# -*- coding: utf-8 -*-
from PIL import Image
import os

im = Image.open(r"images\gaston_16\wa_catalogo_madre.jpg").convert('RGB')
w, h = im.size

# 测量卡片外边框及照片区域
# 观察原图:
# Row 0:
# 卡片外框 y: ~230 到 ~640
# 内部照片 y: 245 到 505
# Col 0: 外框 x: 28 到 304, 照片 x: 42 到 290
# Col 1: 外框 x: 317 到 594, 照片 x: 331 到 579
# Col 2: 外框 x: 606 到 883, 照片 x: 620 到 868

# Row 1:
# 卡片外框 y: 650 到 1060
# 内部照片 y: 665 到 925

# Row 2:
# 卡片外框 y: 1070 到 1480
# 内部照片 y: 1085 到 1345

# 让我们用代码精确探测灰色边框（像素值约 (180, 180, 180) 到 (210, 210, 210)）
out_dir = r"d:\projects\supplier_crawler\scripts\temp\wa_crops"
os.makedirs(out_dir, exist_ok=True)

# 让我们分别测试两种裁剪方式：
# 方案 A：裁剪整张卡片（包含照片 + 品名 + 规格 + 价格气泡）
# 方案 B：裁剪商品实物照片（纯净商品图，无文字干扰）

# 9个商品对应的 SKU 和名称：
GRID_ITEMS = [
    # (row, col, sku, name)
    (0, 0, "SBK-US463",  "CAJON SET DE SPA DE 7 PIEZAS"),
    (0, 1, "SBK-56511",  "CAJON SET DE BAÑO 6 PIEZAS SPA CIRCULAR"),
    (0, 2, "SBK-4159JA", "JABÓN AROMATICO EN BARRA CON CAJA 100g"),
    (1, 0, "SBK-4161V",  "VELA DE SOJA AROMATICA MOOD 6 CM 6X6cm"),
    (1, 1, "SBK-4159V",  "VELA DE SOJA AROMATICA MOOD 10 CM 10X6cm"),
    (1, 2, "SBK-4158VE", "VELA DE SOJA EN FRASCO DE VIDRIO C/CAJA 190g"),
    (2, 0, "SBK-BRU10",  "PORTA SAHUMERIO GOTA MADERA 18MM 17X6cm"),
    (2, 1, "SBK-BRU11",  "PORTA VELA MINI MADERA 18MM C/VELA 11X8cm"),
    (2, 2, "SBK-4158VB", "TABLA CORAZON DE MADERA 18MM 20X16cm"),
]

# 测量各行各列的照片边界
# 让我们写脚本精确找出各行各列照片的具体坐标
