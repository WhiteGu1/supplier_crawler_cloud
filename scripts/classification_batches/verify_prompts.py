import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

prompt_dir = 'D:/projects/supplier_crawler/kk_prompts'

# 读取batch 0-4的prompt内容
for i in range(5):
    path = os.path.join(prompt_dir, f'batch_{i:03d}.txt')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 保存为单独文件方便读取
    print(f"Batch {i}: {len(content)} chars")

print("\nPrompt文件已就绪，可在子agent中直接引用文件路径")
print("每个子agent读取 D:/projects/supplier_crawler/kk_prompts/batch_XXX.txt")
