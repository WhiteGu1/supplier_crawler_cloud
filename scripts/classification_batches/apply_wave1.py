import pymysql, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# 第一波全部80条结果 (batch 0-7)
all_results = [
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
  # batch-4
  {"id": 2216, "category": "个人防护", "desc": "Curitas弹性绷带，用于割伤烫伤急救包扎"},
  {"id": 2217, "category": "日用百货", "desc": "Candela黑色一次性打火机展示装"},
  {"id": 2218, "category": "日用百货", "desc": "Candela Rainbow彩色打火机展示装"},
  {"id": 2219, "category": "日用百货", "desc": "Candela打火机吸塑挂装，多色款"},
  {"id": 2220, "category": "餐饮用品", "desc": "Candela Clásico长柄厨房点火器"},
  {"id": 2221, "category": "日用百货", "desc": "Candela Flex彩色塑料打火机"},
  {"id": 2222, "category": "日用百货", "desc": "Candela打火机，白/黄/绿色款"},
  {"id": 2223, "category": "日用百货", "desc": "BIC Maxi一次性打火机多色套装"},
  {"id": 2224, "category": "日用百货", "desc": "BIC Mini迷你一次性打火机多色套装"},
  {"id": 2225, "category": "日用百货", "desc": "Candela彩色打火机零售展示盒"},
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
  {"id": 2235, "category": "日用百货", "desc": "Sanaturm 床垫保护套/床罩，带印花包装"},
  # batch-6
  {"id": 2236, "category": "美妆个护", "desc": "BIC Sensitive 剃须刀片替换装"},
  {"id": 2237, "category": "美妆个护", "desc": "BIC Twin Select 剃须刀片双刃装"},
  {"id": 2238, "category": "美妆个护", "desc": "Gillette PlatinuS 双刃剃须刀片"},
  {"id": 2239, "category": "美妆个护", "desc": "蓝色礼盒装男士安全剃须刀"},
  {"id": 2240, "category": "个人防护", "desc": "OFF! 家用驱蚊喷雾6小时长效"},
  {"id": 2241, "category": "日用百货", "desc": "Elite 三层加厚纸巾便携装6包"},
  {"id": 2242, "category": "文具办公", "desc": "MaKAO 蓝色按动中性笔套装"},
  {"id": 2243, "category": "文具办公", "desc": "编号685自粘性数字标签贴纸"},
  {"id": 2244, "category": "文具办公", "desc": "VON 绿色按动中性笔套装"},
  {"id": 2245, "category": "婴幼儿用品", "desc": "迪士尼卡通儿童学饮杯训练杯"},
  # batch-7
  {"id": 2246, "category": "厨房餐具", "desc": "Tramontina 6件套不锈钢勺子，橙色木质手柄"},
  {"id": 2247, "category": "厨房餐具", "desc": "Tramontina 6件套牛排刀，橙色木质手柄"},
  {"id": 2248, "category": "厨房餐具", "desc": "Tramontina 6件套不锈钢叉子，木质手柄"},
  {"id": 2249, "category": "厨房餐具", "desc": "Tramontina New Kolor 12件套不锈钢勺子，黑色手柄"},
  {"id": 2250, "category": "厨房餐具", "desc": "Tramontina New Kolor 大号不锈钢勺子，黑色手柄"},
  {"id": 2251, "category": "厨房餐具", "desc": "Tramontina New Kolor 12件套牛排刀，黑色手柄"},
  {"id": 2252, "category": "厨房餐具", "desc": "Tramontina New Kolor 12件套不锈钢叉子，黑色手柄"},
  {"id": 2253, "category": "厨房餐具", "desc": "KAR OPEN 红黑色手柄开罐器"},
  {"id": 2254, "category": "厨房餐具", "desc": "NANSHENG 红色波浪防护开罐器/开瓶器"},
  {"id": 2255, "category": "清洁用品", "desc": "GANGAPRO 加厚垃圾袋 10只装 43x65cm"},
]

