# -*- coding: utf-8 -*-
from PIL import Image
import os

im = Image.open(r"images\gaston_16\wa_catalogo_madre.jpg")
w, h = im.size
print(f"Image dimensions: width={w}, height={h}")

# 让我们找到3列3行的卡片区域及纯图片区域
# 卡片边界和图片区域
# 图片整体在 900x1600
# 顶部有 DIA DE LA MADRE 标题 (大概 y=0 到 y=200)
# 底部留白 (大概 y=1480 到 y=1600)
