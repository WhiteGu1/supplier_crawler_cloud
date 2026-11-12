# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np

im = Image.open(r"images\gaston_16\wa_catalogo_madre.jpg").convert('L')
arr = np.array(im)

# 寻找垂直卡片边框：在 y = 300 处扫描 x 方向
row_sample = arr[300, :]
dark_cols = np.where(row_sample < 220)[0]
print("Dark x at y=300:", dark_cols)

# 寻找水平卡片边框：在 x = 100 处扫描 y 方向
col_sample = arr[:, 100]
dark_rows = np.where(col_sample < 220)[0]
print("Dark y at x=100:", dark_rows)
