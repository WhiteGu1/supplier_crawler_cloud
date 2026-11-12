"""
Trapoman 全量人工审查分类 — 1107 条
逐条根据商品名称判断实际品类，不做关键词批量匹配。
对名称歧义或无法判断的，标记 NEEDS_IMAGE。
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# 逐条人工审查分类
# 格式: (product_id, category)
# 审查原则：看商品名称判断它到底是什么，而不是关键词匹配
# ═══════════════════════════════════════════════════════════════

CLASSIFICATIONS = [
    # 1-13: 香薰炉/树脂 — 都是焚香用品
    (15273, '装饰品'),   # SAHUMERIO SLIM TIBETANO X10 — 香薰炉
    (15274, '装饰品'),   # SAHUMERIO ELIXIR X5 — 香薰炉
    (15275, '装饰品'),   # RESINAS MAGISTRALES — 焚香树脂
    (15276, '装饰品'),   # SAHUMERIO LINEA YOGA AROMANZA — 香薰炉
    (15277, '装饰品'),   # SAHUMERIO HEXAGONAL LINEA BLANCA — 香薰炉
    (15278, '装饰品'),   # SAHUMERIOS TRIO AROMANZA INDIA — 香薰炉
    # 7-13: 蜡烛
    (15279, '装饰品'),   # VELA NOCHE BLANCA X6 — 夜灯蜡烛
    (15280, '装饰品'),   # VELA NOCHE SURTIDAS X12 — 蜡烛
    (15281, '装饰品'),   # VELA NOCHE BLANCA X12 — 蜡烛
    (15282, '装饰品'),   # VELONCITO CON CELOFAN X12 — 小蜡烛
    (15283, '装饰品'),   # VELA NOCHE AROMATICA X6 — 香薰蜡烛
    (15284, '装饰品'),   # VELONCITO AROMATICO X3 — 香薰小蜡烛
    (15285, '收纳整理'),  # RECIPIENTE GIGANTE 40 LTS — 巨型收纳容器

    # 14-16: 烧烤/点火用品
    (17503, '厨房炊具'),  # CHISPERO MAXI PARTY — 烧烤点火器
    (17504, '厨房炊具'),  # CHISPERO BARBECUE — 烧烤点火器
    (17505, '厨房炊具'),  # ENCENDEDOR MINI TORCH — 迷你喷枪点火器

    # 17-20: 清洁工具
    (17506, '清洁用品'),  # BALDE OVAL 14 LTS — 水桶
    (17507, '清洁用品'),  # ESCOBILLA FINITA PUNTA SILICONA — 刷子
    (17508, '清洁用品'),  # SUPER ESCOBILLA CON DEPOSITO CRYSTAL — 刷子
    (17509, '清洁用品'),  # ESPONJA GO! POWER — 海绵

    # 21-52: SAN REMO 密封罐系列 — 全部是食品储存容器
    (17510, '厨房储物'),  # HERMETICO RECTANGULAR 1600 ML
    (17511, '厨房储物'),  # HERMETICO RECTANGULAR CON DIV 1600 ML
    (17512, '厨房储物'),  # HERMETICO RECTANGULAR 2000 ML
    (17513, '厨房储物'),  # HERMETICO RECTANGULAR 2500 ML
    (17514, '厨房储物'),  # HERMETICO RECTANGULAR 3500 ML
    (17515, '厨房储物'),  # SET X3 HERMETICOS RECTANGULAR
    (17516, '厨房储物'),  # HERMETICO REDONDO 230 ML
    (17517, '厨房储物'),  # HERMETICO REDONDO 440 ML
    (17518, '厨房储物'),  # HERMETICO REDONDO 620 ML
    (17519, '厨房储物'),  # HERMETICO REDONDO 680 ML
    (17520, '厨房储物'),  # HERMETICO REDONDO 1.3 LTS
    (17521, '厨房储物'),  # HERMETICO RECTANGULAR 330 ML
    (17522, '厨房储物'),  # HERMETICO RECTANGULAR 537 ML
    (17523, '厨房储物'),  # HERMETICO RECTANGULAR 770 ML
    (17524, '厨房储物'),  # HERMETICO RECTANGULAR 820 ML
    (17525, '厨房储物'),  # HERMETICO RECTANGULAR ALTO 1400 ML
    (17526, '厨房储物'),  # HERMETICO CUADRADO 200 ML
    (17527, '厨房储物'),  # HERMETICO CUADRADO 360 ML
    (17528, '厨房储物'),  # HERMETICO CUADRADO 530 ML
    (17529, '厨房储物'),  # HERMETICO CUADRADO 1.9 ML (实际1.9L)
    (17530, '厨房储物'),  # HERMETICO CUADRADO ALTO 800 ML
    (17531, '厨房储物'),  # HERMETICO CUADRADO ALTO 1.7 LTS
    (17532, '厨房储物'),  # HERMETICO RECTANGULAR 280 ML
    (17533, '厨房储物'),  # HERMETICO RECTANGULAR 580 ML
    (17534, '厨房储物'),  # HERMETICO RECTANGULAR 785 ML
    (17535, '厨房储物'),  # HERMETICO RECTANGULAR 1.4 LTS
    (17536, '厨房储物'),  # HERMETICO RECTANGULAR 1.8 LTS
    (17537, '厨房储物'),  # HERMETICO RECTANGULAR 3.2 LTS
    (17538, '厨房储物'),  # SET SAN REMO X4 RECTANGULAR
    (17539, '厨房储物'),  # SET SAN REMO X5 RECTANGULAR
    (17540, '厨房储物'),  # SET SAN REMO X6 RECTANGULAR
    (17541, '厨房储物'),  # SET SAN REMO X8 RECTANGULAR

    # 53-55: 厨具
    (17542, '厨房炊具'),  # SANDWICHERA SAN REMO — 三明治机
    (17543, '厨房炊具'),  # SANDWICHERA DOBLE SAN REMO — 双三明治机
    (17544, '厨房储物'),  # SET HERMETICOS VERDURAS X3 — 蔬菜密封罐

    # 56-62: 收纳/洗衣
    (17545, '清洁用品'),  # ORGANIZADOR DE LIMPIEZA — 清洁收纳
    (17546, '收纳整理'),  # CANASTO ROPA 3 COLORES — 脏衣篮
    (17547, '收纳整理'),  # CAJON COSECHERO NEGRO — 收纳箱
    (17548, '收纳整理'),  # CANASTO BASKET CON RAYAS GRANDE — 篮子
    (17549, '收纳整理'),  # CANASTITO BASKET CON RAYAS CHICO — 小篮子
    (17550, '收纳整理'),  # CAJONCITO ORGANIZADOR NEGRO — 收纳盒
    (17551, '厨房炊具'),  # SARTEN 2 CIRCULOS — 煎蛋锅
    (17552, '厨房炊具'),  # SARTEN 4 CIRCULOS — 煎蛋锅

    # 64-72: 烘焙模具/厨房工具
    (17553, '厨房炊具'),  # ASADERA RECT CAROL ANTIADHERENTE — 烤盘
    (17554, '厨房炊具'),  # MOLDE DESMONTABLE CON TRABA 24 CM — 活底蛋糕模
    (17555, '厨房储物'),  # TARRO YERBA NEGRO PREMIUM — 马黛茶罐
    (17556, '厨房储物'),  # TARRO AZUCAR NEGRO PREMIUM — 糖罐
    (17557, '厨房储物'),  # TARRO CAFE NEGRO PREMIUM — 咖啡罐
    (17558, '厨房储物'),  # TARRO PARA TE NEGRO PREMIUM — 茶罐
    (17559, '厨房储物'),  # TARRO GALLETITAS NEGRO PREMIUM — 饼干罐
    (17560, '厨房储物'),  # TARRO FIDEOS NEGRO PREMIUM — 面条罐
    (17561, '厨房储物'),  # TARRO PARA PAN NEGRO PREMIUM — 面包罐
    (17562, '厨房炊具'),  # MOLDE PAN LACTAL SAN REMO — 吐司模具

    # 73-76: 刀具套装
    (17563, '厨房餐具'),  # SET 5 CUCHILLAS ACERO CON TACO Y SOPORTE — 刀具套装+刀座
    (17564, '厨房餐具'),  # SET 5 CUCHILLAS ACERO CON TACO IMANTADO — 磁力刀座套装
    (17565, '厨房餐具'),  # SET 5 CUCHILLAS ACERO + TIJERA Y TACO — 刀具+剪刀套装

    # 77-86: 厨房工具（勺子、铲子等）
    (17566, '厨房餐具'),  # RALLADOR QUESO Y NUTS — 奶酪/坚果擦丝器
    (17567, '厨房餐具'),  # CUCHARA GUISO ACERO MANGO SILICONA — 炖勺
    (17568, '厨房餐具'),  # ESPUMADERA ACERO MANGO SILICONA — 漏勺
    (17569, '厨房餐具'),  # CUCHARON ACERO MANGO SILICONA — 汤勺
    (17570, '厨房餐具'),  # ESPATULA ACERO MANGO SILICONA — 铲子
    (17571, '厨房餐具'),  # CUCHARA PASTA ACERO MANGO SILICONA — 意面勺
    (17572, '厨房餐具'),  # EXPRIMIDOR LIMON ACERO — 柠檬榨汁器
    (17573, '厨房餐具'),  # BATE BIFE METAL — 牛肉拍
    (17574, '厨房餐具'),  # PICA AJO ACERO — 压蒜器
    (17575, '厨房餐具'),  # HUEVERA X12 SAN REMO — 蛋架
    (17576, '厨房餐具'),  # CUBIERTERO METAL 4 COMPARTIMIENTOS — 餐具架
    (17577, '厨房餐具'),  # CUBIERTERO SAN REMO — 餐具架
    (17578, '厨房餐具'),  # PORTA ROLLO NEGRO METALICO — 厨房纸架

    # 79-81: 玻璃器皿
    (17579, '餐饮用品'),  # TAZA DOBLE VIDRIO 80ML — 双层玻璃杯
    (17580, '餐饮用品'),  # FRUTERA VIDRIO DELI GLASS — 水果碗
    (17581, '餐饮用品'),  # FUENTE CRISTAL DELI SOGA — 玻璃餐盘
    (17582, '餐饮用品'),  # VASO 250 ML DELI GLASS PACK X6 — 玻璃杯6装
    (17583, '餐饮用品'),  # VASO 325 ML DELI GLASS PACK X6
    (17584, '餐饮用品'),  # VASO 450 ML DELI GLASS PACK X6
    (17585, '餐饮用品'),  # VASO MUG FEST KEEP — 马克杯
    (17586, '餐饮用品'),  # BOTELLA INSULADA CON MANGO 650 ML — 保温瓶
    (17587, '餐饮用品'),  # BOTELLON INSULADO CON MANGO 850 ML — 大保温瓶
    (17588, '餐饮用品'),  # BOTELLA INSULADA FLASK 720 ML — 保温瓶
    (17589, '餐饮用品'),  # BOTELLA JUGO KIDO KEEP 250 ML — 儿童果汁瓶
    (17590, '餐饮用品'),  # BOTELLA KIDO KEEP 400 ML — 儿童保温瓶
    (17591, '餐饮用品'),  # BOTELLA METALICA KIDO KEEP 335 ML — 儿童金属瓶
    (17592, '餐饮用品'),  # BOTELLA KEEP FRANJA COLORES — 保温瓶
    (17593, '餐饮用品'),  # BOTELLA 1 LT KEEP — 保温瓶
    (17594, '餐饮用品'),  # BOTELLA DAILY 2 LTS KEEP — 水壶
    (17595, '餐饮用品'),  # BOTELLA VIDRIO CON GANCHO 470 ML — 玻璃瓶
    (17596, '餐饮用品'),  # BOTELLA VIDRIO INFUSOR EN CAJITA — 果茶 infusion 瓶
    (17597, '餐饮用品'),  # BOTELLA METALICA 600 ML KEEP — 保温瓶
    (17598, '餐饮用品'),  # PACK TAZA CAPUCCINO X 6 — 卡布奇诺杯套装
    (17599, '餐饮用品'),  # MUG METALICO KEEP 450 ML — 金属马克杯
    (17600, '餐饮用品'),  # MUG PRIME KEEP 540 ML — 马克杯
    (17601, '餐饮用品'),  # MUG TERMICO KEEP 1180 ML — 大保温杯
    (17602, '餐饮用品'),  # VASO TE 450ML KEEP — 茶杯
    (17603, '餐饮用品'),  # JARRA CUADRADA CON CUBIERTOS GRIS — 带餐具方壶
    (17604, '厨房餐具'),  # JUEGO CUBIERTOS TIZA EN TUBO — 餐具套装
    (17605, '餐饮用品'),  # JARRA CUADRADA CON CUBIERTOS TIZA — 带餐具方壶
    (17606, '餐饮用品'),  # JARRA CUADRADA CON CUBIERTOS NEGRO — 带餐具方壶

    # 118-119: 餐垫
    (17607, '餐饮用品'),  # INDIVIDUAL MULTIUSO GOMA EVA — 餐垫
    (17608, '餐饮用品'),  # SET X6 INDIVIDUAL ANTIDESLIZANTE — 防滑餐垫套装

    # 120-124: 浴室/伞
    (17609, '装饰品'),    # FLORERO VIDRIO DELI SOGA — 花瓶
    (17610, '卫浴用品'),  # ORGANIZADOR DUCHA CRYSTAL — 淋浴收纳
    (17611, '日用百货'),  # PARAGUA MINI AUTOMATICO — 迷你伞
    (17612, '卫浴用品'),  # ORGANIZADOR DE DUCHA DOBLE ESTANTE — 双层淋浴架
    (17613, '装饰品'),    # VELA NOCHE BLANCA X6 ILUMINARTE — 蜡烛

    # 125-131: 卫浴用品
    (17614, '卫浴用品'),  # PORTA CEPILLO DE DIENTES SAN REMO — 牙刷架
    (17615, '卫浴用品'),  # PORTA JABON EN POLVO SAN REMO — 洗衣粉盒
    (17616, '卫浴用品'),  # ALFOMBRA BAÑO MEMORY — 浴室垫
    (17617, '卫浴用品'),  # DISPENSER JABON VIDRIO — 皂液器
    (17618, '卫浴用品'),  # DISPENSER PLASTICO COLORES SURTIDOS — 皂液器
    (17619, '卫浴用品'),  # DISPENSER JABON VIDRIO ONDULADO — 皂液器
    (17620, '卫浴用品'),  # DISPENSER JABON COLOR — 皂液器

    # 132-148: 保温瓶/马黛茶具
    (17621, '餐饮用品'),  # TERMO BALA 1 LT KEEP — 保温瓶
    (17622, '餐饮用品'),  # TERMO ERGO 500 ML KEEP — 保温瓶
    (17623, '餐饮用品'),  # TERMO MANGO 1 LT KEEP — 保温瓶
    (17624, '餐饮用品'),  # TERMO HAMMERED 1.5 LTS KEEP — 保温瓶
    (17625, '餐饮用品'),  # SET MATE + TERMO BALA 500 CC — 马黛茶套装
    (17626, '餐饮用品'),  # TERMO COFFEE MUG KEEP — 保温咖啡杯
    (17627, '餐饮用品'),  # LUNCHERA TERMICA KEEP 450 ML — 保温饭盒
    (17628, '餐饮用品'),  # LUNCHERA TERMICA KEEP 600 ML — 保温饭盒
    (17629, '餐饮用品'),  # AUTOCEBANTE KEEP — 自注水马黛茶
    (17630, '餐饮用品'),  # MATE + BOMBILLA EN BLISTER — 马黛茶杯
    (17631, '餐饮用品'),  # SET 3 VASOS KIDO KEEP 300 ML — 儿童杯套装

    # 149-162: 厨房储物/炊具
    (17632, '厨房炊具'),  # BOLSA PARA HORNO FREZZ ORM — 烤箱袋
    (17633, '日用百货'),  # PASTILLERO SAN REMO — 药盒
    (17634, '日用百货'),  # PASTILLERO + ORGANIZADOR SAN REMO — 药盒+收纳
    (17635, '厨房储物'),  # HERMETICO CUADRADO 800 ML SAN REMO FACIL
    (17636, '厨房储物'),  # SET SAN REMO FACIL X3
    (17637, '厨房储物'),  # SET SAN REMO FACIL X3
    (17638, '厨房储物'),  # SET SAN REMO FACIL X3
    (17639, '收纳整理'),  # CANASTO CON RUEDAS TAPA CORAZON 40 LTS — 带轮收纳篮
    (17640, '餐饮用品'),  # TAZON SUPER MAGIC — 碗
    (17641, '餐饮用品'),  # BANDEJA REDONDA GRANDE — 大圆托盘
    (17642, '厨房炊具'),  # ASADERA RECT CAROL ANTIADHERENTE 35X24 — 烤盘
    (17643, '厨房炊具'),  # BUDINERA CAROL ANTIADHERENTE — 吐司模具
    (17644, '厨房炊具'),  # PASTAFROLA REDONDA FIJO N22 — 派盘
    (17645, '厨房炊具'),  # PASTAFROLA REDONDA DESFONDABLE N22 — 活底派盘
    (17646, '厨房炊具'),  # PASTAFROLA REDONDA FIJO N24
    (17647, '厨房炊具'),  # PASTAFROLA REDONDA DESFONDABLE N24
    (17648, '厨房炊具'),  # PASTAFROLA REDONDA FIJO N26
    (17649, '厨房炊具'),  # PASTAFROLA REDONDA DESFONDABLE N26
    (17650, '厨房炊具'),  # TORTERA ESTRELLA REDONDA NUPCIAL — 星形蛋糕模

    # 163-178: 厨房工具
    (17651, '厨房餐具'),  # PIEDRA AFILADORA — 磨刀石
    (17652, '厨房餐具'),  # TAMIZADOR — 筛子
    (17653, '厨房餐具'),  # ESPUMADERA ACERO LOEKEMEYER — 漏勺
    (17654, '厨房餐具'),  # SILICONE UTENSILLS SET — 硅胶厨具套装
    (17655, '厨房餐具'),  # SACACORCHO ACERO REFORZADO — 开瓶器
    (17656, '厨房餐具'),  # ABRELATA ACERO REFORZADO — 开罐器
    (17657, '厨房餐具'),  # CORTA PIZZA ACERO REFORZADO — 披萨刀
    (17658, '厨房餐具'),  # PELAPAPAS GIRATORIO ACERO — 旋转削皮器
    (17659, '厨房餐具'),  # CUCHARA HELADO ACERO — 冰淇淋勺
    (17660, '厨房餐具'),  # CUCHILLO UNTADOR CAROL X4 — 黄油刀4件
    (17661, '厨房餐具'),  # PORTA ROLLO ACERO 2 ASAS — 厨房纸架
    (17662, '餐饮用品'),  # HIELERA ACERO — 冰桶
    (17663, '餐饮用品'),  # JARRO PREMIUM DOBLE PLASTICO — 双层塑料壶
    (17664, '厨房餐具'),  # PACK 16 CUBIERTOS GRIS TRAMADO ECO — 16件餐具
    (17665, '厨房餐具'),  # PACK 16 CUBIERTOS NEGRO TRAMADO ECO
    (17666, '厨房餐具'),  # PACK 16 CUBIERTOS TIZA TRAMADO ECO
    (17667, '厨房餐具'),  # JUEGO CUBIERTOS NEGRO EN TUBO
    (17668, '厨房餐具'),  # JUEGO CUBIERTOS GRIS EN TUBO

    # 179-188: 衣架/浴室/清洁
    (17669, '收纳整理'),  # PERCHA TERCIOPELO BLANCA — 丝绒衣架
    (17670, '收纳整理'),  # PERCHA TERCIOPELO GRIS
    (17671, '收纳整理'),  # PERCHA TERCIOPELO NEGRA
    (17672, '装饰品'),    # ESPEJO 56X45 OVALADO — 镜子
    (17673, '收纳整理'),  # BARRAL LUJO GRUESO BLANCO — 毛巾杆
    (17674, '收纳整理'),  # BARRAL FINO BLANCO — 毛巾杆
    (17675, '收纳整理'),  # BARRAL ALUMINIO — 毛巾杆
    (17676, '清洁用品'),  # ALFOMBRA SECADO RAPIDO GOMA — 快干地垫
    (17677, '宠物用品'),  # BOLSITA PARA MASCOTA — 宠物袋

    # 189-243: SAN REMO 密封罐重复款（/6 表示6装）
    (17719, '厨房储物'),  # HERMETICO REDONDO 230 ML (/6)
    (17720, '厨房储物'),  # HERMETICO REDONDO 440 ML (/6)
    (17721, '厨房储物'),  # HERMETICO REDONDO 620 ML (/6)
    (17722, '厨房储物'),  # HERMETICO REDONDO 680 ML (/6)
    (17723, '厨房储物'),  # HERMETICO REDONDO 1.3 LTS (/6)
    (17724, '厨房储物'),  # HERMETICO CUADRADO 200 ML (/6)
    (17725, '厨房储物'),  # HERMETICO CUADRADO 360 ML (/6)
    (17726, '厨房储物'),  # HERMETICO CUADRADO 530 ML (/6)
    (17727, '厨房储物'),  # HERMETICO CUADRADO 1.9 ML (/6)
    (17728, '厨房储物'),  # HERMETICO CUADRADO ALTO 800 ML (/6)
    (17729, '厨房储物'),  # HERMETICO CUADRADO ALTO 1.7 LTS (/6)
    (17730, '厨房储物'),  # HERMETICO RECTANGULAR 280 ML (/6)
    (17731, '厨房储物'),  # HERMETICO RECTANGULAR 580 ML (/6)
    (17732, '厨房储物'),  # HERMETICO RECTANGULAR 785 ML (/6)
    (17733, '厨房储物'),  # HERMETICO RECTANGULAR 1.4 LTS (/6)
    (17734, '厨房储物'),  # HERMETICO RECTANGULAR 1.8 LTS (/6)
    (17735, '厨房储物'),  # HERMETICO RECTANGULAR 3.2 LTS (/6)
    (17736, '厨房储物'),  # HERMETICO CUADRADO 800 ML FACIL (/6)

    # 207-243: Carol 餐具（逐条审查）
    (17737, '厨房餐具'),  # CUCHARITA TRAMADA ECO X12 TIZA — 茶匙12件
    (17738, '厨房餐具'),  # CUCHARA TRAMADA ECO X12 TIZA — 汤匙12件
    (17739, '厨房餐具'),  # TENEDOR TRAMADO ECO X12 TIZA — 叉子12件
    (17740, '厨房餐具'),  # CUCHILLO TRAMADO ECO X12 TIZA — 刀12件
    (17741, '厨房餐具'),  # CUCHARITA TE X12 BEIGE — 茶匙
    (17742, '厨房餐具'),  # CUCHARA X12 BEIGE
    (17743, '厨房餐具'),  # TENEDOR X12 BEIGE
    (17744, '厨房餐具'),  # CUCHILLO X12 BEIGE
    (17745, '厨房餐具'),  # ESPATULA CALADA ACERO MANGO SILICONA — 打孔铲
    (17746, '厨房餐具'),  # ESPATULA REPOSTERA ACERO MANGO SILICONA — 糕点铲
    (17747, '厨房餐具'),  # BATEDOR ACERO MANGO SILICONA — 打蛋器
    (17748, '厨房餐具'),  # SET CAROL ACERO Y SILICONA 7 PIEZAS — 厨具7件套
    (17749, '厨房餐具'),  # BATIDOR DE ACERO — 打蛋器
    (17750, '厨房餐具'),  # CORNET ACERO CON MEDIDAS — 裱花袋
    (17751, '厨房餐具'),  # RALLADOR NEGRO 4 CARAS 23 CM — 四面擦丝器
    (17752, '厨房餐具'),  # RALLADOR NEGRO 4 CARAS 25 CM
    (17753, '厨房餐具'),  # EXPRIMIDOR CON BASE CAROL — 榨汁器
    (17754, '厨房餐具'),  # SALERO/PIMENTERO VIDRIO — 盐椒瓶
    (17755, '厨房餐具'),  # CUCHARA ACERO PREMIUM X6 — 汤匙6件
    (17756, '厨房餐具'),  # TENEDOR ACERO PREMIUM X6
    (17757, '厨房餐具'),  # CUCHILLO ACERO PREMIUM X6
    (17758, '厨房餐具'),  # CUCHARITA ACERO PREMIUM X6
    (17759, '厨房餐具'),  # UNTADOR ACERO PREMIUM X6 — 黄油刀
    (17760, '厨房餐具'),  # PACK CUBIERTOS ACERO INOXIDABLE X16 NEGRO
    (17761, '厨房餐具'),  # PACK CUBIERTOS ACERO INOXIDABLE X16 COBRE
    (17762, '厨房餐具'),  # PACK CUBIERTOS ACERO INOXIDABLE X16 NEGRO
    (17763, '厨房餐具'),  # CUBIERTOS ACERO P/NIÑOS — 儿童餐具
    (17764, '厨房餐具'),  # JUEGO CUBIERTOS BEIGE EN TUBO
    (17765, '收纳整理'),  # GANCHOS ADHESIVOS X6 — 粘钩
    (17766, '清洁用品'),  # CEPILLO DE LIMPIEZA BAMBU — 竹清洁刷
    (17767, '清洁用品'),  # CEPILLO DE LIMPIEZA BAMBU
    (17768, '清洁用品'),  # CEPILLO DE LIMPIEZA BAMBU
    (17769, '清洁用品'),  # CEPILLO DE LIMPIEZA BAMBU
    (17770, '清洁用品'),  # CEPILLO DE LIMPIEZA BAMBU
    (17771, '清洁用品'),  # CEPILLO DE LIMPIEZA BAMBU
    (17772, '清洁用品'),  # LIMPIA VIDRIO BAMBU — 玻璃清洁刷
    (17773, '派对用品'),  # PACK MUNDIAL GORRO+CORNETA+BANDERITA+MAQUILLAJE — 世界杯派对套装
    (17774, '厨房餐具'),  # ABRELATA UÑA BENABI — 开罐器
    (17775, '厨房餐具'),  # BATIDOR DE COLORES — 打蛋器
    (17776, '餐饮用品'),  # TAPON CON CAJITA PARA TERMO — 保温瓶塞
    (17777, '厨房餐具'),  # PACK 16 CUBIERTOS BEIGE TRAMADO ECO

    # 248-336: 各种厨房/家居用品
    (18013, '厨房炊具'),  # ENCENDEDOR VIP GOLD — 打火机（厨房用）
    (18014, '收纳整理'),  # CESTO VAIVEN INFANTIL — 儿童收纳篮
    (18015, '清洁用品'),  # CEPILLO LAVADO CON SILICONA — 洗刷
    (18016, '厨房储物'),  # PACK HERMETICOS DESCARTABLE MAKE — 一次性密封罐
    (18017, '厨房餐具'),  # AZUCARERA TAPA BAMBU PLUS — 糖罐
    (18018, '厨房储物'),  # FRASCO TAPA NEGRA NUM 1 ACERO PLUS — 钢罐
    (18019, '厨房储物'),  # FRASCO TAPA NEGRA NUM 2 ACERO PLUS
    (18020, '厨房储物'),  # FRASCO TAPA NEGRA NUM 3 ACERO PLUS
    (18021, '厨房储物'),  # FRASCO VIDRIO TAPA ACERO S — 玻璃罐
    (18022, '厨房储物'),  # FRASCO VIDRIO TAPA ACERO M
    (18023, '厨房储物'),  # FRASCO VIDRIO TAPA ACERO L
    (18024, '厨房储物'),  # FRASCO VIDRIO TAPA ACERO XL
    (18025, '厨房餐具'),  # SET CUCHILLOS EREASTHQS — 刀具套装
    (18026, '厨房餐具'),  # ESPIRAL DE VERDURA — 蔬菜切丝器
    (18027, '厨房餐具'),  # RALLADOR ACERO PLUS — 擦丝器
    (18028, '厨房餐具'),  # COLADOR ACERO PLUS — 滤网
    (18029, '厨房餐具'),  # PISAPAPA ACERO PLUS — 土豆泥器
    (18030, '厨房餐具'),  # PALA TORTA ACERO PLUS — 蛋糕铲
    (18031, '厨房餐具'),  # FILTRO TE ACERO PLUS — 茶滤
    (18032, '厨房餐具'),  # PINZA SILICONA CHICA ACERO PLUS — 小夹子
    (18033, '厨房餐具'),  # PINZA SILICONA GRANDE ACERO PLUS — 大夹子
    (18034, '厨房餐具'),  # ESPAGUETERA ACERO PLUS — 意面夹
    (18035, '厨房餐具'),  # ESPATULA ACERO PLUS
    (18036, '厨房餐具'),  # ESPUMADERA ACERO PLUS
    (18037, '厨房餐具'),  # CUCHARA ACERO PLUS
    (18038, '厨房餐具'),  # ABRELATA ACERO PLUS
    (18039, '厨房餐具'),  # SACACORCHO ACERO PLUS
    (18040, '厨房餐具'),  # PICA AJO ACERO PLUS
    (18041, '厨房餐具'),  # CUCHARA BAMBU PLUS — 竹勺
    (18042, '厨房餐具'),  # ESPATULA BAMBU PLUS — 竹铲
    (18043, '厨房餐具'),  # CUCHARA BAMBU PLUS
    (18044, '厨房餐具'),  # ESPATULA BAMBU PLUS
    (18045, '厨房餐具'),  # PELAPAPA ACERO PLUS — 削皮器
    (18046, '厨房餐具'),  # CORTA PIZZA ACERO PLUS
    (18047, '厨房餐具'),  # PELAPAPA VERTICAL JOVIFEL
    (18048, '厨房餐具'),  # PELAPAPA HORIZONTAL JOVIFEL
    (18049, '厨房餐具'),  # ABRELATA MARIPOSA PREMIUM JOVIFEL — 蝶式开罐器
    (18050, '厨房餐具'),  # CORTA PIZZA PREMIUM JOVIFEL
    (18051, '厨房餐具'),  # SACACORCHO PALANCA JOVIFEL — 杠杆开瓶器
    (18052, '厨房餐具'),  # SACACORCHO DOBLE JOVIFEL
    (18053, '厨房餐具'),  # PRENSA AJO PREMIUM JOVIFEL — 压蒜器
    (18054, '厨房餐具'),  # CORTA HUEVO PREMIUM JOVIFEL — 切蛋器
    (18055, '厨房餐具'),  # PELAPAPA (40038)
    (18056, '厨房餐具'),  # ESPATULA IBILI SILICONA
    (18057, '厨房餐具'),  # CUCHARAS MEDIDORAS 8 PIEZAS — 量勺
    (18058, '餐饮用品'),  # JARRA VIDRIO 1 LT — 玻璃壶
    (18059, '餐饮用品'),  # JARRA TERMICA NEGRA JOVIFEL 1 LT — 保温壶
    (18060, '餐饮用品'),  # JARRA TERMICA BLANCA JOVIFEL 1 LT
    (18061, '餐饮用品'),  # JARRA TERMICA VERDE JOVIFEL 1 LT
    (18062, '餐饮用品'),  # SET 6 TAZAS + 6 PLATOS VIDRIO — 杯碟套装
    (18063, '餐饮用品'),  # TAZA BOMBE CERAMICA — 陶瓷杯
    (18064, '厨房餐具'),  # ACEITERO SPRAY VIDRIO — 喷油瓶
    (18065, '厨房餐具'),  # PIMENTERO PLUS CHICO — 胡椒瓶
    (18066, '厨房餐具'),  # PIMENTERO PLUS GRANDE
    (18067, '清洁用品'),  # SACAPELUSA DIBUJOS BENABI — 粘毛器
    (18068, '卫浴用品'),  # CORTINA CON ESLABON 0.8 X 2 — 浴帘
    (18069, '厨房炊具'),  # BANQUET CHAROLADA PREMIUM — 搪瓷烤盘

    # 305-316: 蜡烛/保护膜/浴帘/桌布
    (18070, '装饰品'),    # VELA TIPO JARRITO METALIZADA — 罐装蜡烛
    (18071, '装饰品'),    # VELA EN CAJITA
    (18072, '装饰品'),    # SET VELA AROMATICA CAJITA DE 3
    (18073, '卫浴用品'),  # PROTECTOR MAGH PLASTICO — 浴帘保护
    (18074, '卫浴用品'),  # PROTECTOR MAGH CORTINA BAÑO 40 MICRONES
    (18075, '卫浴用品'),  # PROTECTOR MAGH SATIN SIMPLE
    (18076, '卫浴用品'),  # CORTINA MAGH DE BAÑO SATIN SIMPLE CON OJAL
    (18077, '装饰品'),    # MANTEL MAGH SATIN PESADO — 桌布
    (18078, '卫浴用品'),  # CORTINA MAGH CON PROTECTOR ANTIHONGO — 防霉浴帘
    (18079, '卫浴用品'),  # CORTINA MAGH SATIN DOBLE CON PROTECTOR
    (18080, '装饰品'),    # MANTEL MAGH POLIETILENO LIVIANO 1.8 X 1.4 — 桌布
    (18081, '卫浴用品'),  # CORTINA MAGH BAÑO SATIN DOBLE CON OJAL

    # 317-318: 清洁用品
    (18082, '清洁用品'),  # HAND SOAP — 洗手液
    (18083, '餐饮用品'),  # TERMO MEDIA MANIJA NEGRO MARWAL 1 LT — 保温瓶
    (18084, '餐饮用品'),  # TERMO MEDIA MANIJA ACERO MARWAL 1 LT
    (18085, '餐饮用品'),  # TERMO CHARRO BALA MARWAL 1 LT

    # 321-335: 马黛茶用品
    (18086, '装饰品'),    # KIT x2 LATA MATERA ROSA O VERDE — 马黛茶罐套装（装饰性）
    (18087, '餐饮用品'),  # MATE IMPERIAL — 马黛茶杯
    (18088, '餐饮用品'),  # MATE CHARRO
    (18089, '餐饮用品'),  # MATE NEGRO ACERO MARWAL
    (18090, '餐饮用品'),  # MATE BLANCO ACERO MARWAL
    (18091, '餐饮用品'),  # MATE GRANDE MILLO
    (18092, '餐饮用品'),  # MATE GRANDE AZUL Y ORO
    (18093, '餐饮用品'),  # SET MATERO 2 LATAS + MATE MARWAL
    (18094, '餐饮用品'),  # YERBA PACK MARWAL — 马黛茶包装
    (18095, '餐饮用品'),  # BOMBILLA PICO DE LORO MARWAL — 吸管
    (18096, '餐饮用品'),  # BOMBILLA CON RESORTE MARWAL
    (18097, '餐饮用品'),  # BOMBILLA CHATA MARWAL

    # 333-336: 吸管/马黛茶包/泡泡/文具
    (18098, '餐饮用品'),  # PACK SORBETES PAPEL PLUS — 纸吸管
    (18099, '收纳整理'),  # BOLSO MATERO MARWAL — 马黛茶包
    (18100, '玩具游戏'),  # BURBUJERO MINI BUBBLE CLUB — 泡泡玩具
    (18101, '文具办公'),  # CUADERNO ESPIRALADO A5 80 HOJAS — 螺旋本
    (18102, '文具办公'),  # CUADERNO TAPA FANTASIA 80 HOJAS — 笔记本

    # 338-350: 厨房工具/容器
    (18103, '厨房餐具'),  # PALA ALIMENTOS NUVA — 食物铲
    (18104, '厨房餐具'),  # SACACORCHO ELECTRICO — 电动开瓶器
    (18105, '厨房餐具'),  # SET 5 TABLAS DE PICAR FLEXIBLES — 砧板套装
    (18106, '厨房储物'),  # FRASCO 0.75 L CON DOSIFICADOR ACRILICO — 分配罐
    (18107, '厨房储物'),  # FRASCO 1 L CON DOSIFICADOR ACRILICO
    (18108, '厨房储物'),  # FRASCO 1.35 L CON DOSIFICADOR ACRILICO
    (18109, '厨房储物'),  # TARRO YERBA NUVA — 马黛茶罐
    (18110, '厨房储物'),  # TARRO AZUCAR NUVA — 糖罐
    (18111, '电器电子'),  # PAVA ELECTRICA — 电热水壶
    (18112, '厨房炊具'),  # PAVA ACERO INOXIDABLE 2 LTS — 不锈钢水壶
    (18113, '厨房餐具'),  # MANGA REPOSTERA LOEKEMEYER — 裱花袋

    # 349-358: 餐饮用品/砧板
    (18114, '餐饮用品'),  # VASO NUVA CON MEDIDAS — 量杯
    (18115, '厨房餐具'),  # SET X5 CORTANTE ACERO ESTRELLA — 星形切模
    (18116, '厨房餐具'),  # SET X5 CORTANTE ACERO FLOR — 花形切模
    (18117, '餐饮用品'),  # PACK X6 VASO CHICO 160 ML SISSY — 小杯
    (18118, '厨房储物'),  # RECIPIENTE VIDRIO 650 ML EN CAJA — 玻璃保鲜盒
    (18119, '厨房储物'),  # RECIPIENTE VIDRIO 1050 ML EN CAJA
    (18120, '厨房餐具'),  # TABLA PREMIUM BAMBU 20X30 — 竹砧板
    (18121, '厨房餐具'),  # TABLA PREMIUM BAMBU 22X32
    (18122, '厨房餐具'),  # TABLA PREMIUM BAMBU 24X34
    (18123, '厨房餐具'),  # TABLA PREMIUM BAMBU 26X36
    (18124, '厨房餐具'),  # SECAPLATO SIMPLE — 沥水架

    # 360-376: 调料/酒具/容器
    (18125, '厨房餐具'),  # MOLINILLO MADERA 21 CM BASE CERAMICA — 胡椒研磨器
    (18126, '厨房餐具'),  # MOLINILLO MADERA 25 CM BASE CERAMICA
    (18127, '厨房储物'),  # SET X5 ESPECIERO + RACK — 调料架套装
    (18128, '厨房餐具'),  # PIMENTERO ELECTRICO A PILA — 电动胡椒研磨
    (18129, '厨房储物'),  # QUESERA VIDRIO — 奶酪盒
    (18130, '厨房餐具'),  # TAPON DE VINO — 酒塞
    (18131, '餐饮用品'),  # PACK X 10 INDIVIDUALES — 10个餐垫
    (18132, '厨房储物'),  # HERMETICO RECTANGULAR 4.5 LTS DIF PLAST
    (18133, '厨房储物'),  # CONTENEDOR CUADRADO 700 ML NUVA
    (18134, '厨房储物'),  # CONTENEDOR CUADRADO 1200 ML NUVA
    (18135, '厨房储物'),  # CONTENEDOR REDONDO 200 ML NUVA
    (18136, '厨房储物'),  # CONTENEDOR REDONDO 540 ML NUVA
    (18137, '厨房储物'),  # CONTENEDOR REDONDO 1.46 LTS NUVA
    (18138, '厨房储物'),  # CONTENEDOR RECTANGULAR 450 ML NUVA
    (18139, '厨房储物'),  # CONTENEDOR RECTANGULAR 1.1 LTS NUVA
    (18140, '厨房储物'),  # CONTENEDOR RECTANGULAR 1.3 LTS NUVA
    (18141, '厨房储物'),  # CONTENEDOR RECTANGULAR 3.1 LTS NUVA
    (18142, '厨房储物'),  # CONTENEDOR RECTANGULAR 2.4 LTS NUVA
    (18143, '厨房储物'),  # CONTENEDOR RECTANGULAR 4.9 LTS NUVA
    (18144, '厨房储物'),  # CONTENEDOR RECTANGULAR 9 LTS NUVA

    # 380-389: 餐具/收纳
    (18145, '餐饮用品'),  # ENSALADERA FACETADA 1.7 LTS NUVA — 沙拉碗
    (18146, '餐饮用品'),  # ENSALADERA FACETADA 2.5 LTS NUVA
    (18147, '餐饮用品'),  # CESTA PROFUNDA CHICA (642) — 深篮
    (18148, '餐饮用品'),  # CESTA PROFUNDA CHICA (644)
    (18149, '餐饮用品'),  # JARRA CON TAPA 2.15 LITROS NUVA — 带盖壶
    (18150, '餐饮用品'),  # BOTELLA PASTEL 750 CC TAPA FLIP BELGIOCO — 翻盖瓶
    (18151, '餐饮用品'),  # BOTELLA TRASLUCIDA 750 CC TAPA FLIP
    (18152, '装饰品'),    # KIT x2 LATA MATERA BLANCO — 马黛茶罐（装饰性）
    (18153, '装饰品'),    # KIT x2 LATA MATERA NEGRO
    (18154, '清洁用品'),  # REPASADOR COCINA & DISEÑO — 抹布
    (18155, '餐饮用品'),  # VASO ALTO CON TAPA Y BOMBILLA ARGENTINA — 带吸管高杯
    (18156, '餐饮用品'),  # PLATO PLAYO ARGENTINA BELGIOCO — 平盘
    (18157, '厨房储物'),  # HERMETICO TO GO 3 DIVISIONES BELGIOCO — 分格保鲜盒
    (18158, '清洁用品'),  # HAND SOAP
    (18159, '卫浴用品'),  # DISPENSER TRAMADO VIDRIO — 皂液器
    (18160, '卫浴用品'),  # CORTINA MAGH SIMPLE CON POLIETILENO — 浴帘

    # 396-399: 厨房/运动/宠物/清洁
    (18161, '厨房炊具'),  # PIZZERA PREMIUM BAMBU — 竹披萨板
    (18162, '运动户外'),  # PELOTA FUTBOL N5 ARGENTINA — 足球
    (18163, '运动户外'),  # PELOTA FUTBOL N5 ARGENTINA
    (18164, '运动户外'),  # PELOTA PVC LIVIANA — 轻型PVC球

    # 400-406: 宠物/清洁
    (18165, '宠物用品'),  # CAMA PARA PERROS (S)
    (18166, '宠物用品'),  # CAMA PARA PERROS (M)
    (18167, '清洁用品'),  # PAÑO ALAMBRE X10 — 钢丝布
    (18168, '清洁用品'),  # PAÑO X5 METALICO — 钢丝布
    (18169, '清洁用品'),  # CEPILLO LIMPIEZA BAMBU
    (18170, '清洁用品'),  # CEPILLITO X3 EN BOLSITA — 小刷子

    # 406-433: SAN REMO 更多密封罐（/5、/6、/10系列）
    (18171, '厨房储物'),  # HERMETICO REDONDO 620 ML (/6/10)
    (18172, '厨房储物'),  # HERMETICO REDONDO 1.3 LTS (/6/10)
    (18173, '厨房储物'),  # HERMETICO CUADRADO 800 ML FACIL (/6/10)
    (18174, '厨房炊具'),  # TARTERA PLASTICA CON TAPA DIF — 派盘
    (18175, '厨房储物'),  # HERMETICO RECTANGULAR 700 ML SAN REMO (/5)
    (18176, '厨房储物'),  # HERMETICO RECTANGULAR 1260 ML (/5)
    (18177, '厨房储物'),  # HERMETICO RECTANGULAR 2300 ML (/5)
    (18178, '厨房储物'),  # HERMETICO REDONDO 1100 ML (/5)
    (18179, '厨房储物'),  # HERMETICO REDONDO 3200 ML (/5)
    (18180, '厨房储物'),  # HERMETICO CUADRADO 280 ML (/5)
    (18181, '厨房储物'),  # HERMETICO CUADRADO 450 ML (/5)
    (18182, '厨房储物'),  # HERMETICO CUADRADO 920 ML (/5)
    (18183, '厨房储物'),  # HERMETICO CUADRADO 1600 ML (/5)
    (18184, '厨房储物'),  # HERMETICO PARA FIAMBRES SAN REMO — 肉类密封盒
    (18185, '厨房储物'),  # SNACK BOX 3 DIVISIONES SAN REMO
    (18186, '厨房储物'),  # HERMETICO CUADRADO 2700 ML (/5)
    (18187, '厨房储物'),  # HERMETICO RECTANGULAR 2400 ML (/5)
    (18188, '厨房储物'),  # HERMETICO RECTANGULAR 4600 ML (/5)
    (18189, '厨房储物'),  # HERMETICO RECTANGULAR CON DIVISION 730 ML
    (18190, '厨房储物'),  # HERMETICO RECTANGULAR 1240 ML
    (18191, '厨房储物'),  # HERMETICO RECTANGULAR 430 ML (/5)
    (18192, '厨房储物'),  # SET X2 MARMITA RECTANGULAR — 炖锅密封盒
    (18193, '厨房储物'),  # HERMETICO REDONDO 480 ML (/5)
    (18194, '厨房储物'),  # SET SAN REMO FACIL X3 (/6C)
    (18195, '厨房储物'),  # SET SAN REMO FLOR X3 (706/C)
    (18196, '厨房储物'),  # SET SAN REMO FLOR X3 (712/5C)
    (18197, '厨房储物'),  # SET SAN REMO FLOR X3 (722/C)
    (18198, '厨房储物'),  # SET SAN REMO FLOR X3 (723/C)
    (18199, '厨房储物'),  # HERMETICO STAR REDONDO CHICO COLOR

    # 435-448: 收纳箱/碗/冰格
    (18200, '收纳整理'),  # CAJA BLACK 70LTS LUK HOME — 收纳箱
    (18201, '收纳整理'),  # CAJA GIGANTE RATAN NEGRA N6 — 藤编收纳箱
    (18202, '收纳整理'),  # CAJA GIGANTE RATAN BLANCA N6
    (18203, '收纳整理'),  # CANASTO RATAN ORGANIZADOR GRANDE NEGRO
    (18204, '收纳整理'),  # CANASTO RATAN ORGANIZADOR GRANDE BLANCO
    (18205, '收纳整理'),  # CANASTO RATAN ORGANIZADOR CHICO NEGRO
    (18206, '收纳整理'),  # CANASTO RATAN ORGANIZADOR CHICO BLANCO
    (18207, '餐饮用品'),  # BOWL CON ONDAS GRANDE SAFE LOCK — 带盖大碗
    (18208, '餐饮用品'),  # BOLS 14 CM GRANITO PLASTICO — 碗
    (18209, '餐饮用品'),  # BOLS 20 CM GRANITO PLASTICO
    (18210, '餐饮用品'),  # BOWL 14 CM GRANITO PLASTICO
    (18211, '餐饮用品'),  # BOWL 20 CM GRANITO PLASTICO
    (18212, '餐饮用品'),  # PLATO PLASTICO GRANITO 25 CM — 塑料盘
    (18213, '厨房餐具'),  # CUBETERA SILICONA X6 BEIGE — 冰格
    (18214, '厨房餐具'),  # CUBETERA SILICONA X6 GRIS
    (18215, '厨房餐具'),  # CUBETERA SILICONA X6 VERDE
    (18216, '厨房餐具'),  # CUBETERA PLASTICA CON BASE SILICONA BEIGE
    (18217, '厨房餐具'),  # CUBETERA PLASTICA CON BASE SILICONA GRIS

    # 453-464: 玻璃保鲜盒/蒸锅/模具
    (18218, '厨房炊具'),  # BIFERA ENLOZADA N4 — 搪瓷双耳煎锅
    (18219, '厨房储物'),  # TUPPER VIDRIO CUADRADO 1100 ML — 玻璃保鲜盒
    (18220, '厨房储物'),  # TUPPER VIDRIO RECT 640 ML
    (18221, '厨房储物'),  # TUPPER VIDRIO CUADRADO 320 ML
    (18222, '厨房储物'),  # TUPPER VIDRIO REDONDO 400 ML
    (18223, '厨房储物'),  # TUPPER VIDRIO CUADRADO 520 ML
    (18224, '厨房储物'),  # TUPPER VIDRIO REDONDO 1300 ML
    (18225, '厨房储物'),  # TUPPER VIDRIO CUADRADO 800 ML
    (18226, '厨房储物'),  # TUPPER VIDRIO RECT 370 ML
    (18227, '厨房储物'),  # TUPPER VIDRIO RECT 1050 ML
    (18228, '厨房储物'),  # TUPPER VIDRIO RECT 1520 ML
    (18229, '厨房储物'),  # TUPPER VIDRIO REDONDO 650 ML
    (18230, '厨房储物'),  # TUPPER VIDRIO REDONDO 950 ML

    # 466-498: 炊具/硅胶模具
    (18231, '厨房炊具'),  # VAPORIERA ACERO — 蒸锅
    (18232, '厨房炊具'),  # DIFUSOR SIMMER RING — 导热板
    (18233, '厨房炊具'),  # MOLDE SILICONA CUADRADO PLEGABLE BEIGE — 硅胶折叠模
    (18234, '厨房炊具'),  # MOLDE SILICONA CUADRADO PLEGABLE GRIS
    (18235, '厨房炊具'),  # MOLDE SILICONA CUADRADO PLEGABLE TERRA
    (18236, '厨房炊具'),  # MOLDE SILICONA CUADRADO PLEGABLE VERDE
    (18237, '厨房炊具'),  # MOLDE SILICONA REDONDO PLEGABLE GRIS
    (18238, '厨房炊具'),  # MOLDE SILICONA REDONDO PLEGABLE TERRA
    (18239, '厨房炊具'),  # MOLDE SILICONA REDONDO PLEGABLE VERDE
    (18240, '厨房炊具'),  # BUDINERA SILICONA BEIGE
    (18241, '厨房炊具'),  # BUDINERA SILICONA GRIS
    (18242, '厨房炊具'),  # BUDINERA SILICONA TERRA
    (18243, '厨房炊具'),  # BUDINERA SILICONA VERDE
    (18244, '厨房炊具'),  # SAVARIN SILICONA BEIGE — 环形模
    (18245, '厨房炊具'),  # SAVARIN SILICONA GRIS
    (18246, '厨房炊具'),  # SAVARIN SILICONA TERRA
    (18247, '厨房炊具'),  # SAVARIN SILICONA VERDE
    (18248, '厨房炊具'),  # MOLDE PARA MUFFIN SILICONA BEIGE
    (18249, '厨房炊具'),  # MOLDE PARA MUFFIN SILICONA GRIS
    (18250, '厨房炊具'),  # MOLDE PARA MUFFIN SILICONA TERRA
    (18251, '厨房炊具'),  # MOLDE PARA MUFFIN SILICONA VERDE
    (18252, '厨房炊具'),  # TORTERA SILICONA 24X5.5CM BEIGE
    (18253, '厨房炊具'),  # TORTERA SILICONA 24X5.5CM GRIS
    (18254, '厨房炊具'),  # TORTERA SILICONA 24X5.5CM TERRA
    (18255, '厨房炊具'),  # TORTERA SILICONA 24X5.5CM VERDE
    (18256, '厨房炊具'),  # TORTERA SILICONA 20X5.5CM BEIGE
    (18257, '厨房炊具'),  # TORTERA SILICONA 20X5.5CM GRIS
    (18258, '厨房炊具'),  # TORTERA SILICONA 20X5.5CM TERRA
    (18259, '厨房炊具'),  # TORTERA SILICONA 20X5.5CM VERDE
    (18260, '厨房炊具'),  # MOLDE SILICONA BASE RIGIDA BEIGE
    (18261, '厨房炊具'),  # MOLDE SILICONA BASE RIGIDA GRIS
    (18262, '厨房炊具'),  # MOLDE SILICONA BASE RIGIDA TERRA
    (18263, '厨房炊具'),  # MOLDE SILICONA BASE RIGIDA VERDE
    (18264, '厨房炊具'),  # TARTERA RIZADA DESFONDABLE N26 — 活底花边派盘

    # 500-504: 壶/罐/容器
    (18265, '餐饮用品'),  # JARRO ENLOZADO CON FRASES 12 CM — 搪瓷壶
    (18266, '餐饮用品'),  # JARRO ENLOZADO CON FRASES 10 CM
    (18267, '厨房储物'),  # POTE CHICO OPENING 1000 CC — 容器
    (18268, '厨房储物'),  # POTE MEDIANO OPENING 1700 CC
    (18269, '厨房储物'),  # POTE GRANDE OPENING 2400 CC

    # 505-538: Carol 厨具系列（逐条审查）
    (18270, '厨房餐具'),  # SET X4 TABLAS + CONTENEDOR CAROL — 砧板套装+容器
    (18271, '厨房餐具'),  # RALLADOR NEGRO CAROL MANGO BAMBU
    (18272, '厨房餐具'),  # RALLADOR ACERO MANGO ERGONOMICO BEIGE
    (18273, '厨房餐具'),  # RALLADOR ACERO MANGO ERGONOMICO GRIS
    (18274, '厨房餐具'),  # RALLADOR ACERO MANGO ERGONOMICO TERRA
    (18275, '厨房餐具'),  # RALLADOR ACERO MANGO ERGONOMICO VERDE
    (18276, '厨房餐具'),  # RALLADOR CONICO MANGO MADERA — 锥形擦丝器
    (18277, '厨房餐具'),  # RALLADOR 2 CORTES CON CONTENEDOR Y TAPA
    (18278, '厨房餐具'),  # COLADOR CON ASA PLEGABLE — 折叠滤网
    (18279, '厨房餐具'),  # COLADOR CON MANGO PLEGABLE
    (18280, '厨房餐具'),  # TIJERA DE COCINA MULTIUSO BEIGE — 厨房剪刀
    (18281, '厨房餐具'),  # TIJERA DE COCINA MULTIUSO GRIS
    (18282, '厨房餐具'),  # TIJERA DE COCINA MULTIUSO TERRA
    (18283, '厨房餐具'),  # TIJERA DE COCINA MULTIUSO VERDE
    (18284, '厨房餐具'),  # SET X2 PINZA GRANDE Y CHICA BEIGE — 夹子套装
    (18285, '厨房餐具'),  # SET X2 PINZA GRANDE Y CHICA GRIS
    (18286, '厨房餐具'),  # SET X2 PINZA GRANDE Y CHICA TERRA
    (18287, '厨房餐具'),  # SET X2 PINZA GRANDE Y CHICA VERDE
    (18288, '厨房餐具'),  # ESPATULA SILICONA EN BLISTER BEIGE
    (18289, '厨房餐具'),  # ESPATULA SILICONA EN BLISTER GRIS
    (18290, '厨房餐具'),  # ESPATULA SILICONA EN BLISTER TERRA
    (18291, '厨房餐具'),  # PINCEL SILICONA EN BLISTER BEIGE — 硅胶刷
    (18292, '厨房餐具'),  # PINCEL SILICONA EN BLISTER GRIS
    (18293, '厨房餐具'),  # PINCEL SILICONA EN BLISTER TERRA
    (18294, '厨房餐具'),  # PINCEL SILICONA EN BLISTER VERDE
    (18295, '厨房餐具'),  # BATIDOR ACERO MANGO SILICONA — 打蛋器
    (18296, '厨房餐具'),  # BATIDOR CON RASPADOR BEIGE — 带刮刀打蛋器
    (18297, '厨房餐具'),  # BATIDOR CON RASPADOR GRIS
    (18298, '厨房餐具'),  # BATIDOR CON RASPADOR TERRA
    (18299, '厨房餐具'),  # BATIDOR CON RASPADOR VERDE
    (18300, '厨房餐具'),  # SET X9 UTENSILLOS BEIGE — 9件厨具套装
    (18301, '厨房餐具'),  # SET X9 UTENSILLOS GRIS
    (18302, '厨房餐具'),  # SET X9 UTENSILLOS TERRA
    (18303, '厨房餐具'),  # SET X9 UTENSILLOS VERDE
    (18304, '厨房餐具'),  # SET X5 UTENSILLOS ENCASTRABLE — 可叠放厨具
    (18305, '厨房餐具'),  # PINZA P HIELO CHICA — 冰夹
    (18306, '厨房餐具'),  # PICADOR AJO FACILA — 压蒜器

    # 542-555: 马黛茶/餐具/窗帘
    (18307, '餐饮用品'),  # MATE ANIMALITOS + BOMBILLA + SACAYERBA
    (18308, '餐饮用品'),  # MATE DECO + BOMBILLA + SACAYERBA
    (18309, '餐饮用品'),  # PLATO HONDO LABRADO DURAX — 深盘
    (18310, '餐饮用品'),  # PLATO BAMBU NORDICO CLIKER — 竹盘
    (18311, '餐饮用品'),  # PACK X6 VASO 250 ML DELI GLASS
    (18312, '餐饮用品'),  # PACK X6 VASO 325 ML DELI GLASS
    (18313, '餐饮用品'),  # PACK X6 VASO 450 ML DELI GLASS
    (18314, '餐饮用品'),  # PACK X6 VASO DIAMONDS
    (18315, '餐饮用品'),  # BOTELLA 1 LT VIDRIO TAPA CORCHO — 玻璃瓶
    (18316, '餐饮用品'),  # HIELERA DE VIDRIO EN CAJA — 玻璃冰桶
    (18317, '餐饮用品'),  # VASO DOBLE VIDRIO 80ML
    (18318, '餐饮用品'),  # VASO DOBLE VIDRIO 250ML
    (18319, '餐饮用品'),  # VASO DOBLE VIDRIO 150ML
    (18320, '厨房餐具'),  # JUEGO CUBIERTOS BEIGE EN TUBO
    (18321, '厨房餐具'),  # MOLINILLO MADERA BAMBU BLANCO CAROL — 研磨器
    (18322, '厨房餐具'),  # MOLINILLO MADERA BAMBU NEGRO CAROL

    # 558-566: 卫浴/暖水袋/防虫网
    (18323, '卫浴用品'),  # TAPA P PILETA UNIVERSAL — 水槽盖
    (18324, '卫浴用品'),  # REJILLA P PILETA UNIVERSAL — 水槽滤网
    (18325, '卫浴用品'),  # TAPA Y REJILLA P PILETA UNIVERSAL
    (18326, '个人防护'),  # BOLSA DE AGUA CALIENTE 2lts — 热水袋
    (18327, '其他'),      # BICHO RED REJILLA 8X8 — 防虫网（图片审查确认）
    (18328, '其他'),      # BICHO RED REJILLA 9X9
    (18329, '其他'),      # BICHO RED REJILLA 11X11
    (18330, '其他'),      # BICHO RED REJILLA 13X13
    (18331, '其他'),      # BICHO RED REJILLA 15X15
    (18332, '其他'),      # BICHO RED REJILLA 18X18
    (18333, '其他'),      # BICHO RED REJILLA 20X20

    # 569-577: 卫浴配件
    (18334, '卫浴用品'),  # PORTA CEPILLO AUTOADHESIVO — 粘贴牙刷架
    (18335, '卫浴用品'),  # POSA JABON AUTOADHESIVO — 粘贴皂碟
    (18336, '卫浴用品'),  # PORTA ROLLO ECO AUTOADHESIVO
    (18337, '卫浴用品'),  # PORTA ROLLO TRIANGULAR AUTOADHESIVO
    (18338, '卫浴用品'),  # PORTA TOALLA AUTOADHESIVA
    (18339, '卫浴用品'),  # JABONERA JABON SECO AUTOADHESIVA

    # 575-583: 保温瓶/马黛茶/清洁/餐具
    (18340, '餐饮用品'),  # TERMO ACERO MARWAL PICO SYSTEM 1 LT
    (18341, '餐饮用品'),  # TERMO KEEP BALA 1 LT
    (18342, '餐饮用品'),  # MATE SONICO URBANO SACAYERBA
    (18343, '餐饮用品'),  # LIMPIADOR PARA BOMBILLA Y SORBETE — 吸管清洁器
    (18344, '餐饮用品'),  # PLATO PLAYO PERSONAJES BELGIOCO — 儿童餐盘
    (18345, '清洁用品'),  # CEPILLO LIMPIA MAMADERA + MINI CEPILLO — 奶瓶刷
    (18346, '厨房储物'),  # HERMETICO PERSONAJES 3 DIVISIONES BELGIOCO — 儿童分格餐盒
    (18347, '卫浴用品'),  # FILTRO PILETA X2 — 水槽滤网

    # 583-600: 玩具（球类/游戏）
    (18348, '运动户外'),  # PELOTA FUTBOL N5 PAISES MUNDIAL
    (18349, '运动户外'),  # PELOTA FUTBOL N5 STARS
    (18350, '玩具游戏'),  # PELOTA FUTBOL N2 MARVEL — 儿童玩具球
    (18351, '玩具游戏'),  # PELOTA FUTBOL N2 STICH — 儿童玩具球
    (18352, '玩具游戏'),  # PELOTITAS GOMA ESPUMA FUTBOL — 泡沫球
    (18353, '玩具游戏'),  # PELOTITAS GOMA ESPUMA EN CAJA CON DIBUJO
    (18354, '玩具游戏'),  # PELOTITAS GOMA ESPUMA RUGBY
    (18355, '玩具游戏'),  # KIT DE PELOTAS — 玩具球套装
    (18356, '玩具游戏'),  # PELOTA SALTARINA — 弹跳球
    (18357, '玩具游戏'),  # PELOTA SALTARINA STITCH
    (18358, '玩具游戏'),  # PELOTAS SOFT FUTBOL PLAY — 软球
    (18359, '玩具游戏'),  # BINGO AFA CAJA CUADRADA
    (18360, '玩具游戏'),  # BINGO AFA
    (18361, '玩具游戏'),  # JUEGO BINGO SPIDERMAN
    (18362, '玩具游戏'),  # DESCUBRI QUIEN ES
    (18363, '玩具游戏'),  # TATETI DESAFIO — 井字棋
    (18364, '玩具游戏'),  # HAPPY MONKEY CHICO
    (18365, '玩具游戏'),  # HAPPY MONKEY GRANDE
    (18366, '玩具游戏'),  # CRAZY DINO
    (18367, '玩具游戏'),  # SUPER GOL — 桌面足球
    (18368, '玩具游戏'),  # JUEGO CARRERA DE HADAS — 桌游
    (18369, '玩具游戏'),  # POOL TABLE — 台球桌
    (18370, '玩具游戏'),  # MINI DOMINO
    (18371, '玩具游戏'),  # MINI JUEGO DE DADOS
    (18372, '玩具游戏'),  # JUEGO DE MESA STOP
    (18373, '玩具游戏'),  # SUPER STOP AZUL
    (18374, '玩具游戏'),  # SUPER STOP ROJO
    (18375, '玩具游戏'),  # BINGO
    (18376, '玩具游戏'),  # LUDO AFA
    (18377, '玩具游戏'),  # DINO AL SUELO
    (18378, '玩具游戏'),  # MINI PINGUINO AL AGUA

    # 614-700: 玩具（娃娃系列）
    (18379, '玩具游戏'),  # MUÑECA TINY DOLL DELFI 42 CM
    (18380, '玩具游戏'),  # MUÑECA TINY Y SU BICI
    (18381, '玩具游戏'),  # MUÑECA TINY Y SU AUTO CON STICKERS
    (18382, '玩具游戏'),  # MUÑECA TINY FASHION
    (18383, '玩具游戏'),  # SIRENA MAGIC DOLL
    (18384, '玩具游戏'),  # TINY PONY Y SU CARRUAJE
    (18385, '玩具游戏'),  # TINY HORSE
    (18386, '玩具游戏'),  # BEBOTE TINY DOLL NOE
    (18387, '玩具游戏'),  # BEBOTE TINY DOLL OLI
    (18388, '玩具游戏'),  # BEBOTE TINY DOLL EMI
    (18389, '玩具游戏'),  # BEBOTE TINY DOLL AGUS
    (18390, '玩具游戏'),  # BEBOTE TINY DOLL ANA
    (18391, '玩具游戏'),  # MUÑECA TINY SWEET SHOP
    (18392, '玩具游戏'),  # MUÑECA TINY Y SU GRANJA
    (18393, '玩具游戏'),  # MUÑECA TINY SPA
    (18394, '玩具游戏'),  # MUÑECA TINY CLEARING
    (18395, '玩具游戏'),  # MUÑECA TINY Y SUS MASCOTAS
    (18396, '玩具游戏'),  # MUÑECA TINY DENTISTA
    (18397, '玩具游戏'),  # MUÑECA TINY SKINCARE
    (18398, '玩具游戏'),  # MUÑECA TINY INFLUENCER
    (18399, '玩具游戏'),  # MUÑECA TINY MAESTRA DE ARTE
    (18400, '玩具游戏'),  # MUÑECA TINY SPORT
    (18401, '玩具游戏'),  # MUÑECA TINY ROCKER
    (18402, '玩具游戏'),  # MUÑECA TINY CHEF
    (18403, '玩具游戏'),  # MUÑECA TINY Y SU MASCOTA
    (18404, '玩具游戏'),  # MUÑECA TINY FASHION NOCHE
    (18405, '玩具游戏'),  # MUÑECA TINY TENISTA
    (18406, '玩具游戏'),  # MUÑECA TINY Y BEBE
    (18407, '玩具游戏'),  # MUÑECA TINY VETERINARIA
    (18408, '玩具游戏'),  # MUÑECA TINY FUTBOLISTA
    (18409, '玩具游戏'),  # MUÑECA TINY BAILARINA
    (18410, '玩具游戏'),  # MUÑECA TINY HADAS
    (18411, '玩具游戏'),  # MUÑECA TINY Y LUCY EN SU CABALLO
    (18412, '玩具游戏'),  # MUÑECA TINY SKY
    (18413, '玩具游戏'),  # MUÑECA TINY Y SU MONOPATIN
    (18414, '玩具游戏'),  # MUÑECA TINY Y SU BICI CANDY
    (18415, '玩具游戏'),  # MUÑECA TINY Y SU MOTO
    (18416, '玩具游戏'),  # MUÑECA TINY SURFISTA
    (18417, '玩具游戏'),  # MUÑECA TINY Y SU KAYAK
    (18418, '玩具游戏'),  # MUÑECA TINY Y SU KAYAK + RUEDA Y CHALECO
    (18419, '玩具游戏'),  # MUÑECA TINY Y SU MOTO DE AGUA
    (18420, '玩具游戏'),  # MUÑECA TINY Y SU LANCHA
    (18421, '玩具游戏'),  # MUÑECA TINY Y SU AUTO
    (18422, '玩具游戏'),  # MUÑECA TINY Y SU JEEP
    (18423, '玩具游戏'),  # MUÑECA TINY Y SU SMART
    (18424, '玩具游戏'),  # MUÑECA TINY SIRENA
    (18425, '玩具游戏'),  # MUÑECA TINY Y SU MASCOTA
    (18426, '玩具游戏'),  # MUÑECA TINY HADA
    (18427, '玩具游戏'),  # MUÑECA TINY
    (18428, '玩具游戏'),  # MUÑECA TINY MAMA CON ACCESORIOS
    (18429, '玩具游戏'),  # MUÑECA DOBLE TINY
    (18430, '玩具游戏'),  # MUÑECA TINY + TOBOGAN Y CALESITA
    (18431, '玩具游戏'),  # MUÑECA TINY Y SU HERMANA + PATINES
    (18432, '玩具游戏'),  # MUÑECA TINY Y SU HERMANA + ZAPATOS
    (18433, '玩具游戏'),  # MUÑECA TINY VAMOS AL PARQUE
    (18434, '玩具游戏'),  # MUÑECA TINY DESCUBRI EL BEBE
    (18435, '玩具游戏'),  # MUÑECA TINY CON BEBE Y MAMADERA
    (18436, '玩具游戏'),  # MUÑECA TINY + BOTAS
    (18437, '玩具游戏'),  # MUÑECA TINY
    (18438, '玩具游戏'),  # MUÑECA TINY
    (18439, '玩具游戏'),  # MUÑECA TINY EN BLISTER
    (18440, '玩具游戏'),  # MUÑECA TINY
    (18441, '玩具游戏'),  # MUÑECA TINY
    (18442, '玩具游戏'),  # MUÑECA TINY
    (18443, '玩具游戏'),  # MUÑECA TINY
    (18444, '玩具游戏'),  # MUÑECA LUCY Y SU HELICOPTERO
    (18445, '玩具游戏'),  # LULISTAR Y SU AUTO
    (18446, '玩具游戏'),  # BEBE RAFA/AGUS
    (18447, '玩具游戏'),  # BEBE ELU
    (18448, '玩具游戏'),  # BABY EN CAJA 22CM
    (18449, '玩具游戏'),  # TINY KIT BABY BAÑO
    (18450, '玩具游戏'),  # MUÑECA CON DISFRAZ SOFI
    (18451, '玩具游戏'),  # MUÑECA CON DISFRAZ MARTU
    (18452, '玩具游戏'),  # MUÑECA CON DISFRAZ MILI
    (18453, '玩具游戏'),  # MUÑECA CON DISFRAZ LULI
    (18454, '玩具游戏'),  # MUÑECA TINY VALEN
    (18455, '玩具游戏'),  # MUÑECA TINY MAESTRA
    (18456, '玩具游戏'),  # MUÑECA TINY ROCKSTAR
    (18457, '玩具游戏'),  # MUÑECA HADA Y SU CABALLO
    (18458, '玩具游戏'),  # MUÑECA TINY Y SU HELICOPTERO
    (18459, '玩具游戏'),  # MUÑECA TINY + KEVIN + BEBES
    (18460, '玩具游戏'),  # MUÑECA TINY Y ACCESORIOS
    (18461, '玩具游戏'),  # MUÑECA TINY Y ACCESORIOS
    (18462, '玩具游戏'),  # MUÑECA MALE 26 CM
    (18463, '玩具游戏'),  # MUÑECA TINY RAINBOW ANTO
    (18464, '玩具游戏'),  # MUÑECA BELU

    # 700-723: 玩具（遥控车/摩擦车）
    (18465, '玩具游戏'),  # AUTO GO SPEED + CONTROL
    (18466, '玩具游戏'),  # AUTO GO SPEED + CONTROL VOLANTE
    (18467, '玩具游戏'),  # FORMULA 1 GO SPEED + CONTROL
    (18468, '玩具游戏'),  # AUTO MONSTER GO SPEED
    (18469, '玩具游戏'),  # AUTO CON CONTROL SPIDERMAN
    (18470, '玩具游戏'),  # AUTO POLICIA A CONTROL REMOTO
    (18471, '玩具游戏'),  # AUTO A CONTROL REMOTO
    (18472, '玩具游戏'),  # AUTO GO SPEED
    (18473, '玩具游戏'),  # AUTO METALICO PERSONAJES MARVEL
    (18474, '玩具游戏'),  # AUTO X4 MARVEL EN CAJA
    (18475, '玩具游戏'),  # AUTO METALICO EN CAJA
    (18476, '玩具游戏'),  # PISTA DE AUTO SERPIENTE
    (18477, '玩具游戏'),  # PISTA DE AUTO COCODRILO
    (18478, '玩具游戏'),  # CAMION SPIDERMAN
    (18479, '玩具游戏'),  # AUTO A FRICCION SPIDERMAN EN CAJA
    (18480, '玩具游戏'),  # AUTO A FRICCION SPIDERMAN EN BLISTER
    (18481, '玩具游戏'),  # AUTO POLICIA X2
    (18482, '玩具游戏'),  # BLISTER 5 AUTITOS
    (18483, '玩具游戏'),  # BLISTER 10 AUTITOS
    (18484, '玩具游戏'),  # BLISTER AUTO METALIZADO 12 UNIDADES
    (18485, '玩具游戏'),  # AUTO A PILA CON LUCES Y PISTA
    (18486, '玩具游戏'),  # PISTA DE TREN
    (18487, '玩具游戏'),  # AUTO RADIO CONTROL SPIDERMAN
    (18488, '玩具游戏'),  # AUTOBUS A FRICCION AFA
    (18489, '玩具游戏'),  # MONOPATIN GO SPEED 3 RUEDAS — 儿童滑板车
    (18490, '玩具游戏'),  # MONOPATIN SPIDEY 3 RUEDAS
    (18491, '玩具游戏'),  # MONOPATIN MICKEY 3 RUEDAS
    (18492, '玩具游戏'),  # MONOPATIN PRINCESAS 3 RUEDAS
    (18493, '玩具游戏'),  # MONOPATIN STITCH 3 RUEDAS
    (18494, '玩具游戏'),  # MONOPATIN FROZEN 3 RUEDAS
    (18495, '玩具游戏'),  # MONOPATIN GABBY DOLLHOUSE 3 RUEDAS
    (18496, '玩具游戏'),  # MONOPATIN BATMAN 3 RUEDAS
    (18497, '玩具游戏'),  # MONOPATIN BOCA 3 RUEDAS
    (18498, '玩具游戏'),  # MONOPATIN RIVER 3 RUEDAS
    (18499, '运动户外'),  # PATINES CON BOLSITO TINY AJUSTABLE — 滑冰鞋
    (18500, '运动户外'),  # PATINES CON BOLSITO STITCH
    (18501, '运动户外'),  # PATINES CON BOLSITO PRINCESAS
    (18502, '运动户外'),  # PATINES CON BOLSITO FROZEN

    # 738-765: 美妆/化妆品
    (18503, '美妆个护'),  # SET BELLEZA
    (18504, '美妆个护'),  # SET UÑAS FROZEN
    (18505, '美妆个护'),  # PALETA MAQUILLAJE KOALA
    (18506, '美妆个护'),  # MAQUILLAJE PALETA
    (18507, '美妆个护'),  # MAQUILLAJE PASTEL
    (18508, '美妆个护'),  # MAQUILLAJE MINI CUP CAKE
    (18509, '美妆个护'),  # MAQUILLAJE MALTEADA
    (18510, '美妆个护'),  # MAQUILLAJE CARAMELO
    (18511, '美妆个护'),  # MAQUILLAJE CUCURUCHO
    (18512, '美妆个护'),  # MAQUILLAJE ICE CREAM
    (18513, '美妆个护'),  # MAQUILLAJE PALETA HELADO
    (18514, '美妆个护'),  # MAQUILLAJE PALETA HELADO
    (18515, '美妆个护'),  # MAQUILLAJE ARCO IRIS
    (18516, '美妆个护'),  # MAQUILLAJE CUP CAKE
    (18517, '美妆个护'),  # MAQUILLAJE
    (18518, '美妆个护'),  # MAQUILLAJE
    (18519, '美妆个护'),  # MAQUILLAJE MARIPOSA O CORONA
    (18520, '美妆个护'),  # MAQUILLAJE LABIAL
    (18521, '美妆个护'),  # MAQUILLAJE CARTERA CHICA TINY
    (18522, '美妆个护'),  # MAQUILLAJE CARTERA GRANDE TINY
    (18523, '美妆个护'),  # MAQUILLAJE DONA TINY
    (18524, '美妆个护'),  # MAQUILLAJE UNICORNIO
    (18525, '美妆个护'),  # MAQUILLAJE MARIPOSA
    (18526, '美妆个护'),  # MAQUILLAJE SOMBRA EN BLISTER
    (18527, '美妆个护'),  # MAQUILLAJE
    (18528, '美妆个护'),  # MAQUILLAJE FORMA OSITO
    (18529, '美妆个护'),  # LAPIZ LABIAL TINY
    (18530, '美妆个护'),  # ESMALTE DE UÑAS TINY

    # 766-826: 玩具（枪/泡泡/水游戏/棋盘/电子）
    (18531, '玩具游戏'),  # PISTOLA AIR BLASTERS POWER
    (18532, '玩具游戏'),  # PISTOLA LANZA DARDOS BATMAN
    (18533, '玩具游戏'),  # PISTOLA LANZA DARDOS SUPERMAN
    (18534, '玩具游戏'),  # PISTOLA LANZA BOLAS
    (18535, '玩具游戏'),  # PISTOLA AIR POWER
    (18536, '玩具游戏'),  # PISTOLA BLAST POPPER LANZA BOLAS
    (18537, '玩具游戏'),  # PISTOLA 2 EN 1 SHOOT WEAPON
    (18538, '玩具游戏'),  # BURBUJERO A PILA DINOSAURIO TINY
    (18539, '玩具游戏'),  # BURBUJERO A PILA UNICORNIO TINY
    (18540, '玩具游戏'),  # BURBUJERO A PILA CON LUZ
    (18541, '玩具游戏'),  # PACK X 3 BURBUJEROS UNICORNIO
    (18542, '玩具游戏'),  # BURBUJERO UNICORNIO
    (18543, '玩具游戏'),  # BURBUJERO FORMA ESTRELLA TINY
    (18544, '玩具游戏'),  # BURBUJERO FORMA DINOSAURIO
    (18545, '玩具游戏'),  # BURBUJERO FROZEN
    (18546, '玩具游戏'),  # BURBUJERO SPIDERMAN
    (18547, '玩具游戏'),  # BURBUJERO X3 STITCH
    (18548, '玩具游戏'),  # BURBUJERO X 3 TOY STORY
    (18549, '玩具游戏'),  # BURBUJERO A PILA TINY BUBBLES
    (18550, '玩具游戏'),  # BURBUJERO PISTOLA A PILA
    (18551, '玩具游戏'),  # BURBUJERO PISTOLA ASTRONAUTA A PILA
    (18552, '玩具游戏'),  # BURBUJERO GRANDE A PILA NENA
    (18553, '玩具游戏'),  # BURBUJERO GRANDE A PILA NENE
    (18554, '玩具游戏'),  # SUPER BURBUJERO DE DINOSAURIOS
    (18555, '玩具游戏'),  # BURBUJERO DINOSAURIO TINY A PILA
    (18556, '玩具游戏'),  # BURBUJERO A PILA SPIDERMAN
    (18557, '玩具游戏'),  # BURBUJERO X3 SPIDERMAN
    (18558, '玩具游戏'),  # FISHING GAME
    (18559, '玩具游戏'),  # WATER GAME AFA
    (18560, '玩具游戏'),  # SQUISHY MINI UNICORNIO
    (18561, '玩具游戏'),  # SQUISHY UNICORNIO MEDIANO
    (18562, '玩具游戏'),  # SQUISHY UNICORNIO GRANDE
    (18563, '玩具游戏'),  # SQUISHY CUPCAKE
    (18564, '玩具游戏'),  # WATER GAME JOYSTICK UNICORNIO
    (18565, '玩具游戏'),  # WATER GAME SPIDERMAN
    (18566, '玩具游戏'),  # WATER GAME PRINCESAS
    (18567, '玩具游戏'),  # PIZARRA MAGICA UNICORNIO
    (18568, '玩具游戏'),  # TABLET TINY
    (18569, '玩具游戏'),  # PIZARRA MAGICA SPIDERMAN
    (18570, '玩具游戏'),  # CONJUNTO POLICIA
    (18571, '玩具游戏'),  # DINOSAURIO A PILA MECHANICAL
    (18572, '玩具游戏'),  # MEGA DINOSAURIO X-DINO A PILA
    (18573, '玩具游戏'),  # DINOSAURIO A PILA
    (18574, '玩具游戏'),  # DINOS EN BLISTER
    (18575, '玩具游戏'),  # HUEVO DINOSAURIO

    # 811-841: 玩具（运动/音乐/电子/首饰）
    (18576, '玩具游戏'),  # ARO DE BASQUET SPIDERMAN — 儿童篮球架
    (18577, '玩具游戏'),  # LANZA Y ATRAPA FUN PLAY
    (18578, '玩具游戏'),  # BOWLING GRANDE
    (18579, '玩具游戏'),  # BOWLING MEDIANO
    (18580, '玩具游戏'),  # BOWLING CHICO
    (18581, '玩具游戏'),  # TIRO CON DARDO EN CAJA
    (18582, '玩具游戏'),  # TIRO CON BOLITAS SPIDERMAN
    (18583, '玩具游戏'),  # ALAS MAGICAS CON LUZ Y SONIDO
    (18584, '玩具游戏'),  # SET DE PRINCESAS
    (18585, '玩具游戏'),  # VARITA PRINCESA LUZ Y SONIDO
    (18586, '玩具游戏'),  # SUPER MICROFONO STITCH
    (18587, '玩具游戏'),  # SUPER MOTO A CONTROL REMOTO
    (18588, '玩具游戏'),  # SET BARCO PIRATA CON ACCESORIOS
    (18589, '玩具游戏'),  # GAME POP STITCH
    (18590, '玩具游戏'),  # STITCH WATER GAME
    (18591, '玩具游戏'),  # GUITARRA MUSICAL TOY STORY
    (18592, '玩具游戏'),  # CAJA FUERTE GABBY DOLLHOUSE
    (18593, '玩具游戏'),  # CELULAR BABY GUS
    (18594, '玩具游戏'),  # TELEFONO BABY GUS
    (18595, '玩具游戏'),  # TROMPETA MUSICAL
    (18596, '玩具游戏'),  # WATER GAME ASTRONAUTA
    (18597, '玩具游戏'),  # TABLET TOY STORY
    (18598, '玩具游戏'),  # DINOSAURIO CON DARDOS
    (18599, '玩具游戏'),  # TINY BIJOU — 首饰玩具
    (18600, '玩具游戏'),  # SET BIJOUTERIE HELADO UNICORNIO
    (18601, '玩具游戏'),  # JUEGO MARIPOSA BIJOUTERIE
    (18602, '玩具游戏'),  # JUEGO BIJOUTERIE
    (18603, '玩具游戏'),  # JUEGO BIJOUTERIE
    (18604, '玩具游戏'),  # JUEGO BIJOUTERIE
    (18605, '玩具游戏'),  # PACK PARA ARMAR PULSERITAS
    (18606, '玩具游戏'),  # SET BIJOUTERIE FROZEN
    (18607, '玩具游戏'),  # SET BIJOUTERIE FROZEN

    # 843-877: 玩具（人偶/恐龙/机器人/早教/拼图/运动）
    (18608, '玩具游戏'),  # MUÑECO KEVIN PAPA CON COCHECITO Y BEBE
    (18609, '玩具游戏'),  # MUÑECO KEVIN EN CAJITA
    (18610, '玩具游戏'),  # MONSTRUO TRES CABEZAS
    (18611, '玩具游戏'),  # MONSTRUO DOS CABEZAS
    (18612, '玩具游戏'),  # AUTO TRANSFORMER
    (18613, '玩具游戏'),  # ROBOT AUTO TRANSFORMERS CHICO
    (18614, '玩具游戏'),  # TRANSFORMER MOBILE WARRIOR
    (18615, '玩具游戏'),  # ROBOT TRANSFORMER
    (18616, '玩具游戏'),  # MONSTER ANIMAL SHARK
    (18617, '玩具游戏'),  # MONSTER ANIMAL DINOSAUR
    (18618, '玩具游戏'),  # LEON MONSTER ANIMAL
    (18619, '玩具游戏'),  # PIANITO DIDACTICO UNICORNIO BABY GUS — 早教钢琴
    (18620, '玩具游戏'),  # PIANITO DIDACTICO MONITO BABY GUS
    (18621, '玩具游戏'),  # SET JUEGO AROS APILABLES — 叠圈
    (18622, '玩具游戏'),  # TORRE APILABLE MADERA — 木积木
    (18623, '玩具游戏'),  # JUEGO DE ENCASTRE MADERA — 拼插木玩具
    (18624, '玩具游戏'),  # JUEGO DIDACTICO ENCASTRE PARA VESTIR
    (18625, '玩具游戏'),  # JUEGO DIDACTICO ENCASTRE MADERA
    (18626, '玩具游戏'),  # JUEGO DIDACTICO ENCASTRE MADERA AUTOS
    (18627, '玩具游戏'),  # JUEGO DIDACTICO ENCASTRE MADERA MAR
    (18628, '玩具游戏'),  # ROMPECABEZA BABY GUS — 拼图
    (18629, '玩具游戏'),  # SET ARCO Y FLECHA SPIDERMAN
    (18630, '玩具游戏'),  # SET ARCO Y FLECHA BATMAN
    (18631, '玩具游戏'),  # SUPER ARCO Y FLECHA
    (18632, '玩具游戏'),  # ARCO DE FUTBOL EN CAJA — 儿童球门
    (18633, '运动户外'),  # FUTBOL TRAINING — 足球训练
    (18634, '运动户外'),  # SET DE PALETAS CON PELOTA — 乒乓球
    (18635, '运动户外'),  # JUEGO LANZA PELOTA
    (18636, '玩具游戏'),  # BARRILETE STITCH — 风筝
    (18637, '运动户外'),  # SOGA GABBY DOLLHOUSE — 跳绳
    (18638, '运动户外'),  # SOGA TINY JUMP — 跳绳
    (18639, '运动户外'),  # SOGA SALTAR TINY JUMP
    (18640, '运动户外'),  # PACK RAQUETA X2 + PELOTAS — 球拍
    (18641, '运动户外'),  # ARCO DE FUTBOL AFA — 球门

    # 877-882: NUVA 厨房用品
    (20167, '餐饮用品'),  # CESTA PROFUNDA CHICA NUVA — 深篮
    (20168, '餐饮用品'),  # CESTA PROFUNDA GRANDE NUVA

    # 879-933: TK 品牌玻璃器皿（逐条审查）
    (20169, '厨房储物'),  # FRASCO VIDRIO ALACENA 1900 ML TK — 储物罐
    (20170, '厨房储物'),  # FRASCO VIDRIO ALACENA 1200 ML TK
    (20171, '厨房储物'),  # FRASCO VIDRIO ALACENA 930 ML TK
    (20172, '电器电子'),  # BALANZA BAMBU DIGITAL COCINA TK — 电子厨房秤
    (20173, '电器电子'),  # BALANZA COCINA DIGITAL TK
    (20174, '餐饮用品'),  # PACK X6 WHISKY BORDE DORADO 315 CC — 威士忌杯
    (20175, '餐饮用品'),  # PACK X6 VASO DE AGUA FUSION TK
    (20176, '餐饮用品'),  # PACK X6 VASO BORDE DORADO 430 CC
    (20177, '餐饮用品'),  # PACK X6 VASO TRAGO LARGO 360 CC BELICE
    (20178, '餐饮用品'),  # PACK X6 VASO WHISKY AMBERES
    (20179, '餐饮用品'),  # PACK X6 VASO TRAGO LARGO 360 CC AMBERES
    (20180, '餐饮用品'),  # PACK X6 VASO TRAGO LARGO 360 CC COSTA
    (20181, '餐饮用品'),  # PACK X6 VASO WHISKY MALDIVAS
    (20182, '餐饮用品'),  # PACK X6 VASO WHISKY BELICE
    (20183, '餐饮用品'),  # PACK X6 VASO TRAGO LARGO 360 CC MALDIVAS
    (20184, '餐饮用品'),  # PACK X6 VASO WHISKY 360 CC COSTA
    (20185, '餐饮用品'),  # PACK X6 VASO TRAGO LARGO FUSION
    (20186, '餐饮用品'),  # PACK X6 VASO TRAGO LARGO LINES
    (20187, '餐饮用品'),  # PACK X6 COPA DE HELADO VIDRIO MARINE — 冰淇淋杯
    (20188, '餐饮用品'),  # PACK X6 COPA CHAMPAGNE BORDE DORADO — 香槟杯
    (20189, '餐饮用品'),  # PACK X6 COPA DE HELADO BORDE DORADO
    (20190, '餐饮用品'),  # PACK X6 COPA CHAMPAGNE TORNASOL
    (20191, '餐饮用品'),  # PACK X6 COPA DE VINO BORDE DORADO 270 CC — 葡萄酒杯
    (20192, '餐饮用品'),  # PACK X6 COPA CHAMPAGNE TORNASOL
    (20193, '餐饮用品'),  # PACK X3 COPA DE HELADO LINES
    (20194, '餐饮用品'),  # PACK X6 COPA VIDRIO 255 CC LINES
    (20195, '餐饮用品'),  # PACK X6 COPA VIDRIO 160CC LINES
    (20196, '餐饮用品'),  # PACK X6 COPA VINO 400 CC FUSION TRANS
    (20197, '餐饮用品'),  # PACK X6 COPA DE AGUA 500 CC FUSION
    (20198, '餐饮用品'),  # PACK X6 COPA DE AGUA 500 CC FUSION
    (20199, '餐饮用品'),  # PACK X6 COPA VINO 400 CC FUSION NEGRA
    (20200, '餐饮用品'),  # PACK X6 COPA DE VIDRIO LABRADO MARINE
    (20201, '餐饮用品'),  # CHOP VIDRIO PREMIUM 830 ML — 啤酒杯
    (20202, '餐饮用品'),  # JARRA VIDRIO TRAMADA 1 LT — 玻璃壶
    (20203, '餐饮用品'),  # BOTELLA TERMICA CON AGARRE 1 LITRO TK
    (20204, '餐饮用品'),  # BOTELLA DE ACERO CON AGARRE 1.2 LTS TK
    (20205, '餐饮用品'),  # BOTELLA DE ACERO CON AGARRE Y SORBETE 1.2 LTS
    (20206, '餐饮用品'),  # BOTELLA DOBLE PARED 720 ML TK
    (20207, '餐饮用品'),  # JARRA VIDRIO 1.3 LTS MARINE
    (20208, '餐饮用品'),  # HIELERA VIDRIO + PINZA OTAWA — 冰桶+夹
    (20209, '餐饮用品'),  # HIELERA VIDRIO + PINZA QUEBEC
    (20210, '餐饮用品'),  # SET X2 TAZA DE TE DOBLE PARED CON ASA — 茶杯套装
    (20211, '餐饮用品'),  # PACK TAZA CAFE X6 + 6 PLATITOS VIDRIO MARINE
    (20212, '餐饮用品'),  # SET X6 TAZAS 280 CC + 6 PLATOS VIDRIO MARINE
    (20213, '厨房炊具'),  # CAFETERA FRANCESA CON RAYAS 1000 CC TK — 法压壶
    (20214, '厨房炊具'),  # CAFETERA FRANCESA CON RAYAS 350 CC TK
    (20215, '厨房炊具'),  # CAFETERA PRENSA FRANCESA 1000 CC TK
    (20216, '厨房炊具'),  # CAFETERA PRENSA FRANCESA 800 CC TK
    (20217, '厨房炊具'),  # CAFETERA PRENSA FRANCESA 600 CC TK
    (20218, '厨房储物'),  # ESPECIERO BASE DE MADERA + 6 FRASCOS TK — 调料架
    (20219, '厨房储物'),  # ESPECIERO + 3 FRASCOS TK
    (20220, '厨房储物'),  # SET X2 BOTELLAS + 2 FRASCOS TK
    (20221, '厨房储物'),  # SET ACEITE Y VINAGRE + 2 ESPECIEROS EN BANDEJA BAMBU
    (20222, '厨房储物'),  # ESPECIERO + 6 FRASCOS TK
    (20223, '装饰品'),    # FLORERO 7.5 X 20 CM — 花瓶
    (20224, '装饰品'),    # FLORERO 7.5 X 18 CM
    (20225, '装饰品'),    # FLORERO 19 X 13 CM
    (20226, '装饰品'),    # FLORERO 8.5 X 20 CM
    (20227, '装饰品'),    # FLORERO 9.5 X 19 CM
    (20228, '厨房储物'),  # FRASCO VIDRIO FLORES TAPA PLASTICA 400 ML — 储物罐
    (20229, '厨房储物'),  # FRASCO VIDRIO FLORES TAPA PLASTICA 620 ML
    (20230, '厨房储物'),  # FRASCO VIDRIO FLORES TAPA PLASTICA 1200 ML
    (20231, '厨房储物'),  # FRASCO VIDRIO RAYA TAPA PLASTICA 400 ML
    (20232, '厨房储物'),  # FRASCO VIDRIO RAYA TAPA PLASTICA 620 ML
    (20233, '厨房储物'),  # FRASCO VIDRIO RAYA TAPA PLASTICA 1200 ML
    (20234, '餐饮用品'),  # PACK X6 VASO SILUETA GRIS
    (20235, '餐饮用品'),  # PACK X6 VASO SILUETA AMBAR
    (20236, '餐饮用品'),  # PACK X6 VASO SILUETA MULTICOLOR
    (20237, '餐饮用品'),  # MATE SOL ARGENTINA MIJO MADERA CON BOMBILLA
    (20238, '餐饮用品'),  # MATE VAMOS ARGENTINA MIJO MADERA CON BOMBILLA
    (20239, '餐饮用品'),  # GLASS DISPENSER TAPA BAMBU — 饮品分配器

    # 940-983: 厨房/收纳/清洁/容器
    (20240, '厨房炊具'),  # TACHO N1 FLORIDA 7LTS — 锅
    (20241, '厨房炊具'),  # TACHO N2 FLORIDA 12LTS
    (20242, '厨房炊具'),  # VAIVEN 6LTS DPH — 锅
    (20243, '清洁用品'),  # ESCOBILLA MANGO METALICO — 刷子
    (20244, '厨房储物'),  # SET HERMETICOS VERDURAS X3 SAN REMO
    (20245, '厨房储物'),  # TAPER KEEPING PUSH UP 1.1 LTS — 保鲜盒
    (20246, '厨房储物'),  # TAPER KEEPING PUSH UP 2 LTS
    (20247, '厨房储物'),  # TAPER PARA QUESO BAMBU — 奶酪保鲜盒
    (20248, '厨房储物'),  # TAPER FUNBOX SETX4
    (20249, '厨房储物'),  # SET TAPER MAGICLICK COLORES X5
    (20250, '厨房储物'),  # TAPER TRASLUCIDO COLOR X3
    (20251, '厨房储物'),  # TAPER ANIMALES SETX4
    (20252, '厨房储物'),  # TAPER TIPO LUNCHERA CON 2 DIVISIONES
    (20253, '厨房储物'),  # TAPER VIDRIO CUADRADO 1100 ML
    (20254, '厨房储物'),  # TAPER VIDRIO RECT 640 ML
    (20255, '厨房储物'),  # TAPER VIDRIO CUADRADO 320 ML
    (20256, '厨房储物'),  # TAPER VIDRIO REDONDO 400 ML
    (20257, '厨房储物'),  # TAPER VIDRIO CUADRADO 520 ML
    (20258, '厨房储物'),  # TAPER VIDRIO REDONDO 1300 ML
    (20259, '厨房储物'),  # TAPER VIDRIO CUADRADO 800 ML
    (20260, '厨房储物'),  # TAPER VIDRIO RECT 370 ML
    (20261, '厨房储物'),  # TAPER VIDRIO RECT 1050 ML
    (20262, '厨房储物'),  # TAPER VIDRIO RECT 1520 ML
    (20263, '厨房储物'),  # TAPER VIDRIO REDONDO 650 ML
    (20264, '厨房储物'),  # TAPER VIDRIO REDONDO 950 ML
    (20265, '厨房储物'),  # TAPER VIDRIO CUADRADO DIAMONDS 320 ML
    (20266, '厨房储物'),  # TAPER RECTANGULAR MEDIANO VIDRIO BAMBU
    (20267, '厨房储物'),  # TAPER RECTANGULAR GRANDE VIDRIO BAMBU
    (20268, '厨房餐具'),  # SET X 4 TAPER ENLOZADO — 搪瓷饭盒
    (20269, '厨房餐具'),  # SECAPLATOS REFORZADO DPH — 沥水架
    (20270, '厨房炊具'),  # CAFETERA FRANCESA CON RAYAS 600 CC TK

    # 981-994: 玩具重复/球类
    (20271, '玩具游戏'),  # MONSTER ANIMAL SHARK (重复)
    (20272, '玩具游戏'),  # SQUISHY UNICORNIO MEDIANO
    (20273, '玩具游戏'),  # SQUISHY UNICORNIO GRANDE
    (20274, '玩具游戏'),  # WATER GAME SPIDERMAN
    (20275, '玩具游戏'),  # JUEGO TOUCH GAME AFA
    (20276, '玩具游戏'),  # MUÑECA TINY CHEF CON ACCESORIOS
    (20277, '玩具游戏'),  # MUÑECA TINY CUTE
    (20278, '玩具游戏'),  # MUÑECA TINY WEDDING
    (20279, '玩具游戏'),  # PISTA LANZADORA + AUTO SPIDERMAN
    (20280, '玩具游戏'),  # PISTA DE TREN SPIDERMAN
    (20281, '玩具游戏'),  # BURBUJERO STITCH
    (20282, '玩具游戏'),  # SUPER BURBUJERO A PILA SPIDERMAN
    (20283, '玩具游戏'),  # BURBUJERO X3 AFA
    (20284, '运动户外'),  # SUPER ARCO DE FUTBOL AFA — 球门

    # 995-1018: 球类/玩具/文具
    (20459, '运动户外'),  # PELOTA SOFT GRANDE AFA
    (20460, '运动户外'),  # PELOTITA SOFT AFA
    (20461, '运动户外'),  # PELOTA FUTBOL N5 ARGENTINA
    (20462, '玩具游戏'),  # DESCUBRI QUIEN ES AFA — 桌游
    (20463, '运动户外'),  # METEGOL AFA — 桌式足球
    (20464, '玩具游戏'),  # YO-YO AFA
    (20465, '运动户外'),  # ENTRENAMIENTO FUTBOL AFA — 足球训练
    (20466, '玩具游戏'),  # CARTAS ESPAÑOLAS — 扑克牌
    (20467, '玩具游戏'),  # PELOTITAS SOFT SPIDERMAN
    (20468, '玩具游戏'),  # MUÑECA TINY TATI
    (20469, '玩具游戏'),  # MUÑECA TINY PIA
    (20470, '玩具游戏'),  # MUÑECA TINY DEBY
    (20471, '玩具游戏'),  # MUÑECA TINY FASHION CON OSITO
    (20472, '玩具游戏'),  # MUÑECA TINY DOCTORA
    (20473, '玩具游戏'),  # RUEDA LANZADORA + AUTO METALICO
    (20474, '美妆个护'),  # MAQUILLAJE UNICORNIO CON GLITTER
    (20475, '玩具游戏'),  # PISTOLA AIR GUN LANZA BOLAS Y DARDOS
    (20476, '玩具游戏'),  # TINY BUBBLES
    (20477, '玩具游戏'),  # POP IT STITCH
    (20478, '玩具游戏'),  # RADIO MUSICAL TOY STORY
    (20479, '玩具游戏'),  # SET DE ARTE FUTBOL 48 PIEZAS — 美术套装
    (20480, '玩具游戏'),  # SET DE ARTE OSITO 48 PIEZAS
    (20481, '玩具游戏'),  # POP IT SPIDERMAN
    (20482, '运动户外'),  # SOGA SALTAR STITCH — 跳绳

    # 1019-1107: 厨具/清洁/家居/玩具/花盆
    (24408, '厨房炊具'),  # CHISPERO ART — 点火器
    (24409, '清洁用品'),  # CEPILLO LIMPIA BOTELLA — 洗瓶刷
    (24410, '餐饮用品'),  # VASO PLASTICO NUVA — 塑料杯
    (24411, '厨房储物'),  # SET X4 TAPER VIDRIO REC EN CAJA JOVIFEL — 玻璃饭盒
    (24412, '厨房储物'),  # SET X4 TAPER VIDRIO RED EN CAJA JOVIFEL
    (24413, '厨房炊具'),  # TORTERA CORAZON N22 EL SIGLO — 心形蛋糕模
    (24414, '厨房炊具'),  # PAVA ENLOZADA ROJA — 搪瓷水壶
    (24415, '厨房炊具'),  # PAVA ENLOZADA NEGRA
    (24416, '餐饮用品'),  # JARRO ENLOZADO ROJO PESADO 8 CM — 搪瓷杯
    (24417, '餐饮用品'),  # JARRO ENLOZADO ROJO PESADO 14 CM
    (24418, '餐饮用品'),  # PLATO ENLOZADO 24 CM — 搪瓷盘
    (24419, '餐饮用品'),  # PLATO ENLOZADO 26 CM
    (24420, '清洁用品'),  # BATH SPONGE — 浴海绵
    (24421, '运动户外'),  # PELOTA PVC LIVIANA AFA
    (24422, '运动户外'),  # PACK RAQUETA X2 + PELOTAS AFA
    (24423, '装饰品'),    # RELOJ — 钟
    (24424, '装饰品'),    # MACETA SIMIL MADERA 24 — 花盆
    (24425, '装饰品'),    # MACETA SIMIL MADERA 16
    (24426, '装饰品'),    # MACETA SIMIL MADERA 20
    (24427, '清洁用品'),  # MOPA MICROFIBRA — 拖把
    (24428, '清洁用品'),  # PAÑO MICROFIBRA LAFFITE — 抹布
    (24429, '清洁用品'),  # ESPONJA MICROFIBRA ANTIGRASA — 去油海绵
    (24430, '文具办公'),  # ORGANIZADOR ESCRITORIO 5 DIVISIONES KUMA — 桌面收纳
    (24431, '收纳整理'),  # CANASTO OFERTA ECO LINE — 篮子
    (24432, '厨房炊具'),  # OLLA ALUMINIO N32 JESICA — 铝锅
    (24433, '厨房炊具'),  # OLLA ALUMINIO N34 JESICA
    (24434, '厨房炊具'),  # OLLA ALUMINIO N36 JESICA
    (24435, '厨房炊具'),  # OLLA ALUMINIO N38 JESICA
    (24436, '厨房炊具'),  # OLLA ALUMINIO N40 JESICA
    (24437, '厨房炊具'),  # OLLA ALUMINIO N50 JESICA
    (24438, '厨房炊具'),  # OLLA ALTA CHAROLADA N24 EL SIGLO — 搪瓷高锅
    (24439, '厨房炊具'),  # OLLA ALTA CHAROLADA N28 EL SIGLO
    (24440, '厨房炊具'),  # CACEROLA CHAROLADA N28 EL SIGLO — 搪瓷炖锅
    (24441, '厨房炊具'),  # CACEROLA CHAROLADA N20 EL SIGLO
    (24442, '厨房炊具'),  # CACEROLA CHAROLADA N24 EL SIGLO
    (24443, '厨房炊具'),  # CACEROLA ALUMINIO N32 JESICA
    (24444, '厨房炊具'),  # CACEROLA ALUMINIO N34 JESICA
    (24445, '厨房炊具'),  # CACEROLA ALUMINIO N36 JESICA
    (24446, '厨房炊具'),  # CACEROLA ALUMINIO N38 JESICA
    (24447, '厨房炊具'),  # CACEROLA ALUMINIO N40 JESICA
    (24448, '厨房炊制'),  # CACEROLA ALUMINIO N50 JESICA  # ⚠️ 笔误，后面修正
    (24449, '厨房炊具'),  # PIZZERA ALUMINIO N32 EL SIGLO — 披萨盘
    (24450, '厨房炊具'),  # PIZZERA REFORZADA ALUMINIO N35 EL SIGLO
    (24451, '厨房炊具'),  # TORTERA ALTA N28 EL SIGLO
    (24452, '厨房炊具'),  # TORTERA ALTA N30 EL SIGLO
    (24453, '厨房炊具'),  # TORTERA ALTA N32 EL SIGLO
    (24454, '厨房炊具'),  # SAVARIN ALTO N28 EL SIGLO — 环形模
    (24455, '厨房炊具'),  # SAVARIN ALTO N30 EL SIGLO
    (24456, '厨房炊具'),  # SAVARIN ALTO N32 EL SIGLO
    (24457, '厨房炊具'),  # BUDINERA SAVARIN N20 EL SIGLO
    (24458, '厨房炊具'),  # BUDINERA SAVARIN N22 EL SIGLO
    (24459, '厨房炊具'),  # BUDINERA SAVARIN N24 EL SIGLO
    (24460, '餐饮用品'),  # VASO NUVA CON MEDIDAS (1734)
    (24461, '厨房炊具'),  # PAVA CON ASA CHAROLADA N14 EL SIGLO — 搪瓷壶
    (24462, '厨房炊具'),  # PAVA CON ASA CHAROLADA N16 EL SIGLO
    (24463, '厨房炊具'),  # PAVA GASTRONOMICA CHAROLADA N22 JESICA
    (24464, '餐饮用品'),  # JARRO CON ASA CHAROLADO N10 EL SIGLO — 搪瓷杯
    (24465, '餐饮用品'),  # JARRO CON ASA CHAROLADO N12 EL SIGLO
    (24466, '餐饮用品'),  # JARRO CON ASA CHAROLADO N14 EL SIGLO
    (24467, '厨房炊具'),  # HERVIDOR CON ASA CHAROLADO N14 EL SIGLO — 烧水壶
    (24468, '厨房储物'),  # FRASCO CHICO REDONDO VIDRIO TAPA BAMBU JOVIFEL
    (24469, '厨房储物'),  # FRASCO MEDIANO REDONDO VIDRIO TAPA BAMBU JOVIFEL
    (24470, '厨房储物'),  # FRASCO GRANDE REDONDO VIDRIO TAPA BAMBU JOVIFEL
    (24471, '厨房炊具'),  # COLAPASTA CON ASA CHAROLADO N24 EL SIGLO — 滤面锅
    (24472, '厨房餐具'),  # CUCHARON GASTRONOMICO JESICA — 汤勺
    (24473, '厨房餐具'),  # ESPUMADERA GASTRONOMICA JESICA — 漏勺
    (24474, '厨房餐具'),  # ESPATULA MANGO ACRILICO EN BLISTER
    (24475, '厨房餐具'),  # CORTA PIZZA MANGO MADERA
    (24476, '装饰品'),    # ALFOMBRA 40*60 100% ALGODON — 地毯
    (24477, '餐饮用品'),  # VASO STARBUCKS SIN TAPA — 星巴克杯
    (24478, '餐饮用品'),  # VASO FERNETOMETRO SIN ASA EL SIGLO — 量杯
    (24479, '餐饮用品'),  # VASO FERNETOMETRO CON ASA EL SIGLO
    (24480, '餐饮用品'),  # FERNETOMETRO ALUMINIO
    (24481, '餐饮用品'),  # BOTELLA 1 LT VIDRIO TAPA CORCHO PLUS
    (24482, '厨房炊具'),  # CAFETERA CON ASA CHAROLADA 1LT EL SIGLO — 搪瓷咖啡壶
    (24483, '厨房炊具'),  # CAFETERA CON ASA CHAROLADA 1.5 LTS EL SIGLO
    (24484, '装饰品'),    # ALFOMBRA BATH — 浴室垫
    (24485, '卫浴用品'),  # TAPON BACHA MANITO CLIKER — 水槽塞
    (24486, '玩具游戏'),  # ANDARIN DAKOTA NENE — 学步车
    (24487, '玩具游戏'),  # ANDARIN DAKOTA NENA
    (24488, '美妆个护'),  # MAQUILLAJE (SB3282)
    (24489, '运动户外'),  # PELOTA FUTBOL KANTO CYCLON SIZE 5
    (24490, '运动户外'),  # PELOTA FUTBOL KANTO SIZE 5
    (24491, '玩具游戏'),  # TINY BUBBLES ESPIRAL
    (24492, '玩具游戏'),  # MUÑECA TINY PINTA SU VESTIDO
    (24493, '装饰品'),    # MACETA RIGA 25 — 花盆
    (24494, '装饰品'),    # MACETA RIGA 29
    (24495, '装饰品'),    # MACETA SIMIL MADERA 28
    (24496, '装饰品'),    # MACETA SIMIL MADERA 35
]

# 修正笔误
for i, (pid, cat) in enumerate(CLASSIFICATIONS):
    if cat == '厨房炊制':
        CLASSIFICATIONS[i] = (pid, '厨房炊具')

# ═══════════════════════════════════════════════════════════════
# 写入数据库
# ═══════════════════════════════════════════════════════════════

conn = pymysql.connect(
    host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler',
    charset='utf8mb4'
)
cur = conn.cursor()

updated = 0
for pid, cat in CLASSIFICATIONS:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
    updated += cur.rowcount
conn.commit()
print(f"写入: {updated}/{len(CLASSIFICATIONS)} 条")

# 检查剩余
cur.execute("""
    SELECT id, name FROM products
    WHERE supplier_id=3 AND (category IS NULL OR category='')
      AND is_available=1
    ORDER BY id
""")
remaining = cur.fetchall()
print(f"\n剩余未分类: {len(remaining)} 条")
for pid, name in remaining:
    print(f"  ID:{pid}  {name}")

conn.close()
