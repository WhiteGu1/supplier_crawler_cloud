import sys
from PIL import Image
import os

sys.stdout.reconfigure(encoding='utf-8')

im = Image.open(r"images\gaston_16\wa_catalogo_madre.jpg").convert('RGB')

photo_cols = [
    (43, 292),
    (332, 581),
    (621, 870)
]

photo_rows = [
    (251, 499),
    (672, 920),
    (1092, 1340)
]

# 卡片全图（含品名和价格）
card_cols = [
    (28, 305),
    (318, 595),
    (606, 884)
]
card_rows = [
    (230, 631),
    (651, 1052),
    (1071, 1471)
]

GRID = [
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

out_dir = r"d:\projects\supplier_crawler\images\gaston_16"

for r_idx, c_idx, sku, name in GRID:
    px0, px1 = photo_cols[c_idx]
    py0, py1 = photo_rows[r_idx]
    crop = im.crop((px0, py0, px1, py1))
    
    # 保存为单独的商品图片: {sku}.jpg
    fp = os.path.join(out_dir, f"{sku}.jpg")
    crop.save(fp, "JPEG", quality=95)
    print(f"Saved {sku}.jpg (size {crop.size}) for {name}")

print("All 9 SBK product photos generated successfully!")
