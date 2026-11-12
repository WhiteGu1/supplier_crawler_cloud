import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('D:/projects/supplier_crawler/diego_50_prompts.json', 'r', encoding='utf-8') as f:
    prompts = json.load(f)
idx = int(sys.argv[1])
# 写到单独文件
with open(f'D:/projects/supplier_crawler/diego_50_prompt_{idx}.txt', 'w', encoding='utf-8') as f:
    f.write(prompts[idx])
print(f'wrote prompt {idx} to file, {len(prompts[idx])} chars')
