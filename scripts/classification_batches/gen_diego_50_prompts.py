import pymysql, json, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT id, name, image_local FROM products WHERE supplier_id=5 AND image_local IS NOT NULL AND image_local != '' AND id > 2475 ORDER BY id")
rows = cur.fetchall()
print(f'remaining: {len(rows)}')

CATEGORIES = '厨房餐具 / 厨房炊具 / 厨房储物 / 餐饮用品 / 清洁用品 / 卫浴用品 / 装饰品 / 收纳整理 / 日用百货 / 文具办公 / 个人防护 / 电器电子 / 美妆个护 / 玩具游戏 / 派对用品 / 宠物用品 / 季节商品 / 婴幼儿用品 / 运动户外 / 其他 / 五金工具 / 照明灯具 / 鞋履护理 / 食品饮料 / 数码科技 / 箱包配件 / 家居纺织 / 家居家具 / 家居收纳 / 家居清洁 / 家居百货 / 家居装饰 / 旅行用品 / 时尚配饰 / 服装服饰 / 针线缝纫 / 园艺户外 / 圣诞用品'

batches = []
for i in range(0, len(rows), 50):
    batch_items = rows[i:i+50]
    lines = []
    lines.append('你是商品分类助手。请用 image 工具逐个分析以下商品图片，结合商品名称判断最合适的分类。')
    lines.append('注意：必须使用 image 工具查看图片，不要使用 read 工具。')
    lines.append('')
    lines.append('商品列表：')
    for j, r in enumerate(batch_items):
        img_path = r[2]
        # 补全路径
        if not img_path.startswith('D:/') and not img_path.startswith('D:\\'):
            img_path = 'D:/projects/supplier_crawler/' + img_path
        lines.append(f'{j+1}. ID:{r[0]}, 名称:{r[1]}, 图片:{img_path}')
    lines.append('')
    lines.append('可选分类（选最匹配的）：')
    lines.append(CATEGORIES)
    lines.append('')
    lines.append('输出格式：JSON数组，每项 {"id": ID, "category": "分类名称", "desc": "简要描述商品"}')
    lines.append('只输出JSON，不要其他文字。')
    batches.append('\n'.join(lines))

print(f'batches(50/batch): {len(batches)}')
for i in range(min(5, len(batches))):
    print(f'batch-{i}: {len(batches[i])} chars, first ID check: {batches[i][:120]}')

with open('D:/projects/supplier_crawler/diego_50_prompts.json', 'w', encoding='utf-8') as f:
    json.dump(batches, f, ensure_ascii=False)
conn.close()
