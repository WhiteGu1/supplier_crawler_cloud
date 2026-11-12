# -*- coding: utf-8 -*-
"""
生成Diego重分类的子agent prompt，并输出批次信息供sessions_spawn使用。
每批10条，每波5批并行。
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('diego_batches.json', 'r', encoding='utf-8') as f:
    batches = json.load(f)

STANDARD_CATEGORIES = [
    '厨房餐具', '厨房炊具', '厨房储物', '餐饮用品', '清洁用品',
    '卫浴用品', '装饰品', '收纳整理', '日用百货', '文具办公',
    '个人防护', '电器电子', '美妆个护', '玩具游戏', '派对用品',
    '宠物用品', '季节商品', '婴幼儿用品', '运动户外', '其他',
    '五金工具', '照明灯具', '鞋履护理', '食品饮料', '数码科技',
    '箱包配件', '家居纺织', '家居家具', '家居收纳', '家居清洁',
    '家居百货', '家居装饰', '旅行用品', '时尚配饰', '服装服饰',
    '针线缝纫', '园艺户外', '圣诞用品'
]

def build_prompt(batch):
    lines = []
    lines.append("你是商品分类助手。请用 image 工具逐个分析以下商品图片，结合商品名称判断最合适的分类。")
    lines.append("注意：必须使用 image 工具查看图片，不要使用 read 工具。")
    lines.append("")
    lines.append("商品列表：")
    for i, item in enumerate(batch['ids']):
        name = batch['names'][i]
        img = batch['imgs'][i]
        lines.append(f"{i+1}. ID:{item}, 名称:{name}, 图片:{img}")
    
    lines.append("")
    lines.append("可选分类（选最匹配的）：")
    lines.append(" / ".join(STANDARD_CATEGORIES))
    lines.append("")
    lines.append("输出格式：JSON数组，每项 {\"id\": ID, \"category\": \"分类名称\", \"desc\": \"简要描述商品\"}")
    lines.append("只输出JSON，不要其他文字。")
    return "\n".join(lines)

# 输出前5批的prompt（第一波）
print("=== 第一波 (batch 0-4) ===\n")
for i in range(5):
    prompt = build_prompt(batches[i])
    print(f"--- Batch {i} ---")
    print(f"Prompt length: {len(prompt)} chars")
    print(f"IDs: {batches[i]['ids']}")
    print(prompt[:200] + "...")
    print()

# 保存所有prompt到文件
all_prompts = {}
for i, batch in enumerate(batches):
    all_prompts[i] = build_prompt(batch)

with open('diego_prompts.json', 'w', encoding='utf-8') as f:
    json.dump(all_prompts, f, ensure_ascii=False, indent=2)

print(f"\n共 {len(batches)} 批prompt已保存到 diego_prompts.json")
print(f"每波5批，共 {(len(batches)+4)//5} 波")
