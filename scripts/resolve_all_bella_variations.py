import pymysql
import json
import re
import urllib.request
import concurrent.futures

conn = pymysql.connect(host='localhost', user='root', password='admin123', database='supplier_crawler', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute('''
        SELECT c.id as cart_id, c.product_id, c.quantity, p.name, p.sku, p.price, p.product_url, p.package_qty, p.sub_pack_qty, p.is_missing
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18
        ORDER BY c.id ASC
    ''')
    cart_items = cur.fetchall()

print(f"Total cart items to resolve: {len(cart_items)}", flush=True)

def parse_num(val_str):
    m = re.search(r'\d+', val_str)
    return int(m.group(0)) if m else None

def process_item(it):
    sku = it['sku']
    qty = it['quantity']
    pkg = it['package_qty'] or 1
    sub = it['sub_pack_qty'] or 1
    name = it['name']
    
    url = f"https://bellacentral.com.ar/wp-json/wc/store/v1/products/{sku}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            p = json.loads(resp.read().decode('utf-8'))
        
        p_type = p.get('type')
        in_stock = p.get('is_in_stock', False)
        
        if not in_stock:
            return {'status': 'out_of_stock', 'id': int(sku), 'qty': qty, 'name': name}
            
        if p_type == 'simple':
            return {'status': 'ok', 'id': int(sku), 'qty': qty, 'name': name, 'type': 'simple'}
            
        variations = p.get('variations', [])
        if not variations:
            return {'status': 'ok', 'id': int(sku), 'qty': qty, 'name': name, 'type': 'simple'}
            
        var_candidates = []
        for v in variations:
            vid = v['id']
            attrs = v.get('attributes', [])
            val = attrs[0].get('value', '').lower() if attrs else ''
            
            count = 1
            if 'caja' in val:
                num = parse_num(val)
                count = num if num else pkg
            elif 'pack' in val:
                num = parse_num(val)
                count = num if num else (sub if sub > 1 else pkg)
            elif 'unidad' in val:
                num = parse_num(val)
                count = num if num else 1
            else:
                num = parse_num(val)
                count = num if num else 1
            var_candidates.append({'id': vid, 'label': val, 'count': count})
            
        chosen = None
        for cand in var_candidates:
            if cand['count'] == pkg and qty % pkg == 0:
                chosen = cand
                break
        if not chosen and sub > 1:
            for cand in var_candidates:
                if cand['count'] == sub and qty % sub == 0:
                    chosen = cand
                    break
        if not chosen:
            for cand in var_candidates:
                if cand['count'] > 1 and qty % cand['count'] == 0:
                    chosen = cand
                    break
        if not chosen:
            for cand in var_candidates:
                if cand['count'] == 1:
                    chosen = cand
                    break
        if not chosen and var_candidates:
            chosen = var_candidates[0]
            
        if chosen:
            actual_qty = qty // chosen['count'] if chosen['count'] > 0 and qty >= chosen['count'] and qty % chosen['count'] == 0 else qty
            return {
                'status': 'ok',
                'parent_id': int(sku),
                'id': chosen['id'],
                'qty': actual_qty,
                'name': name,
                'type': 'variable',
                'var_label': chosen['label'],
                'pack_size': chosen['count'],
                'orig_qty': qty
            }
        return {'status': 'error', 'id': int(sku), 'name': name, 'reason': 'no variation chosen'}
    except Exception as e:
        return {'status': 'error', 'id': int(sku), 'name': name, 'reason': str(e)}

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    future_to_item = {executor.submit(process_item, it): it for it in cart_items}
    for future in concurrent.futures.as_completed(future_to_item):
        res = future.result()
        results.append(res)
        if len(results) % 25 == 0:
            print(f"Resolved: {len(results)}/{len(cart_items)}", flush=True)

resolved = [r for r in results if r['status'] == 'ok']
out_of_stock = [r for r in results if r['status'] == 'out_of_stock']
errors = [r for r in results if r['status'] == 'error']

print(f"Total resolved: {len(resolved)}, Out of stock: {len(out_of_stock)}, Errors: {len(errors)}", flush=True)

with open('scripts/resolved_bella_cart.json', 'w', encoding='utf-8') as f:
    json.dump({'resolved': resolved, 'out_of_stock': out_of_stock, 'errors': errors}, f, ensure_ascii=False, indent=2)
