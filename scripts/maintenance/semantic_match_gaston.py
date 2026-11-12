# -*- coding: utf-8 -*-
import sys
import re
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

# 1. 抓取 Trapoman 收藏中的非玩具商品
cur.execute("""
    SELECT p.id, p.name, p.price, p.category
    FROM favorites f
    JOIN products p ON f.product_id = p.id
    WHERE p.supplier_id = 3
    ORDER BY f.id
""")
favs = cur.fetchall()
toy_keywords = ['juego mesa', 'burbujero', 'pelota', 'damas', 'ajedrez', 'ludo', 'pool table', 'bijouterie', 'muñeca', 'juguete', 'pistola agua', 'inflable']
candidates = [f for f in favs if not ('玩具' in (f['category'] or '') or any(k in f['name'].lower() for k in toy_keywords))]

# 2. 抓取 Gaston 全部商品
cur.execute("""
    SELECT id, sku, name, price, category, image_url
    FROM products
    WHERE supplier_id = 16 AND is_available = 1
""")
gaston_prods = cur.fetchall()

# 定义核心品类名词词典（同义词/核心词归一化映射）
PRODUCT_NOUNS = {
    'percha': ['percha', 'perchas', 'perchero', 'perchita'],
    'jabonera': ['jabonera', 'jaboneras'],
    'vaso': ['vaso', 'vasos', 'jarrito', 'taza', 'tazas'],
    'embudo': ['embudo', 'embudos'],
    'colador': ['colador', 'coladores', 'coladorcito'],
    'paño': ['paño', 'paños', 'trapo', 'trapos', 'rejilla', 'rejillas', 'bayeta', 'franela', 'mopa'],
    'toalla': ['toalla', 'toallas', 'toallita', 'repasador', 'repasadores'],
    'canasto': ['canasto', 'canasta', 'cesta', 'cesto'],
    'organizador': ['organizador', 'organizadores', 'caja organizadora', 'storage basket'],
    'molde': ['molde', 'moldes', 'budinera', 'pizzera'],
    'cepillo': ['cepillo', 'cepillos', 'cepillito', 'escoba', 'escobita', 'escobilla'],
    'esponja': ['esponja', 'esponjas', 'fibra esponja'],
    'hermetico': ['hermetico', 'hermeticos', 'tupper', 'box viandas', 'bowl'],
    'salero': ['salero', 'saleros', 'pimentero', 'pimenteros', 'salsero'],
    'tapon': ['tapon', 'tapones', 'tapa', 'topetina', 'tope'],
    'guantes': ['guantes', 'guante'],
    'rociador': ['rociador', 'pulverizador', 'atomizador'],
    'mamadera': ['mamadera', 'mamaderas', 'biberon'],
    'portacepillo': ['porta cepillo', 'dispenser dentrifico']
}

def identify_noun(name):
    nl = name.lower()
    found = set()
    for category_key, synonyms in PRODUCT_NOUNS.items():
        for syn in synonyms:
            if re.search(r'\b' + re.escape(syn) + r'\b', nl):
                found.add(category_key)
                break
    return found

print("=== 分析 Trapoman 53 个商品的品类词 ===")
c_with_nouns = []
for c in candidates:
    nouns = identify_noun(c['name'])
    c_with_nouns.append((c, nouns))
    print(f"[{c['id']:5d}] ${float(c['price']):7.2f} | 品类: {list(nouns) if nouns else '未识别'} | {c['name']}")

print("\n=== 分析 Gaston 对应的同类商品与价格 ===")
matched_results = []
for c, c_nouns in c_with_nouns:
    if not c_nouns:
        continue
    c_price = float(c['price'])
    max_price = c_price * 1.10
    
    # 查找 Gaston 中有交集品类名词的商品
    same_type_gaston = []
    for g in gaston_prods:
        g_nouns = identify_noun(g['name'])
        if c_nouns & g_nouns:
            g_price = float(g['price'])
            if g_price <= 0: # 过滤无效价格
                continue
            same_type_gaston.append({
                'gaston': g,
                'g_price': g_price,
                'diff_pct': ((g_price - c_price) / c_price) * 100,
                'price_ok': g_price <= max_price,
                'shared_noun': list(c_nouns & g_nouns)
            })
    
    if same_type_gaston:
        # 只要价格符合要求的
        valid_matches = [m for m in same_type_gaston if m['price_ok']]
        if valid_matches:
            # 按价差从小到大排序
            valid_matches.sort(key=lambda x: x['g_price'])
            matched_results.append((c, valid_matches))

print(f"\n成功找到同品类且价格<=110%的商品对: {len(matched_results)} 组")

for c, valids in matched_results:
    print(f"\n[Trapoman] ID:{c['id']} ${float(c['price']):.2f} | {c['name']}")
    for vm in valids[:4]:
        g = vm['gaston']
        print(f"   --> Gaston [ID:{g['id']}] SKU:{g['sku']} ${vm['g_price']:.2f} ({vm['diff_pct']:+.1f}%) | {g['name']}")

conn.close()
