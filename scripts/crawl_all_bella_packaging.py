# -*- coding: utf-8 -*-
"""
scripts/crawl_all_bella_packaging.py
通过 Bella Central 官方 WooCommerce Store API 全量批量获取所有商品的装盒数 (package_qty) 和小包装数 (sub_pack_qty)
并更新写入 MySQL 数据库 products 表 (supplier_id = 18)。
"""
import asyncio
import aiohttp
import json
import os
import re
import sys
import time
import pymysql

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_qty_from_text(text: str) -> int:
    t = text.lower().replace(" ", "")
    m = re.search(r'(?:caja|pack|bulto|display)[x\-_]?(\d+)', t)
    if m:
        return int(m.group(1))
    m2 = re.search(r'(\d+)[x\-_]?(?:u|unid|unida|unidad|unidades|pcs|pz)', t)
    if m2:
        return int(m2.group(1))
    m3 = re.search(r'[x*](\d+)', t)
    if m3:
        return int(m3.group(1))
    return 1


def parse_bella_wc_product(item: dict) -> tuple[int, int]:
    """
    返回 (package_qty, sub_pack_qty)
    """
    box_options = []
    pack_options = []
    
    # 1. 检查 attributes / terms
    attrs = item.get("attributes") or []
    for attr in attrs:
        terms = attr.get("terms") or []
        for term in terms:
            name = (term.get("name") or "").strip().lower()
            slug = (term.get("slug") or "").strip().lower()
            combined = f"{name} {slug}"
            n = extract_qty_from_text(combined)
            if 'caja' in combined:
                box_options.append(n)
            elif 'pack' in combined or 'bulto' in combined or 'display' in combined:
                pack_options.append(n)
            elif n > 1:
                pack_options.append(n)

    # 2. 检查 variations 中的 attributes
    variations = item.get("variations") or []
    for var in variations:
        var_attrs = var.get("attributes") or []
        for va in var_attrs:
            val = (va.get("value") or "").strip().lower()
            n = extract_qty_from_text(val)
            if 'caja' in val:
                box_options.append(n)
            elif 'pack' in val or 'bulto' in val:
                pack_options.append(n)
            elif n > 1:
                pack_options.append(n)

    # 3. 检查商品标题
    p_name = item.get("name") or ""
    m_title = re.search(r'(?:caja|pack|bulto|set)[*\s\-x]+(\d+)', p_name, re.IGNORECASE)
    title_box = int(m_title.group(1)) if m_title else 0

    # 汇总计算 box_qty 与 sub_pack_qty
    box_qty = 1
    sub_pack_qty = 1

    if box_options:
        box_qty = max(box_options)
    elif pack_options:
        box_qty = max(pack_options)
    elif title_box > 1:
        box_qty = title_box

    # 次级小包装
    if pack_options:
        valid_subs = [p for p in pack_options if p < box_qty]
        if valid_subs:
            sub_pack_qty = max(valid_subs)
    elif box_options and len(box_options) > 1:
        valid_subs = [p for p in box_options if p < box_qty]
        if valid_subs:
            sub_pack_qty = max(valid_subs)

    return box_qty, sub_pack_qty


async def main():
    conn = pymysql.connect(
        host='localhost', port=3306, user='root', password='admin123',
        database='supplier_crawler', autocommit=False
    )
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    print("[1/3] 获取本地 Bella Central 所有商品记录...")
    cur.execute("SELECT id, name, sku, product_url, package_qty, sub_pack_qty FROM products WHERE supplier_id=18")
    db_items = cur.fetchall()
    print(f"本地数据库 Bella Central 共 {len(db_items)} 件商品。")
    
    # 建立查找索引字典：按 sku (WC ID) 和 按 clean_url
    by_sku = {}
    by_url = {}
    for r in db_items:
        if r["sku"]:
            by_sku[str(r["sku"]).strip()] = r
        if r["product_url"]:
            clean = r["product_url"].rstrip("/").lower()
            by_url[clean] = r

    print("[2/3] 通过 WooCommerce Store API 批量拉取商品规格 (每页100条)...")
    base_api = "https://bellacentral.com.ar/wp-json/wc/store/v1/products"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    page = 1
    per_page = 100
    total_fetched = 0
    updates = []
    
    timeout = aiohttp.ClientTimeout(total=30)
    sem = asyncio.Semaphore(6) # 稳妥并发

    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        # 先探第一页获取总头信息
        try:
            async with session.get(f"{base_api}?per_page={per_page}&page=1") as resp:
                total_products = int(resp.headers.get("X-WP-Total", 6700))
                total_pages = int(resp.headers.get("X-WP-TotalPages", 68))
                print(f"网站返回总计: {total_products} 件商品, 共 {total_pages} 页。")
        except Exception as e:
            print(f"探测首页面失败: {e}, 按默认 70 页拉取")
            total_pages = 70

        async def fetch_page(p_idx):
            async with sem:
                url = f"{base_api}?per_page={per_page}&page={p_idx}"
                for attempt in range(3):
                    try:
                        async with session.get(url) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                return p_idx, data
                            elif resp.status == 400 or resp.status == 404:
                                return p_idx, []
                    except Exception:
                        await asyncio.sleep(1)
                return p_idx, []

        print(f"启动并发抓取第 1 ~ {total_pages} 页...")
        tasks = [fetch_page(p) for p in range(1, total_pages + 1)]
        pages_results = await asyncio.gather(*tasks)

    print("[3/3] 解析包装规格并批量更新数据库...")
    matched_count = 0
    box_qty_gt_1 = 0
    sub_qty_gt_1 = 0

    for p_idx, items in pages_results:
        total_fetched += len(items)
        for it in items:
            wc_id = str(it.get("id") or "").strip()
            permalink = (it.get("permalink") or "").rstrip("/").lower()
            
            # 找到本地匹配商品
            target = by_sku.get(wc_id) or by_url.get(permalink)
            if not target:
                continue

            box_qty, sub_qty = parse_bella_wc_product(it)
            matched_count += 1
            if box_qty > 1:
                box_qty_gt_1 += 1
            if sub_qty > 1:
                sub_qty_gt_1 += 1

            updates.append((box_qty, sub_qty, target["id"]))

    print(f"API 总拉取商品: {total_fetched} 件, 成功匹配本地商品: {matched_count} 件")
    print(f"其中具有装盒规格 (package_qty > 1): {box_qty_gt_1} 件")
    print(f"其中具有小包规格 (sub_pack_qty > 1): {sub_qty_gt_1} 件")

    if updates:
        print("正在批量写入 MySQL...")
        cur.executemany("UPDATE products SET package_qty=%s, sub_pack_qty=%s WHERE id=%s", updates)
        conn.commit()
        print("MySQL 更新完成！")

    conn.close()
    print("全部抓取与规格更新大功告成！")


if __name__ == "__main__":
    t0 = time.time()
    asyncio.run(main())
    print(f"总耗时: {time.time() - t0:.2f} 秒")
