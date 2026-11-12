# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np

im = Image.open(r"images\gaston_16\wa_catalogo_madre.jpg").convert('RGB')
arr = np.array(im)
h, w, _ = arr.shape

# 检测每个卡片的边框（灰色细线边框）
# 我们也可以直接看每个单元格的大致范围并精确定位
# 3 列水平分布：
# 列 0: x ~ [25, 305]
# 列 1: x ~ [315, 595]
# 列 2: x ~ [605, 885]

# 3 行垂直分布：
# 行 0: y ~ [230, 640]
# 行 1: y ~ [650, 1060]
# 行 2: y ~ [1070, 1480]

# 在每个卡片内部：
# 上半部分是纯商品照片
# 下半部分是文字描述和价格气泡

# 让我们分别打印出每个单元格内部照片的精确边框
print("Image shape:", arr.shape)
