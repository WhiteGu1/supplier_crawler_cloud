import json, sys, os, time
sys.stdout.reconfigure(encoding='utf-8')

# 读取批次
with open('diego_batches.json', 'r', encoding='utf-8') as f:
    batches = json.load(f)

# 生成每批的 task prompt
def make_task(batch):
    lines = []
    for i, item in enumerate(batch):
        lines.append(f"{i+1}. ID:{item['id']}, 路径: {item['img']}")
    img_list = "\n".join(lines)
    return f"""你是商品分类验证助手。请用 read 工具逐个读取以下图片，判断每张图片的商品类别。

图片列表：
{img_list}

分类类别请用中文，从以下列表中选择最匹配的：
- 厨房餐具（碗、盘、杯、刀叉勺等）
- 厨房炊具（锅、铲、烤具等）
- 厨房储物（保鲜盒、储物罐等）
- 餐饮用品（餐盘、托盘、餐盒等）
- 清洁用品（桶、盆、刷等）
- 卫浴用品（镜、收纳等）
- 装饰品（摆件、花瓶等）
- 收纳整理（篮、箱、袋等）
- 日用百货（杂项）
- 文具办公
- 个人防护
- 五金工具
- 电器电子
- 美妆个护
- 食品饮料
- 玩具游戏
- 运动户外
- 鞋履护理
- 派对用品
- 照明灯具
- 季节商品
- 婴幼儿用品
- 宠物用品
- 箱包配件
- 数码科技
- 其他

输出格式：JSON数组，每项 {{"id": ID, "category": "分类名称", "desc": "简要描述"}}
只输出JSON，不要其他文字。"""

# 输出每批的task文本，用分隔符隔开
for i, batch in enumerate(batches):
    print(f"===BATCH {i}===")
    print(make_task(batch))
    print(f"===END BATCH {i}===")
