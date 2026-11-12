# -*- coding: utf-8 -*-
import sys
import re
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

# 1. 抓取 Trapoman 候选商品
cur.execute("""
    SELECT p.id, p.name, p.price, p.category, p.description
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

print(f"Candidates from Trapoman: {len(candidates)}")
print(f"Gaston products: {len(gaston_prods)}")

# 提取关键词词根做初步匹配分析
stop_words = {'de', 'con', 'para', 'en', 'x', 'x2', 'x3', 'x4', 'x5', 'x6', 'chico', 'grande', 'mediano', 'color', 'la', 'el', 'los', 'las', 'un', 'una', 'art', 'cm', 'lts', 'cc', 'grs', 'y', 'del', 'al', 'nuevo', 'nueva', 'super', 'oferta', 'detalles'}

def get_keywords(name):
    # 去除括号内容
    cleaned = re.sub(r'\(.*?\)', '', name)
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned).lower()
    tokens = [w for w in cleaned.split() if len(w) >= 3 and w not in stop_words and not w.isdigit()]
    return set(tokens)

matches = []
for c in candidates:
    c_kw = get_keywords(c['name'])
    c_price = float(c['price'])
    max_price = c_price * 1.10  # 价格不超过10%
    
    c_matches = []
    for g in gaston_prods:
        g_kw = get_keywords(g['name'])
        common = c_kw & g_kw
        if common:
            g_price = float(g['price'])
            # 检查价格是否 <= max_price
            price_ok = (g_price <= max_price)
            # 计算相似度分
            score = len(common)
            # 核心品类词（如 percha, jabonera, vaso, embudo, repasador, trapo, rejilla, etc.）
            c_matches.append({
                'gaston': g,
                'common_kw': list(common),
                'score': score,
                'g_price': g_price,
                'c_price': c_price,
                'price_ok': price_ok,
                'diff_pct': ((g_price - c_price) / c_price) * 100
            })
    
    if c_matches:
        # 按关键词重合数降序，且价格符合优先
        c_matches.sort(key=lambda x: (x['price_ok'], x['score'], -abs(x['diff_pct'])), reverse=True)
        matches.append((c, c_matches))

print(f"\n找到潜在关键词关联的 Trapoman 商品数: {len(matches)} / {len(candidates)}")

for c, mlist in matches:
    valid_m = [m for m in mlist if m['price_ok']]
    print(f"\n--------------------------------------------------")
    print(f"Trapoman: [{c['id']}] {c['name']} | 价格: ${float(c['price']):.2f} (上限+10%: ${float(c['price'])*1.10:.2f})")
    print(f"  符合价格条件的目标数: {len(valid_m)} / 总重合候选: {len(mlist)}")
    for m in mlist[:5]:
        status = "【符合价格条件】" if m['price_ok'] else "【超出价格限制】"
        g = m['gaston']
        print(f"    -> {status} Gaston [{g['id']}] {g['name']} | 价格: ${m['g_price']:.2f} ({m['diff_pct']:+.1f}%) | 关键词: {m['common_kw']}")

conn.close()
