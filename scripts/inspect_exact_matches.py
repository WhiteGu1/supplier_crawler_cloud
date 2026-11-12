import pymysql

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

items_to_report = [
    {
        "input_code": "art/405",
        "inv_desc": "MASCARA CAPILAR ALMENDRAS 270G FIDELITE ($4,350, 4罐)",
        "pid": 45887,
        "note": "完全匹配：发票 ART/405 即为 Fidelite 杏仁发膜，网站SKU存的是 71261"
    },
    {
        "input_code": "art/403",
        "inv_desc": "MASCARA CAPILAR KERATINA 270G FIDELITE ($4,400, 4罐)",
        "pid": 45884,
        "note": "完全匹配：发票 ART/403 即为 Fidelite 角蛋白发膜，网站SKU存的是 71269"
    },
    {
        "input_code": "sku tei18383",
        "inv_desc": "C*6 SOMBRA PALETA ($8,300, 12盘)",
        "pid": 40934,
        "note": "完全匹配：发票 TE18383 即为 TEI 48色眼影盘(TEI8383/16978)，网站SKU存的是 194272"
    },
    {
        "input_code": "dh509-222",
        "inv_desc": "MASCARILLA FACIAL KAKAZIYAN ($500, 60片)",
        "pid": 44123,
        "note": "完全匹配：发票 DH509-222 即为卡通动物面膜(36型DH509-222/223/224)，网站SKU存的是 133757"
    },
    {
        "input_code": "14625",
        "inv_desc": "SKALA MAYONESA 1000GR ($4,600, 8罐)",
        "pid": 43284,
        "note": "完全匹配：发票 14625 为 Skala 蛋黄酱发膜的厂家条码款号，网站SKU存的是 156192"
    },
    {
        "input_code": "k3086/k3082",
        "inv_desc": "MASCARILLA TEI MMTEI ($550, 30片)",
        "pid": 42470,
        "note": "完全匹配：发票 K3086/K3082 为 TEI 补水面膜混装出货款式，网站SKU存的是 174000"
    },
    {
        "input_code": "sku dh-lso5",
        "inv_desc": "CAJA 12PCS DELINEADOR EN FIBRA ($5,000, 2盒)",
        "pid": 43990,
        "note": "完全匹配：发票打印为 DH-L505 (OCR误识别为DH-LSO5)，条码8972423632101，网站SKU存的是 136314"
    },
    {
        "input_code": "sku 969955",
        "inv_desc": "BASE DE MAQUILLAJE PINK 21 ($1,900, 24支)",
        "pid": 43869, # also 44029 in cart
        "note": "对应商品：Pink 21 $1900底妆系列(网站SKU 141190)；购物车下单的类似款为 CS3403(SKU 135823, PID 44029)"
    },
    {
        "input_code": "sku dh80058",
        "inv_desc": "C*36 MASCARA MINI TANGO ($1,100, 36支)",
        "pid": 43704,
        "note": "对应商品：Mini Tango 睫毛膏系列(条码尾号81152)，购物车下单对应款为 DH-MT-M342(SKU 144541, Qty 36)"
    },
    {
        "input_code": "sku tei18364",
        "inv_desc": "C*24 LABIAL ($1,500, 24支)",
        "pid": None,
        "note": "对应商品：TEI 哑光唇膏/口红(条码 6971968516763)，单价 $1500，线下按批次实配"
    },
    {
        "input_code": "dh75114",
        "inv_desc": "DELINEADOR LIQUIDO ($1,150, 24支)",
        "pid": None,
        "note": "对应商品：DH系列液体眼线液(单价 $1,150)，线下出库款号 DH75114"
    },
    {
        "input_code": "dh-bqy42576",
        "inv_desc": "MASCARILLA FACIAL ($600, 36片)",
        "pid": 43118,
        "note": "对应商品：Bioaqua $600 补水面膜系列(购物车中为莲花面膜 PID 43118/SKU 158840 及蜂蜜面膜 PID 43122/SKU 158817)"
    },
    {
        "input_code": "dh-bqy40602",
        "inv_desc": "MASCARILLA FACIAL ($600, 30片)",
        "pid": 43122,
        "note": "对应商品：Bioaqua $600 补水黑面膜/竹炭系列，同属于 Bioaqua 单片面膜(网站SKU 158817/126658)"
    }
]

with conn.cursor() as cur:
    for item in items_to_report:
        pid = item['pid']
        if pid:
            cur.execute("SELECT * FROM products WHERE id = %s", (pid,))
            prod = cur.fetchone()
            cur.execute("SELECT * FROM cart_items WHERE product_id = %s", (pid,))
            cart = cur.fetchone()
            item['prod'] = prod
            item['cart'] = cart
        else:
            item['prod'] = None
            item['cart'] = None

print("Inspection completed.")
