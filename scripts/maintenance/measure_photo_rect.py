# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np

im = Image.open(r"images\gaston_16\wa_catalogo_madre.jpg").convert('L')
arr = np.array(im)

# Col 2: x in [606, 884]
# Row 1: y in [651, 1052]
# 在这个区域里，纯照片的具体边框在哪里？
# 我们看 x=745 (中心垂直线)，从 y=655 往下扫描：
print("Scanning vertical line x=745 for Row 1:")
for y in range(655, 950):
    val = arr[y, 745]
    # 打印照片顶边和底边的突变点
    if y in [660, 665, 670, 671, 672, 915, 916, 917, 918, 920, 925]:
        print(f"y={y}: val={val}")

# 同样看 y=750 (中心水平线)，从 x=606 扫描到 884：
print("\nScanning horizontal line y=750 for Col 2:")
for x in range(615, 875):
    val = arr[750, x]
    if x in [615, 620, 621, 622, 623, 868, 869, 870, 871, 872]:
        print(f"x={x}: val={val}")
