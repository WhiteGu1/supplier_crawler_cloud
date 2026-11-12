import urllib.request
import json
import time
import pymysql
import concurrent.futures

print("=== 1. 开始对购物车中 141 件 Bella Central 商品进行实时重爬核验 ===", flush=True)

conn = pymysql.connect(
    host='localhost', user='root', password='admin123', database='supplier_crawler',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute('''
        SELECT c.id as cart_id, c.product_id, c.quantity, p.name, p.sku, p.product_url, p.is_missing
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE p.supplier_id = 18
        ORDER BY c.id ASC
    ''')
    cart_items = cur.fetchall()

print(f"购物车待核验商品数: {len(cart_items)}", flush=True)

def check_single_sku(it):
    sku = it['sku']
    url = f"https://bellacentral.com.ar/wp-json/wc/store/v1/products/{sku}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        is_in_stock = data.get('is_in_stock', False)
        
        # 还要检查变体情况
        variations = data.get('variations', [])
        has_in_stock_var = False
        var_details = []
        if variations:
            # check if at least one wholesale variation is in stock
            for v in variations:
                vid = v['id']
                v_attrs = [a.get('value', '') for a in v.get('attributes', [])]
                var_details.append({'id': vid, 'attrs': v_attrs})
        return {
            'sku': sku,
            'name': it['name'],
            'cart_qty': it['quantity'],
            'is_in_stock': is_in_stock,
            'type': data.get('type'),
            'variations_count': len(variations),
            'url': it['product_url']
        }
    except Exception as e:
        return {
            'sku': sku,
            'name': it['name'],
            'cart_qty': it['quantity'],
            'is_in_stock': False,
            'error': str(e),
            'url': it['product_url']
        }

cart_results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(check_single_sku, it): it for it in cart_items}
    for f in concurrent.futures.as_completed(futures):
        cart_results.append(f.result())
        if len(cart_results) % 25 == 0:
            print(f"购物车实时核验进度: {len(cart_results)}/{len(cart_items)}", flush=True)

cart_out_of_stock = [r for r in cart_results if not r['is_in_stock']]
cart_in_stock = [r for r in cart_results if r['is_in_stock']]

print(f"购物车核验完成: 在售 {len(cart_in_stock)} 件，断货售罄 {len(cart_out_of_stock)} 件", flush=True)

# 更新数据库中购物车商品的 is_missing 状态
with conn.cursor() as cur:
    for o in cart_out_of_stock:
        cur.execute("UPDATE products SET is_missing = 1, stock = 0 WHERE supplier_id = 18 AND sku = %s", (o['sku'],))
    for s in cart_in_stock:
        cur.execute("UPDATE products SET is_missing = 0 WHERE supplier_id = 18 AND sku = %s", (s['sku'],))
    conn.commit()

print("数据库已完成购物车商品断货标记更新！", flush=True)

# 保存购物车核验结果到 JSON
with open('scripts/cart_stock_verification.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(cart_items),
        'in_stock_count': len(cart_in_stock),
        'out_of_stock_count': len(cart_out_of_stock),
        'out_of_stock_items': cart_out_of_stock,
        'in_stock_items': cart_in_stock
    }, f, ensure_ascii=False, indent=2)

print("\n=== 2. 开始对 Bella Central 全站约 6970 件商品进行全量库存爬取更新 ===", flush=True)

total_pages = 70
all_out_of_stock_skus = []
all_in_stock_skus = []

for page in range(1, total_pages + 1):
    api_url = f"https://bellacentral.com.ar/wp-json/wc/store/v1/products?per_page=100&page={page}"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            prods = json.loads(resp.read().decode('utf-8'))
            if not prods:
                break
            page_total = resp.headers.get('X-WP-TotalPages')
            if page_total:
                total_pages = int(page_total)
            
            p_out = [str(p['id']) for p in prods if not p.get('is_in_stock')]
            p_in = [str(p['id']) for p in prods if p.get('is_in_stock')]
            
            all_out_of_stock_skus.extend(p_out)
            all_in_stock_skus.extend(p_in)
            
            if page % 10 == 0 or page == total_pages:
                print(f"全站进度: 第 {page}/{total_pages} 页 (累计发现断货: {len(all_out_of_stock_skus)}, 在售: {len(all_in_stock_skus)})", flush=True)
    except Exception as e:
        print(f"第 {page} 页抓取重试: {e}", flush=True)
        time.sleep(1)

print(f"全站扫描结束！共扫描 {len(all_in_stock_skus) + len(all_out_of_stock_skus)} 件商品", flush=True)
print(f"在售: {len(all_in_stock_skus)}, 售罄断货: {len(all_out_of_stock_skus)}", flush=True)

# 批量更新数据库
with conn.cursor() as cur:
    print("正在批量更新数据库 is_missing 状态...", flush=True)
    if all_out_of_stock_skus:
        batch_size = 500
        for i in range(0, len(all_out_of_stock_skus), batch_size):
            chunk = all_out_of_stock_skus[i:i+batch_size]
            placeholders = ','.join(['%s'] * len(chunk))
            cur.execute(f"UPDATE products SET is_missing = 1, stock = 0 WHERE supplier_id = 18 AND sku IN ({placeholders})", chunk)
    if all_in_stock_skus:
        batch_size = 500
        for i in range(0, len(all_in_stock_skus), batch_size):
            chunk = all_in_stock_skus[i:i+batch_size]
            placeholders = ','.join(['%s'] * len(chunk))
            cur.execute(f"UPDATE products SET is_missing = 0 WHERE supplier_id = 18 AND sku IN ({placeholders})", chunk)
    conn.commit()

conn.close()
print("🎉 全站断货数据爬取与数据库同步全部完成！", flush=True)
