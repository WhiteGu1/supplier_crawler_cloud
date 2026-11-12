import pymysql, sys, re, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 标准化函数：去除所有空格、特殊字符，转大写，去除重音
def normalize(s):
    if not s:
        return ''
    # 去除重音
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    # 去除所有非字母数字
    s = re.sub(r'[^A-Za-z]', '', s)
    return s.upper()

# 仅处理剩余6个分类
fix_map = {
    'TERMICOS': '厨房储物',        # 保温瓶/保温容器
    'DECORACION': '家居装饰',       # 装饰品
    'ARTICULOSDEVIAJE': '旅行用品',  # 旅行用品
    'MUNECAS': '玩具游戏',          # 洋娃娃
    'BANO': '卫浴用品',             # 浴室用品
    'ARTICULOSPARABEBE': '婴幼儿用品', # 婴儿用品
}

# 获取剩余非标准分类
std_categories = (
    '厨房餐具','厨房炊具','厨房储物','餐饮用品','清洁用品','卫浴用品',
    '装饰品','收纳整理','日用百货','文具办公','个人防护','电器电子',
    '美妆个护','玩具游戏','派对用品','宠物用品','季节商品','婴幼儿用品',
    '运动户外','其他','五金工具','照明灯具','鞋履护理','食品饮料',
    '数码科技','箱包配件','家居纺织','家居家具','家居收纳','家居清洁',
    '家居百货','家居装饰','旅行用品','时尚配饰','服装服饰','针线缝纫',
    '园艺户外','圣诞用品'
)

cur.execute("""
    SELECT DISTINCT category FROM products 
    WHERE supplier_id=10 AND category NOT IN (%s)
""" % ','.join(['%s']*len(std_categories)), std_categories)
remaining_cats = [r[0] for r in cur.fetchall()]

updated = 0
for cat in remaining_cats:
    norm = normalize(cat)
    if norm in fix_map:
        std_cat = fix_map[norm]
        cur.execute("UPDATE products SET category=%s WHERE supplier_id=10 AND category=%s", (std_cat, cat))
        updated += cur.rowcount
        print(f"  '{cat}' -> '{std_cat}': {cur.rowcount}条")
    else:
        print(f"  未匹配: '{cat}' (norm: '{norm}')")

conn.commit()
print(f"\n已更新: {updated} 条")

# 最终检查
cur.execute("""
    SELECT COUNT(*) FROM products 
    WHERE supplier_id=10 AND category NOT IN (%s)
""" % ','.join(['%s']*len(std_categories)), std_categories)
final_remaining = cur.fetchone()[0]
print(f"最终非标准分类剩余: {final_remaining}")

# 最终分布
cur.execute("""
    SELECT category, COUNT(*) as cnt FROM products 
    WHERE supplier_id=10 
    GROUP BY category ORDER BY cnt DESC
""")
rows = cur.fetchall()
print(f"\nKK最终分类分布 ({len(rows)} 个):")
for r in rows:
    print(f"  {r[0]:<20} {r[1]:>5}")

conn.close()
