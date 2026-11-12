# -*- coding: utf-8 -*-
from PIL import Image
import os

im = Image.open(r"images\gaston_16\wa_catalogo_madre.jpg").convert('RGB')

# 3行3列的外框
cols = [
    (28, 305),
    (318, 595),
    (606, 884)
]
rows = [
    (230, 631),
    (651, 1052),
    (1071, 1471)
]

# 内部纯商品照片区域 (内边距约 left+14, top+18, right-14, bottom-(631-496))
# 检查照片的精细边界
# 让我们分别保存卡片全图和商品纯照片
out_card_dir = r"d:\projects\supplier_crawler\scripts\temp\wa_cards"
out_photo_dir = r"d:\projects\supplier_crawler\scripts\temp\wa_photos"
os.makedirs(out_card_dir, exist_ok=True)
os.makedirs(out_photo_dir, exist_ok=True)

GRID = [
    (0, 0, "SBK-US463"),
    (0, 1, "SBK-56511"),
    (0, 2, "SBK-4159JA"),
    (1, 0, "SBK-4161V"),
    (1, 1, "SBK-4159V"),
    (1, 2, "SBK-4158VE"),
    (2, 0, "SBK-BRU10"),
    (2, 1, "SBK-BRU11"),
    (2, 2, "SBK-4158VB"),
]

for r_idx, c_idx, sku in GRID:
    c_x0, c_x1 = cols[c_idx]
    r_y0, r_y1 = rows[r_idx]
    
    # 1. 整张卡片
    card_crop = im.crop((c_x0, r_y0, c_x1, r_y1))
    card_crop.save(os.path.join(out_card_dir, f"{sku}_card.jpg"), quality=95)
    
    # 2. 纯商品照片 (微调内边框，去掉卡片外框线，直达内部照片的边缘)
    # 照片上方离卡片顶部约 18px，下方在文本上方（约265px高）
    p_x0 = c_x0 + 15
    p_x1 = c_x1 - 15
    p_y0 = r_y0 + 18
    p_y1 = r_y0 + 283
    
    photo_crop = im.crop((p_x0, p_y0, p_x1, p_y1))
    photo_crop.save(os.path.join(out_photo_dir, f"{sku}_photo.jpg"), quality=95)

print("Crops generated!")
