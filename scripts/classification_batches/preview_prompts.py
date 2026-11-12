import os, sys
sys.stdout.reconfigure(encoding='utf-8')

prompt_dir = 'D:/projects/supplier_crawler/kk_prompts'
files = sorted(os.listdir(prompt_dir))
print(f"总prompt文件: {len(files)}")

# 读取前5批prompt内容
for i in range(5):
    path = os.path.join(prompt_dir, files[i])
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"\nbatch_{i:03d}: {len(content)} chars")
    # 输出前200字符预览
    print(content[:200] + "...")
