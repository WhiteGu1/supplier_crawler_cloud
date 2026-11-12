import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取5个prompt文件内容并输出
prompt_dir = 'D:/projects/supplier_crawler/kk_prompts'
for i in range(5):
    path = os.path.join(prompt_dir, f'batch_{i:03d}.txt')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 输出到stdout，用分隔符标记
    print(f"===BATCH_{i}===")
    print(content)
    print(f"===END_BATCH_{i}===")
