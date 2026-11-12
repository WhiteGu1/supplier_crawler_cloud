# -*- coding: utf-8 -*-
"""
scripts/audit_bella_cart_packaging.py
全面检查购物车中所有 Bella Central 商品与网站实际装盒数/打包数是否成倍数
"""
import asyncio
import aiohttp
import json
import os
import re
import sys
from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.db_manager import DatabaseManager


def extract_qty_from_text(text: str) -> int:
    """从文本如 'caja-24u', 'caja x24', 'pack-10u', '6-unidad', 'caja-21unida' 中提取数字"""
    t = text.lower().replace(" ", "")
    # 匹配 caja x 24, caja-24u, caja24
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


def analyze_product_packaging(html: str, product_name: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    
    box_options = []
    pack_options = []
    unit_option = False
    
    # 1. 检查 variations 表单中的 data-product_variations
    form = soup.select_one('form.variations_form')
    if form and form.get('data-product_variations'):
        try:
            vars_list = json.loads(form.get('data-product_variations'))
            for v in vars_list:
                attrs = v.get('attributes') or {}
                for attr_val in attrs.values():
                    if not attr_val:
                        continue
                    val_lower = str(attr_val).lower().strip()
                    n = extract_qty_from_text(val_lower)
                    
                    if 'caja' in val_lower:
                        box_options.append((n, attr_val))
                    elif 'pack' in val_lower or 'bulto' in val_lower or 'display' in val_lower:
                        pack_options.append((n, attr_val))
                    elif n > 1:
                        pack_options.append((n, attr_val))
                    elif 'unidad' in val_lower or val_lower == 'u':
                        unit_option = True
        except Exception:
            pass

    # 2. 如果没在 variations json 中找到，但在 select option 中
    if not box_options and not pack_options:
        for opt in soup.select('select option'):
            val = opt.text.strip().lower()
            if not val or 'elegir' in val:
                continue
            n = extract_qty_from_text(val)
            if 'caja' in val:
                box_options.append((n, opt.text.strip()))
            elif 'pack' in val or 'bulto' in val:
                pack_options.append((n, opt.text.strip()))
            elif n > 1:
                pack_options.append((n, opt.text.strip()))

    # 3. 检查页面 input quantity step
    step_qty = 1
    qty_inp = soup.select_one('input.qty, input[name="quantity"]')
    if qty_inp and qty_inp.get('step'):
        try:
            step_qty = int(qty_inp.get('step'))
        except Exception:
            step_qty = 1

    # 4. 从商品名称中提取规格（例如 "CAJA*12", "Pack 15pcs", "CAJA X29"）
    title_box = 0
    m_title = re.search(r'(?:caja|pack|bulto|set)[*\s\-x]+(\d+)', product_name, re.IGNORECASE)
    if m_title:
        title_box = int(m_title.group(1))

    # 确定最佳整盒数 / 装盒数
    # 如果有明确的 caja 变体，以 caja 的数量为主
    primary_box_qty = 1
    raw_desc = ""
    
    if box_options:
        # 取最大的 caja 数量（例如 24u）
        sorted_boxes = sorted(box_options, key=lambda x: x[0], reverse=True)
        primary_box_qty = sorted_boxes[0][0]
        raw_desc = f"变体盒装: {sorted_boxes[0][1]} ({primary_box_qty}件/盒)"
    elif pack_options:
        # 其次取 pack 数量
        sorted_packs = sorted(pack_options, key=lambda x: x[0], reverse=True)
        primary_box_qty = sorted_packs[0][0]
        raw_desc = f"变体包装: {sorted_packs[0][1]} ({primary_box_qty}件/包)"
    elif title_box > 1:
        primary_box_qty = title_box
        raw_desc = f"标题标明包装: {primary_box_qty}件/盒"
    elif step_qty > 1:
        primary_box_qty = step_qty
        raw_desc = f"网站输入步长 step: {primary_box_qty}"
    else:
        primary_box_qty = 1
        raw_desc = "单件销售(无盒装变体)"

    # 次级包装（例如 6件小包）
    sub_pack_qty = 1
    if pack_options:
        sorted_sub = sorted([p for p in pack_options if p[0] < primary_box_qty], key=lambda x: x[0], reverse=True)
        if sorted_sub:
            sub_pack_qty = sorted_sub[0][0]

    return {
        "box_qty": primary_box_qty,
        "sub_pack_qty": sub_pack_qty,
        "raw_desc": raw_desc,
        "has_box_variation": bool(box_options),
        "has_pack_variation": bool(pack_options),
        "all_box_options": box_options,
        "all_pack_options": pack_options,
    }


async def main():
    db = DatabaseManager('localhost', 3306, 'root', 'admin123', 'supplier_crawler')
    items = db.get_cart_items()
    bella_items = [it for it in items if 'bella' in (it.get('supplier_name') or '').lower() or it.get('supplier_id') == 18]
    
    print(f"开始抓取分析 Bella Central 购物车共 {len(bella_items)} 件商品的网站实际包装规格...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    timeout = aiohttp.ClientTimeout(total=20)
    sem = asyncio.Semaphore(12) # 12 并发

    results = []

    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        async def fetch_one(item):
            async with sem:
                url = item.get('product_url')
                name = item.get('name') or ''
                cart_qty = item.get('quantity') or 1
                pid = item.get('product_id')
                sku = item.get('sku') or ''
                
                info = {
                    "product_id": pid,
                    "name": name,
                    "sku": sku,
                    "cart_qty": cart_qty,
                    "url": url,
                    "box_qty": 1,
                    "sub_pack_qty": 1,
                    "raw_desc": "无URL",
                    "status": "error"
                }
                
                if not url:
                    results.append(info)
                    return
                
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            html = await resp.text()
                            pkg = analyze_product_packaging(html, name)
                            info.update(pkg)
                            info["status"] = "ok"
                        else:
                            info["raw_desc"] = f"HTTP {resp.status}"
                except Exception as e:
                    info["raw_desc"] = f"请求失败: {str(e)[:50]}"
                
                results.append(info)

        tasks = [fetch_one(it) for it in bella_items]
        await asyncio.gather(*tasks)

    # 排序并分析倍数关系
    compliant_box = []      # 完全是整盒倍数
    compliant_pack = []     # 是小包倍数但非整盒
    non_compliant = []      # 既不成整盒也不成整包倍数
    single_unit = []        # 网站本身就是单件起售无盒装概念

    for r in results:
        q = r["cart_qty"]
        b = r["box_qty"]
        sub = r["sub_pack_qty"]

        if b == 1:
            single_unit.append(r)
            r["compliance"] = "单件/无装盒限制"
            r["rec_qty"] = q
        elif q % b == 0:
            compliant_box.append(r)
            r["compliance"] = f"是装盒数({b})的整数倍 ({q // b}盒)"
            r["rec_qty"] = q
        elif sub > 1 and q % sub == 0:
            compliant_pack.append(r)
            r["compliance"] = f"非整盒({b})，但符合小包({sub})倍数 ({q // sub}包)"
            # 建议向上规整为整盒
            r["rec_qty"] = ((q + b - 1) // b) * b
        else:
            non_compliant.append(r)
            r["compliance"] = f"❌ 不成倍数！装盒数={b}" + (f"(小包={sub})" if sub > 1 else "")
            # 建议向上规整为整盒
            r["rec_qty"] = ((q + b - 1) // b) * b

    # 保存完整的详细 JSON 结果
    report_file = os.path.join(ROOT_DIR, "scripts", "bella_cart_audit_result.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_bella_items": len(results),
            "single_unit_count": len(single_unit),
            "compliant_box_count": len(compliant_box),
            "compliant_pack_count": len(compliant_pack),
            "non_compliant_count": len(non_compliant),
            "items": results
        }, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("【Bella Central 购物车数量 vs 网站装盒数审核报告】")
    print("=" * 60)
    print(f"购物车中 Bella Central 商品总数: {len(results)}")
    print(f"1. ✅ 完全符合整盒装盒数倍数: {len(compliant_box)} 件")
    print(f"2. ⚠️  符合小包倍数 (但未达到整盒倍数): {len(compliant_pack)} 件")
    print(f"3. ❌ 完全不符合装盒/装包倍数: {len(non_compliant)} 件")
    print(f"4. ℹ️  单件销售/无盒装限制: {len(single_unit)} 件")
    print("=" * 60)

    if non_compliant:
        print("\n【部分严重不合规商品抽样 (不成盒倍数)】:")
        for r in non_compliant[:15]:
            print(f"- {r['name'][:35]} | 当前加购: {r['cart_qty']} | 网站装盒数: {r['box_qty']} | 规格: {r['raw_desc']} | 建议调为: {r['rec_qty']}")

    if compliant_pack:
        print("\n【符合小包但不成整盒抽样】:")
        for r in compliant_pack[:10]:
            print(f"- {r['name'][:35]} | 当前加购: {r['cart_qty']} | 整盒数: {r['box_qty']} (小包={r['sub_pack_qty']}) | 建议调为整盒: {r['rec_qty']}")


if __name__ == "__main__":
    asyncio.run(main())