# 第二波已完成的部分 (batch-8,9,12)
wave2_partial = [
  # batch-8
  {"id": 2256, "category": "清洁用品", "desc": "ganga 黑色垃圾袋 45x60cm 10只装"},
  {"id": 2257, "category": "清洁用品", "desc": "ganga 黑色垃圾袋 50x70cm 10只装"},
  {"id": 2258, "category": "清洁用品", "desc": "ganga 黑色垃圾袋 60x90cm 10只装"},
  {"id": 2259, "category": "清洁用品", "desc": "ganga 黑色垃圾袋 80x110cm 10只装"},
  {"id": 2260, "category": "清洁用品", "desc": "ganga 黑色垃圾袋 90x120cm 10只装"},
  {"id": 2261, "category": "日用百货", "desc": "ganga 三卷装彩色线绳/打包绳（红、黑、蓝）"},
  {"id": 2262, "category": "日用百货", "desc": "木质晾衣夹/木夹子"},
  {"id": 2263, "category": "日用百货", "desc": "BROCHE 塑料夹子 12只装"},
  {"id": 2264, "category": "装饰品", "desc": "绿色花园围栏/草坪装饰边栏配金属夹"},
  {"id": 2265, "category": "装饰品", "desc": "CORTINA DANFORT 窗帘挂钩/窗帘配件 0.80x2.00m"},
  # batch-9
  {"id": 2266, "category": "厨房储物", "desc": "透明塑料鸡蛋收纳盒，带分隔设计"},
  {"id": 2267, "category": "清洁用品", "desc": "make品牌黄色百洁布/清洁海绵"},
  {"id": 2268, "category": "清洁用品", "desc": "Steff品牌黄色橡胶清洁手套"},
  {"id": 2269, "category": "清洁用品", "desc": "BIE-POL抗蛀丸（防虫防蛀球）"},
  {"id": 2270, "category": "清洁用品", "desc": "红色塑料苍蝇拍（电蚊拍式）"},
  {"id": 2271, "category": "餐饮用品", "desc": "一次性竹制烧烤签/食品级竹签"},
  {"id": 2272, "category": "文具办公", "desc": "Gommaoca 12mm白色粉笔"},
  {"id": 2273, "category": "文具办公", "desc": "Gommaoca 10mm红色彩色粉笔"},
  {"id": 2274, "category": "文具办公", "desc": "Gommaoca 5mm棕色细彩色粉笔"},
  {"id": 2275, "category": "餐饮用品", "desc": "红色多功能红酒开瓶器/酒刀"},
  # batch-12
  {"id": 2296, "category": "美妆个护", "desc": "El Mono品牌黑色合成发辫/发束"},
  {"id": 2297, "category": "美妆个护", "desc": "El Mono品牌白色合成发辫/发束"},
  {"id": 2298, "category": "美妆个护", "desc": "El Mono品牌彩色(彩虹)合成发辫/发束"},
  {"id": 2299, "category": "美妆个护", "desc": "El Mono品牌棕色合成发辫/发束"},
  {"id": 2300, "category": "美妆个护", "desc": "El Mono品牌黑色合成发辫/发束"},
  {"id": 2301, "category": "箱包配件", "desc": "Guapa Guapa品牌连裤袜/丝袜"},
  {"id": 2302, "category": "鞋履护理", "desc": "Macao品牌棕色鞋油(罐装)"},
  {"id": 2303, "category": "鞋履护理", "desc": "Macao品牌黑色鞋油(罐装)"},
  {"id": 2304, "category": "鞋履护理", "desc": "Wassington品牌白色鞋油膏(Crema Blanca)"},
  {"id": 2305, "category": "鞋履护理", "desc": "Wassington品牌无色鞋油膏(Pomada Incolora)"},
]

all_results.extend(wave2_partial)

# 写入数据库
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

updated = 0
for r in all_results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount

conn.commit()
print(f"成功更新 {updated}/{len(all_results)} 条商品分类")

# 查看当前进度
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=2 AND is_available=1 AND (category IS NULL OR category='' OR category='未分类')")
remaining = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=2 AND is_available=1")
total = cur.fetchone()[0]
print(f"Diego 进度: {total - remaining}/{total} 已分类, {remaining} 待分类")

conn.close()
