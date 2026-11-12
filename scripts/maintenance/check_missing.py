import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')

cache_dir = r'D:\projects\supplier_crawler\classify_cache'

# 列出所有文件
all_files = os.listdir(cache_dir)

# 分离 batch_N.json 和 batch_N_diff.json
batch_nums = set()
diff_nums = set()
for f in all_files:
    if f.startswith('batch_') and f.endswith('.json'):
        name = f.replace('.json', '')
        if name.endswith('_diff'):
            num_str = name.replace('batch_', '').replace('_diff', '')
            try:
                diff_nums.add(int(num_str))
            except ValueError:
                pass
        else:
            num_str = name.replace('batch_', '')
            try:
                batch_nums.add(int(num_str))
            except ValueError:
                pass

print(f"batch_N.json: {len(batch_nums)} 个")
print(f"batch_N_diff.json: {len(diff_nums)} 个")

# 找出有batch但没diff的
only_batch = batch_nums - diff_nums
only_diff = diff_nums - batch_nums
both = batch_nums & diff_nums

print(f"两者都有: {len(both)}")
print(f"只有batch(没diff): {len(only_batch)}")
print(f"只有diff(没batch): {len(only_diff)}")

# 找缺失的batch
all_expected = set(range(1, 238))
missing = all_expected - batch_nums
print(f"\n缺失batch文件: {sorted(missing)}")
print(f"共 {len(missing)} 个")

# 检查diff中是否有108-148
print(f"\n108-148区间:")
for n in range(108, 149):
    b = n in batch_nums
    d = n in diff_nums
    print(f"  batch_{n}: batch={'有' if b else '无'}, diff={'有' if d else '无'}")
