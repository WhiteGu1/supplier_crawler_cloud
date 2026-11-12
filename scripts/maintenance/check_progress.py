import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

cache_dir = r'D:\projects\supplier_crawler\classify_cache'
batches = []
for f in os.listdir(cache_dir):
    if f.endswith('.json') and '_diff' not in f and f.startswith('batch_'):
        with open(os.path.join(cache_dir, f), 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            batches.append(data)

batches.sort(key=lambda x: x['batch_id'])
total = sum(b['total'] for b in batches)
changed = sum(b.get('diff', {}).get('changed', 0) for b in batches)
same = sum(b.get('diff', {}).get('same', 0) for b in batches)
new_cats_total = sum(len(b.get('new_categories', [])) for b in batches)

need_verify = 0
no_img_changed = 0
all_new_cats = set()
for b in batches:
    for item in b.get('assignments', []):
        if item.get('new_category') != item.get('old_category'):
            if item.get('has_image'):
                need_verify += 1
            else:
                no_img_changed += 1
    for nc in b.get('new_categories', []):
        all_new_cats.add(nc['category'])

print(f'已完成批次: {len(batches)}')
print(f'总商品: {total}')
print(f'变化: {changed}, 不变: {same}')
print(f'新分类: {new_cats_total} (去重: {len(all_new_cats)})')
print(f'待识图验证(有图变化): {need_verify}')
print(f'无图变化: {no_img_changed}')
print(f'进度: {total}/23601 = {total/23601*100:.1f}%')
print(f'剩余批次: {236 - len(batches)}')

# 收集所有待验证项
verify_items = []
for b in batches:
    for item in b.get('assignments', []):
        if item.get('new_category') != item.get('old_category') and item.get('has_image'):
            verify_items.append({
                'batch_id': b['batch_id'],
                'id': item['id'],
                'name': item.get('name', ''),
                'old_category': item.get('old_category', ''),
                'new_category': item.get('new_category', ''),
                'image_path': item.get('image_path', ''),
            })

# 输出前10条
print('\n前10条待验证:')
for v in verify_items[:10]:
    print(f"  batch={v['batch_id']} id={v['id']} | {v['old_category']} -> {v['new_category']} | {v['name'][:30]}")
    print(f"    img: {v['image_path']}")

# 保存待验证列表
out_path = os.path.join(cache_dir, 'verify_list.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(verify_items, f, ensure_ascii=False, indent=2)
print(f'\n待验证列表已保存: {out_path}')
print(f'共 {len(verify_items)} 条')
