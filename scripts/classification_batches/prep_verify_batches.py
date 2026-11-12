"""准备抽查的第2-5批图片路径（id 21-100对应的待验证项）"""
import json, sys, shutil, os
sys.stdout.reconfigure(encoding='utf-8')

VERIFY_DIR = r"D:\projects\supplier_crawler\classify_cache\verify_results"
WORKSPACE = r"C:\Users\Administrator\.qclaw\workspace-agent-b550e3e8\verify_imgs"

with open(os.path.join(VERIFY_DIR, "need_verify.json"), "r", encoding="utf-8") as f:
    items = json.load(f)

# 已验证前20条，取21-100条
batch_items = items[20:100]

# 分成4批，每批20条
for batch_idx in range(4):
    start = batch_idx * 20
    end = start + 20
    batch = batch_items[start:end]
    
    # 复制图片到workspace
    paths = []
    for i, item in enumerate(batch):
        src = item['image_path']
        ext = os.path.splitext(src)[1]
        dst = os.path.join(WORKSPACE, f"v2_{batch_idx}_{i}{ext}")
        shutil.copy2(src, dst)
        paths.append(dst)
    
    # 输出这批的信息
    print(f"\n=== 批次{batch_idx+2} (共{len(batch)}条) ===")
    for i, item in enumerate(batch):
        print(f"商品{i+1} (id={item['id']}): {item.get('name','')[:40]}")
        print(f"  旧: {item['old_category']}")
        print(f"  新: {item['new_category']}")
        print(f"  img: {paths[i]}")
    
    # 保存路径列表
    with open(os.path.join(VERIFY_DIR, f"batch_{batch_idx+2}_paths.json"), "w", encoding="utf-8") as f:
        json.dump({"items": batch, "paths": paths}, f, ensure_ascii=False, indent=2)

print(f"\n共准备 {len(batch_items)} 条待验证")
