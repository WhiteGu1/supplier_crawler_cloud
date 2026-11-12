import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 检查KK是否已经过分类统一
cur.execute("""
    SELECT category, COUNT(*) as cnt 
    FROM products WHERE supplier_id=10 
    GROUP BY category ORDER BY cnt DESC LIMIT 50
""")
rows = cur.fetchall()
print("KK分类分布（前50）:")
for r in rows:
    print(f"  '{r[0]}' -> {r[1]}")

# 检查是否已是中文分类
cur.execute("""
    SELECT COUNT(*) FROM products 
    WHERE supplier_id=10 AND category IN (
        '厨房餐具','厨房炊具','厨房储物','餐饮用品','清洁用品','卫浴用品',
        '装饰品','收纳整理','日用百货','文具办公','个人防护','电器电子',
        '美妆个护','玩具游戏','派对用品','宠物用品','季节商品','婴幼儿用品',
        '运动户外','其他','五金工具','照明灯具','鞋履护理','食品饮料',
        '数码科技','箱包配件','家居纺织','家居家具','家居收纳','家居清洁',
        '家居百货','家居装饰','旅行用品','时尚配饰','服装服饰','针线缝纫',
        '园艺户外','圣诞用品'
    )
""")
std = cur.fetchone()[0]
print(f"\n已是标准中文分类: {std}")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=10")
total = cur.fetchone()[0]
print(f"非标准分类: {total - std}")

# 有图商品数量
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=10 AND image_local IS NOT NULL AND image_local != ''")
has_img = cur.fetchone()[0]
print(f"\n有图: {has_img}")
print(f"无图: {total - has_img}")

# 看有图商品的分类情况
cur.execute("""
    SELECT COUNT(*) FROM products 
    WHERE supplier_id=10 AND image_local IS NOT NULL AND image_local != ''
    AND category NOT IN (
        '厨房餐具','厨房炊具','厨房储物','餐饮用品','清洁用品','卫浴用品',
        '装饰品','收纳整理','日用百货','文具办公','个人防护','电器电子',
        '美妆个护','玩具游戏','派对用品','宠物用品','季节商品','婴幼儿用品',
        '运动户外','其他','五金工具','照明灯具','鞋履护理','食品饮料',
        '数码科技','箱包配件','家居纺织','家居家具','家居收纳','家居清洁',
        '家居百货','家居装饰','旅行用品','时尚配饰','服装服饰','针线缝纫',
        '园艺户外','圣诞用品'
    )
""")
non_std_has_img = cur.fetchone()[0]
print(f"有图且非标准分类: {non_std_has_img}")

conn.close()
