# -*- coding: utf-8 -*-
"""
清理历史遗留的非标准三级分类
- 将旧的2级路径或旧命名精确映射到 standard_categories.json 规范三级路径
- 更新 products.category (使用 updated_at = updated_at 保护时间戳)
- 更新/替换 product_categories 表中的遗留分类
- 确保整个数据库中 100% 的分类路径都在 270 条标准分类中
"""
import os
import sys
import json
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"D:\projects\supplier_crawler"
STD_CATS_FILE = os.path.join(BASE_DIR, "scripts", "classification_batches", "standard_categories.json")

with open(STD_CATS_FILE, "r", encoding="utf-8") as f:
    STANDARD_CATS = json.load(f)

STD_SET = set(STANDARD_CATS)

LEGACY_MAP = {
    # 2级遗留路径映射到标准3级
    "五金 > 五金工具": "五金 > 五金工具 > 五金工具",
    "化妆品饰品 > 时尚配饰": "化妆品饰品 > 时尚配饰 > 首饰",
    "化妆品饰品 > 美妆个护": "化妆品饰品 > 美妆个护 > 护肤/化妆品",
    "厨房用品 > 储物保鲜": "厨房用品 > 储物保鲜 > 保鲜盒/储物罐",
    "厨房用品 > 储物保鲜 > 保鲜盒/储能罐": "厨房用品 > 储物保鲜 > 保鲜盒/储物罐",
    "厨房用品 > 炊具": "厨房用品 > 炊具 > 厨房工具",
    "厨房用品 > 烘焙器具 > 烘焙模具": "厨房用品 > 炊具 > 模具/烤模",
    "厨房用品 > 餐具": "厨房用品 > 餐具 > 其他餐具",
    "厨房用品 > 餐饮水具": "厨房用品 > 餐饮水具 > 水瓶/水壶",
    "宠物 > 宠物用品": "宠物 > 宠物用品 > 宠物用品",
    "家居生活 > 卫浴用品": "家居生活 > 卫浴用品 > 其他卫浴",
    "家居生活 > 浴室用品 > 浴帘": "家居生活 > 卫浴用品 > 浴帘",
    "家居生活 > 浴室用品 > 防滑垫": "家居生活 > 卫浴用品 > 浴室地垫",
    "家居生活 > 家纺 > 家纺": "家居生活 > 家纺毛巾 > 毯子/床品",
    "家居生活 > 收纳整理": "家居生活 > 收纳整理 > 收纳盒",
    "家居生活 > 日用杂货": "家居生活 > 日用杂货 > 其他杂货",
    "家居生活 > 清洁用品": "家居生活 > 清洁用品 > 清洁工具",
    "摆件礼品 > 派对节庆": "摆件礼品 > 派对节庆 > 派对用品",
    "摆件礼品 > 派对用品 > 派对装饰": "摆件礼品 > 派对节庆 > 派对用品",
    "摆件礼品 > 装饰摆件": "摆件礼品 > 装饰摆件 > 装饰摆件",
    "文具 > 办公文具 > 办公文具": "文具 > 文具办公 > 办公文具",
    "文具 > 办公文具 > 文具包": "文具 > 文具办公 > 笔筒/笔袋",
    "文具 > 文具办公": "文具 > 文具办公 > 其他文具",
    "服装鞋帽 > 鞋帽 > 鞋帽": "服装鞋帽 > 服装服饰 > 帽子",
    "电子电器 > 小家电": "电子电器 > 小家电 > 小家电",
    "电子电器 > 照明灯具": "电子电器 > 照明灯具 > LED灯",
    "箱包皮具 > 箱包 > 包袋": "箱包皮具 > 箱包配件 > 手提包/斜挎包",
    "箱包皮具 > 箱包 > 零钱包": "箱包皮具 > 箱包配件 > 零钱包/腰包",
    "箱包皮具 > 箱包配件": "箱包皮具 > 箱包配件 > 手提包/斜挎包",
    "母婴用品 > 婴幼儿用品": "母婴用品 > 婴幼儿用品 > 婴幼儿用品",
    "美妆个护 > 彩妆 > 彩妆": "化妆品饰品 > 美妆个护 > 彩妆/唇妆",
    "美妆个护 > 护肤 > 护肤品": "化妆品饰品 > 美妆个护 > 护肤/化妆品",
    "美妆个护 > 浴室用品 > 沐浴用品": "家居生活 > 卫浴用品 > 沐浴用品",
    "美妆个护 > 浴室用品 > 肥皂盒": "家居生活 > 卫浴用品 > 皂盒",
    "美妆个护 > 美容工具 > 美容工具": "化妆品饰品 > 美妆个护 > 美妆套装",
    "运动户外 > 运动健身": "运动户外 > 运动健身 > 健身器材"
}

# 验证所有目标路径均在标准库中
for old_c, new_c in LEGACY_MAP.items():
    assert new_c in STD_SET, f"Target {new_c} not in standard categories!"


def main():
    conn = pymysql.connect(
        host='localhost', port=3306, user='root',
        password='admin123', database='supplier_crawler', charset='utf8mb4'
    )
    cur = conn.cursor()

    print("=================================================================")
    print(" 开始清理历史非标准遗留路径")
    print("=================================================================")

    # 1. 更新 products.category
    updated_products = 0
    for old_cat, new_cat in LEGACY_MAP.items():
        cur.execute(
            "UPDATE products SET category = %s, updated_at = updated_at WHERE category = %s",
            (new_cat, old_cat)
        )
        updated_products += cur.rowcount
    conn.commit()
    print(f"products.category 遗留路径更新完成: {updated_products} 件商品")

    # 2. 更新 product_categories
    updated_pc = 0
    for old_cat, new_cat in LEGACY_MAP.items():
        # 首先查询拥有 old_cat 的 product_id
        cur.execute("SELECT product_id FROM product_categories WHERE category = %s", (old_cat,))
        pids = [r[0] for r in cur.fetchall()]
        if not pids:
            continue
        # 删除 old_cat
        cur.execute("DELETE FROM product_categories WHERE category = %s", (old_cat,))
        # 重新插入 new_cat
        for pid in pids:
            cur.execute(
                "INSERT IGNORE INTO product_categories (product_id, category) VALUES (%s, %s)",
                (pid, new_cat)
            )
            updated_pc += 1

    conn.commit()
    print(f"product_categories 遗留路径更新完成: {updated_pc} 条记录")

    # 3. 最终检查：验证全库是否还有任何非标准路径
    cur.execute("""
        SELECT count(*)
        FROM products p
        JOIN suppliers s ON s.id = p.supplier_id
        WHERE s.is_active = 1 AND p.is_available = 1 AND p.is_missing = 0
          AND p.category NOT IN ({})
    """.format(','.join(['%s'] * len(STD_SET))), list(STD_SET))
    invalid_p_count = cur.fetchone()[0]

    cur.execute("""
        SELECT count(distinct category)
        FROM product_categories
        WHERE category NOT IN ({})
    """.format(','.join(['%s'] * len(STD_SET))), list(STD_SET))
    invalid_pc_distinct = cur.fetchone()[0]

    print("\n=================================================================")
    print(" 最终全库合规校验结果:")
    print(f" 活跃在售商品中非标准分类数量: {invalid_p_count}")
    print(f" product_categories 中非标准分类数量: {invalid_pc_distinct}")
    print("=================================================================")

    conn.close()


if __name__ == "__main__":
    main()
