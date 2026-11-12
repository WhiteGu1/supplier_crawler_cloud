import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# 已完成的批次结果
results = [
  # batch-0
  {"id": 2176, "category": "清洁用品", "desc": "多色小型喷雾瓶，带扳机式喷头，LANBENA品牌"},
  {"id": 2177, "category": "厨房炊具", "desc": "Candela品牌厨房防风火焰点火枪/点火器"},
  {"id": 2178, "category": "美妆个护", "desc": "Hot Tools品牌多色美发梳/直发梳"},
  {"id": 2179, "category": "五金工具", "desc": "双面磨刀石/砂岩磨石，灰色长方体形"},
  {"id": 2180, "category": "文具办公", "desc": "KK-82MS学生科学函数计算器，带多行显示屏"},
  {"id": 2181, "category": "运动户外", "desc": "深蓝色充气枕头，露营旅行用便携款"},
  {"id": 2182, "category": "玩具游戏", "desc": "Bingo Familiar墨西哥传统宾果游戏，木质游戏筹码"},
  {"id": 2183, "category": "其他", "desc": "气泡缓冲膜/气柱包装卷，运输防震填充"},
  {"id": 2184, "category": "清洁用品", "desc": "Condal品牌彩色塑料苍蝇拍/苍蝇拍组"},
  {"id": 2185, "category": "派对用品", "desc": "紫色大理石纹路圆形派对气球"},
  # batch-1
  {"id": 2186, "category": "文具办公", "desc": "彩色塑料文件夹/活页夹，多色装订文件册"},
  {"id": 2187, "category": "文具办公", "desc": "Épica 90g A4复印纸，480张装"},
  {"id": 2188, "category": "文具办公", "desc": "黄色便利贴/便签纸，100g装订堆叠"},
  {"id": 2189, "category": "电器电子", "desc": "Candela 蓝色 AA碱性电池，5节装卡装"},
  {"id": 2190, "category": "电器电子", "desc": "Candela 蓝色电池吸塑包装，多节装"},
  {"id": 2191, "category": "电器电子", "desc": "Candela 黑色电池吸塑包装，10节装"},
  {"id": 2192, "category": "电器电子", "desc": "Candela 蓝色电池吸塑包装，多节装"},
  {"id": 2193, "category": "电器电子", "desc": "Eveready 金霸王通用电池红色包装盒"},
  {"id": 2194, "category": "电器电子", "desc": "Maxell CR2032 3V纽扣电池，5粒装"},
  {"id": 2195, "category": "电器电子", "desc": "Maxell AA/AAA碱性电池，多节装"},
  # batch-2
  {"id": 2196, "category": "电器电子", "desc": "Maxell 金霸王 AA 五号碱性电池"},
  {"id": 2197, "category": "电器电子", "desc": "Maxell 9V 碱性电池"},
  {"id": 2198, "category": "电器电子", "desc": "Maxell D型一号碱性电池"},
  {"id": 2199, "category": "电器电子", "desc": "Maxell C型二号碱性电池"},
  {"id": 2200, "category": "餐饮用品", "desc": "Bombillas 阿根廷金属吸管（马黛茶吸管）"},
  {"id": 2201, "category": "派对用品", "desc": "Parafina 蛋糕蜡烛及红色点火器"},
  {"id": 2202, "category": "玩具游戏", "desc": "彩色玻璃弹珠"},
  {"id": 2203, "category": "食品饮料", "desc": "Star 牌瓶装饮用水"},
  {"id": 2204, "category": "食品饮料", "desc": "Star 牌瓶装饮用水"},
  {"id": 2205, "category": "美妆个护", "desc": "TRIM 美国指甲钳"},
  # batch-3
  {"id": 2206, "category": "美妆个护", "desc": "TRIM品牌美式指甲刀套装，盒装展示"},
  {"id": 2207, "category": "美妆个护", "desc": "TRIM品牌指甲刀，透明罐装"},
  {"id": 2208, "category": "美妆个护", "desc": "TRIM品牌脚趾甲刀，透明罐装"},
  {"id": 2209, "category": "日用百货", "desc": "llamita牌木杆火柴，三瓶装"},
  {"id": 2210, "category": "玩具游戏", "desc": "网袋装彩色玻璃弹珠"},
  {"id": 2211, "category": "玩具游戏", "desc": "各色玻璃弹珠袋装组合"},
  {"id": 2212, "category": "玩具游戏", "desc": "25mm彩色弹珠及充气玩具组合包装"},
  {"id": 2213, "category": "美妆个护", "desc": "MAKAO牌剃须刷套装"},
  {"id": 2214, "category": "餐饮用品", "desc": "独立包装塑料小叉子/搅拌棒"},
  {"id": 2215, "category": "个人防护", "desc": "adhesur牌创可贴/保护性敷料盒装"},
  # batch-5
  {"id": 2226, "category": "卫浴用品", "desc": "Yanina 蓝色球形洁厕/除味块，整版挂卡包装"},
  {"id": 2227, "category": "五金工具", "desc": "Tres Patitos 家用硅酮喷雾，用于家电维修保养"},
  {"id": 2228, "category": "日用百货", "desc": "Tres Estrellas 抽纸，400张大包装"},
  {"id": 2229, "category": "厨房炊具", "desc": "BROGAS 便携丁烷气罐（带安全接头），用于户外炉具"},
  {"id": 2230, "category": "厨房炊具", "desc": "Llamita 小型丁烷气罐补充装，便携炉具燃料"},
  {"id": 2231, "category": "厨房炊具", "desc": "Llamita 瓶装丁烷气体，便携炉具燃料"},
  {"id": 2232, "category": "个人防护", "desc": "IQP 10x10cm 无菌医用纱布片，5片装"},
  {"id": 2233, "category": "美妆个护", "desc": "塑料包装小瓶装液体产品，疑似个人护理分装瓶"},
  {"id": 2234, "category": "美妆个护", "desc": "Super-Max Platinum 双刃安全剃须刀片"},
  {"id": 2235, "category": "日用百货", "desc": "Sanaturm 床垫保护套/床罩，带印花包装"}
]

with open('D:/projects/supplier_crawler/diego_wave1_partial.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"已保存 {len(results)} 条结果到 diego_wave1_partial.json")
