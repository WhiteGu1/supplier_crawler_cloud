"""分析差异类型，减少识图验证量"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache"

# 分类差异类型
type1_add_l3 = 0  # 二级补充到三级 (old是二级，new是三级，且前缀一致)
type2_change_l3 = 0  # 三级分类变化
type3_l2_to_l3_diff_parent = 0  # 二级到三级但换了父分类
type4_change_l2 = 0  # 二级分类变化
type5_l1_change = 0  # 一级分类变化
type6_other = 0

# 详细分类
examples = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

for f in sorted(os.listdir(CACHE_DIR)):
    if f.endswith('.json') and '_diff' not in f and f.startswith('batch_'):
        with open(os.path.join(CACHE_DIR, f), 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            for item in data.get('assignments', []):
                old = item.get('old_category', '')
                new = item.get('new_category', '')
                if old == new:
                    continue
                if not item.get('has_image'):
                    continue  # 无图已写入
                
                old_parts = old.split(' > ')
                new_parts = new.split(' > ')
                
                if len(old_parts) == 2 and len(new_parts) == 3 and old_parts[0] == new_parts[0] and old_parts[1] == new_parts[1]:
                    # 二级补充到三级，同一二级下
                    type1_add_l3 += 1
                    if len(examples[1]) < 5:
                        examples[1].append(item)
                elif len(old_parts) == 3 and len(new_parts) == 3 and old_parts[0] == new_parts[0] and old_parts[1] == new_parts[1]:
                    # 三级变化，同一二级下
                    type2_change_l3 += 1
                    if len(examples[2]) < 5:
                        examples[2].append(item)
                elif len(old_parts) >= 2 and len(new_parts) == 3 and old_parts[0] != new_parts[0]:
                    # 一级分类变了
                    type5_l1_change += 1
                    if len(examples[5]) < 5:
                        examples[5].append(item)
                elif len(old_parts) == 2 and len(new_parts) == 3 and old_parts[0] == new_parts[0] and old_parts[1] != new_parts[1]:
                    # 二级到三级但换了二级
                    type3_l2_to_l3_diff_parent += 1
                    if len(examples[3]) < 5:
                        examples[3].append(item)
                elif len(old_parts) == 2 and len(new_parts) == 2 and old_parts[0] == new_parts[0]:
                    # 二级变化
                    type4_change_l2 += 1
                    if len(examples[4]) < 5:
                        examples[4].append(item)
                else:
                    type6_other += 1
                    if len(examples[6]) < 5:
                        examples[6].append(item)

total = type1_add_l3 + type2_change_l3 + type3_l2_to_l3_diff_parent + type4_change_l2 + type5_l1_change + type6_other
print(f"有图差异总数: {total}")
print(f"  Type1 (二级补充到三级): {type1_add_l3}  ← 可自动确认")
print(f"  Type2 (三级变化-同二级): {type2_change_l3}  ← 需识图")
print(f"  Type3 (二级到三级-换二级): {type3_l2_to_l3_diff_parent}  ← 需识图")
print(f"  Type4 (二级变化-同一级): {type4_change_l2}  ← 需识图")
print(f"  Type5 (一级分类变化): {type5_l1_change}  ← 需识图")
print(f"  Type6 (其他): {type6_other}  ← 需识图")
print(f"\n可自动确认(Type1): {type1_add_l3} ({type1_add_l3/total*100:.1f}%)")
print(f"需识图验证: {total - type1_add_l3} ({(total-type1_add_l3)/total*100:.1f}%)")

for t, exs in examples.items():
    if exs:
        print(f"\nType{t} 示例:")
        for ex in exs:
            print(f"  {ex['old_category']} -> {ex['new_category']}")
            print(f"    name: {ex.get('name','')[:40]}")
