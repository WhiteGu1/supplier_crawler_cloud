"""
重新分类脚本：将扁平分类迁移为 "一级 > 二级" 层级格式
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# 旧分类 -> 新分类 映射
CATEGORY_MAP = {
    # 厨房用品
    "厨房餐具":   "厨房用品 > 餐具",
    "厨房炊具":   "厨房用品 > 炊具",
    "厨房储物":   "厨房用品 > 储物保鲜",
    "餐饮用品":   "厨房用品 > 餐饮水具",
    # 家居生活
    "卫浴用品":   "家居生活 > 卫浴用品",
    "清洁用品":   "家居生活 > 清洁用品",
    "家居清洁":   "家居生活 > 清洁用品",
    "收纳整理":   "家居生活 > 收纳整理",
    "家居收纳":   "家居生活 > 收纳整理",
    "家居纺织":   "家居生活 > 家纺毛巾",
    "家居家具":   "家居生活 > 家具",
    "家居百货":   "家居生活 > 家居杂货",
    "个人防护":   "家居生活 > 个人防护",
    "园艺户外":   "家居生活 > 园艺户外",
    # 电子电器
    "照明灯具":   "电子电器 > 照明灯具",
    "电器电子":   "电子电器 > 小家电",
    "数码科技":   "电子电器 > 数码配件",
    # 玩具
    "玩具游戏":   "玩具 > 玩具游戏",
    # 文具
    "文具办公":   "文具 > 文具办公",
    # 化妆品饰品
    "时尚配饰":   "化妆品饰品 > 时尚配饰",
    "美妆个护":   "化妆品饰品 > 美妆个护",
    # 箱包皮具
    "箱包配件":   "箱包皮具 > 箱包配件",
    "旅行用品":   "箱包皮具 > 旅行用品",
    # 摆件礼品
    "家居装饰":   "摆件礼品 > 装饰摆件",
    "装饰品":     "摆件礼品 > 装饰摆件",
    "派对用品":   "摆件礼品 > 派对节庆",
    "圣诞用品":   "摆件礼品 > 派对节庆",
    "季节商品":   "摆件礼品 > 季节商品",
    # 服装鞋帽
    "服装服饰":   "服装鞋帽 > 服装服饰",
    "鞋履护理":   "服装鞋帽 > 鞋履护理",
    # 五金
    "五金工具":   "五金 > 五金工具",
    "针线缝纫":   "五金 > 缝纫针线",
    # 运动户外
    "运动户外":   "运动户外 > 运动健身",
    # 母婴用品
    "婴幼儿用品": "母婴用品 > 婴幼儿用品",
    # 宠物
    "宠物用品":   "宠物 > 宠物用品",
    # 杂货
    "日用百货":   "杂货 > 日用百货",
    "其他":       "杂货 > 其他",
    "食品饮料":   "杂货 > 食品饮料",
}

def main():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
    cur = conn.cursor()

    # 先统计当前状态
    cur.execute("SELECT COUNT(*) FROM products WHERE is_available=1 AND category!=''")
    total = cur.fetchone()[0]
    print(f"待迁移商品总数: {total}")

    # 检查是否有未映射的分类
    cur.execute("SELECT DISTINCT category FROM products WHERE is_available=1 AND category!=''")
    existing_cats = [r[0] for r in cur.fetchall()]
    unmapped = [c for c in existing_cats if c not in CATEGORY_MAP]
    if unmapped:
        print(f"⚠️ 未映射的分类: {unmapped}")
        return

    # 执行迁移
    updated = 0
    for old_cat, new_cat in CATEGORY_MAP.items():
        cur.execute(
            "UPDATE products SET category=%s WHERE category=%s AND is_available=1",
            (new_cat, old_cat)
        )
        affected = cur.rowcount
        if affected > 0:
            print(f"  {old_cat:12s} -> {new_cat:20s}  ({affected} 条)")
        updated += affected

    conn.commit()
    print(f"\n✅ 迁移完成，共更新 {updated} 条")

    # 验证
    cur.execute("SELECT DISTINCT category FROM products WHERE is_available=1 AND category!='' ORDER BY category")
    new_cats = [r[0] for r in cur.fetchall()]
    print(f"\n新分类列表 ({len(new_cats)} 个):")
    for c in new_cats:
        cur.execute("SELECT COUNT(*) FROM products WHERE category=%s AND is_available=1", (c,))
        cnt = cur.fetchone()[0]
        print(f"  {cnt:5d}  {c}")

    # 统计一级分类
    cur.execute("""
        SELECT SUBSTRING_INDEX(category, ' > ', 1) as main_cat, COUNT(*) as cnt
        FROM products WHERE is_available=1 AND category!=''
        GROUP BY main_cat ORDER BY cnt DESC
    """)
    print(f"\n一级分类统计:")
    for r in cur.fetchall():
        print(f"  {r[1]:5d}  {r[0]}")

    conn.close()

if __name__ == "__main__":
    main()
