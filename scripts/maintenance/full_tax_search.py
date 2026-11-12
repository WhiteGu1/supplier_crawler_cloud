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

# 2. 抓取 Gaston 全部在售商品并算上 10.5% 额外税
cur.execute("""
    SELECT id, sku, name, price, category
    FROM products
    WHERE supplier_id = 16 AND is_available = 1 AND price > 0
""")
gaston_prods = cur.fetchall()

# 核心品类名词词典
PRODUCT_NOUNS = {
    'percha': ['percha', 'perchas', 'perchero', 'perchita'],
    'gancho': ['gancho', 'ganchos'],
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
    'hermetico': ['hermetico', 'hermeticos', 'tupper', 'box viandas'],
    'salero': ['salero', 'saleros', 'pimentero', 'pimenteros', 'salsero'],
    'tapon': ['tapon', 'tapones', 'tapa'],
    'tope': ['tope', 'topetina', 'aplique adhesivo'],
    'guantes': ['guantes', 'guante'],
    'rociador': ['rociador', 'pulverizador', 'atomizador'],
    'mamadera': ['mamadera', 'mamaderas', 'biberon']
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

TAX = 1.105

print(f"Trapoman candidates: {len(candidates)}, Gaston products: {len(gaston_prods)}")

qualified = []
for c in candidates:
    c_nouns = identify_noun(c['name'])
    if not c_nouns:
        continue
    c_price = float(c['price'])
    max_price = c_price * 1.10
    
    for g in gaston_prods:
        g_nouns = identify_noun(g['name'])
        common = c_nouns & g_nouns
        if common:
            g_raw = float(g['price'])
            g_adj = g_raw * TAX
            if g_adj <= max_price:
                # 排除一些不相干假阳性（比如 aguja - canasta, cepillo de pestañas 等）
                if 'aguja' in g['name'].lower() or 'pestaña' in g['name'].lower() or 'alfiler' in g['name'].lower():
                    continue
                diff_pct = ((g_adj - c_price) / c_price) * 100
                qualified.append({
                    'gaston_id': g['id'],
                    'sku': g['sku'],
                    'gaston_name': g['name'],
                    'g_raw': g_raw,
                    'g_adj': g_adj,
                    'trapoman_id': c['id'],
                    'trapoman_name': c['name'],
                    't_price': c_price,
                    'diff_pct': diff_pct,
                    'noun': list(common)
                })

print(f"Total qualified matches with 10.5% tax: {len(qualified)}")
# 按 Gaston ID 去重
unique_g = {}
for q in qualified:
    gid = q['gaston_id']
    if gid not in unique_g or q['diff_pct'] < unique_g[gid]['diff_pct']:
        unique_g[gid] = q

print(f"Unique Gaston products: {len(unique_g)}")
for gid, item in sorted(unique_g.items(), key=lambda x: x[1]['diff_pct']):
    print(f"[{gid}] {item['sku']} | 原价:${item['g_raw']:.2f} -> 税后:${item['g_adj']:.2f} (对标 T[{item['trapoman_id']}] ${item['t_price']:.2f}, {item['diff_pct']:+.1f}%) | {item['gaston_name']}")

conn.close()
