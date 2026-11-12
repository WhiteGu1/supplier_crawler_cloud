"""
supplier_crawler/crawler/cart_sync.py
购物车一键同步至目标供应商网站购物车模块
兼容 6 大供应商：Trapoman, benabi, Diego (Distri-Nimay), Bella Central, sfpanda, osa
同时提供起订量 (min_qty) 与箱规/包装倍数 (package_qty) 校验与智能规整
"""
import asyncio
import json
import logging
import math
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def calc_valid_quantity(qty: int, min_qty: int = 1, package_qty: int = 1) -> int:
    """
    计算满足供应商约束的合规订购数量：
    1. 数量必须 >= min_qty (起订量)
    2. 数量必须为 package_qty (箱规/包装数/步进倍数) 的整数倍，向上取整
    """
    q = max(int(qty or 1), 1)
    min_q = max(int(min_qty or 1), 1)
    pkg_q = max(int(package_qty or 1), 1)

    # 先保证不低于起订量
    if q < min_q:
        q = min_q

    # 若有包装倍数要求，向上取整到下一个合规倍数
    if pkg_q > 1:
        remainder = q % pkg_q
        if remainder != 0:
            q = q + (pkg_q - remainder)

    return q


class CartSyncManager:
    """供应商购物车同步管理器"""

    def __init__(self, db_manager=None):
        self.db = db_manager

    def sync_to_supplier(
        self,
        supplier_id: int,
        cart_items: list[dict],
        auto_adjust: bool = True,
        session_cookies: Optional[str] = None,
    ) -> dict:
        """
        同步购物车商品到指定供应商的网站购物车中。
        cart_items 格式示例:
        [
            {
                "product_id": 123,
                "sku": "58512",
                "name": "...",
                "quantity": 24,
                "price": 5000.0,
                "min_qty": 24,
                "package_qty": 24,
                "product_url": "...",
                "image_url": "..."
            }, ...
        ]
        """
        if not cart_items:
            return {
                "success": False,
                "message": "购物车中没有该供应商的商品",
                "synced_count": 0,
                "total_items": 0,
                "cart_url": "",
                "adjusted_items": [],
                "failed_items": [],
            }

        # 获取供应商基础信息与配置
        supplier = self._get_supplier(supplier_id)
        if not supplier:
            return {
                "success": False,
                "message": f"未找到 ID 为 {supplier_id} 的供应商配置",
                "synced_count": 0,
                "total_items": len(cart_items),
                "cart_url": "",
                "adjusted_items": [],
                "failed_items": [],
            }

        s_name = (supplier.get("name") or "").lower()
        base_url = supplier.get("base_url") or ""
        list_url = supplier.get("list_url") or ""
        selectors = supplier.get("selectors") or {}
        if isinstance(selectors, str):
            try:
                selectors = json.loads(selectors)
            except Exception:
                selectors = {}

        # 优先使用传入的 session_cookies，否则取配置的 manual_cookies
        active_cookies = session_cookies or selectors.get("manual_cookies", "")

        logger.info(f"开始同步商品至供应商 [{supplier.get('name')}] (ID={supplier_id})，共 {len(cart_items)} 件")

        # 1. SmartyCart 平台 (Trapoman id=3, benabi id=4)
        if "smarty" in base_url.lower() or "smarty" in list_url.lower() or "benabi" in s_name or "trapoman" in s_name:
            return self._sync_smartycart(supplier, cart_items, auto_adjust)

        # 2. Diego (Distrinimay id=2)
        elif "distrinimay" in base_url.lower() or "diego" in s_name:
            return self._sync_diego(supplier, cart_items, auto_adjust, active_cookies)

        # 3. Bella Central (WooCommerce id=18)
        elif "bellacentral" in base_url.lower() or "bella" in s_name:
            return self._sync_bella_central(supplier, cart_items, auto_adjust, active_cookies)

        # 4. sfpanda (Jumpseller id=1)
        elif "sfpanda" in base_url.lower() or "panda" in s_name:
            return self._sync_sfpanda(supplier, cart_items, auto_adjust)

        # 5. osa (Tiendanube id=5)
        elif "osadistribuidora" in base_url.lower() or "osa" in s_name:
            return self._sync_osa(supplier, cart_items, auto_adjust, active_cookies)

        else:
            return {
                "success": False,
                "message": f"供应商 [{supplier.get('name')}] 暂未适配自动加购协议",
                "synced_count": 0,
                "total_items": len(cart_items),
                "cart_url": base_url,
                "adjusted_items": [],
                "failed_items": [],
            }

    def _get_supplier(self, supplier_id: int) -> Optional[dict]:
        if self.db:
            sups = self.db.get_all_suppliers()
            for s in sups:
                if s.get("id") == supplier_id:
                    return s
        return None

    # ================================================================
    # 1. SmartyCart 同步适配器 (benabi, trapoman)
    # ================================================================
    def _sync_smartycart(self, supplier: dict, items: list[dict], auto_adjust: bool) -> dict:
        list_url = supplier.get("list_url") or ""
        # 优先使用供应商自身域名（兼容 randy.smarty.com.ar 等独立子域），否则回退官方主站域名
        parsed = urlparse(list_url or supplier.get("base_url") or "")
        if parsed.netloc and "smarty" in parsed.netloc.lower():
            clean_base = f"{parsed.scheme or 'https'}://{parsed.netloc}"
        else:
            clean_base = "https://catalog.smarty.com.ar"

        m = re.search(r'/token/([a-f0-9]+)', list_url)
        token = m.group(1) if m else ""
        if not token:
            return {
                "success": False,
                "message": f"未在 SmartyCart 供应商配置中找到有效 token 目录链接: {list_url}",
                "synced_count": 0,
                "total_items": len(items),
                "cart_url": "",
                "adjusted_items": [],
                "failed_items": [],
            }

        cart_url = f"{clean_base}/token/{token}/cart"
        add_api_url = f"{clean_base}/Carts/add_item/"

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{clean_base}/token/{token}",
        })

        synced_count = 0
        adjusted_items = []
        failed_items = []

        for item in items:
            p_name = item.get("name") or ""
            sku = (item.get("sku") or "").strip()
            orig_qty = int(item.get("quantity") or 1)
            min_q = int(item.get("min_qty") or 1)
            pkg_q = int(item.get("package_qty") or 1)

            valid_qty = calc_valid_quantity(orig_qty, min_q, pkg_q) if auto_adjust else orig_qty
            if valid_qty != orig_qty:
                adjusted_items.append({
                    "product_id": item.get("product_id"),
                    "name": p_name,
                    "old_quantity": orig_qty,
                    "new_quantity": valid_qty,
                    "min_qty": min_q,
                    "package_qty": pkg_q,
                })
                if self.db and item.get("product_id"):
                    try:
                        self.db.update_cart_quantity(item["product_id"], valid_qty)
                    except Exception:
                        pass

            # 解析 SmartyCart 平台的内部商品 ID (7位数字如 4074508)
            prod_id = self._resolve_smarty_prod_id(session, clean_base, token, item)
            if not prod_id:
                failed_items.append({
                    "name": p_name,
                    "sku": sku,
                    "reason": "未能从 SmartyCart 目录检索到对应的商品 ID (尝试 SKU / 关键词搜索均无匹配)",
                })
                continue

            # 回写 product_url 加速后续处理
            if self.db and item.get("product_id"):
                try:
                    with self.db.connection() as conn:
                        conn.cursor().execute(
                            "UPDATE products SET product_url=%s WHERE id=%s AND (product_url IS NULL OR product_url='')",
                            (f"{clean_base}/token/{token}/{prod_id}", item["product_id"])
                        )
                except Exception:
                    pass

            try:
                data = {
                    "token": token,
                    "quantity_data[0][product_id]": str(prod_id),
                    "quantity_data[0][quantity]": str(valid_qty),
                    "do-lookup-cart-html": "0",
                }
                resp = session.post(add_api_url, data=data, timeout=12)
                res_json = {}
                try:
                    res_json = resp.json()
                except Exception:
                    pass

                if resp.status_code == 200 and res_json.get("result") in (1, True):
                    synced_count += 1
                else:
                    err_msg = res_json.get("message") or resp.text[:120]
                    failed_items.append({
                        "name": p_name,
                        "sku": sku,
                        "reason": f"接口返回: {err_msg}",
                    })
            except Exception as e:
                failed_items.append({
                    "name": p_name,
                    "sku": sku,
                    "reason": f"请求异常: {str(e)}",
                })

        return {
            "success": synced_count > 0,
            "message": f"成功将 {synced_count}/{len(items)} 件商品添加至 SmartyCart 网站购物车",
            "synced_count": synced_count,
            "total_items": len(items),
            "cart_url": cart_url,
            "adjusted_items": adjusted_items,
            "failed_items": failed_items,
        }

    def _resolve_smarty_prod_id(self, session: requests.Session, base_url: str, token: str, item: dict) -> Optional[str]:
        """解析 SmartyCart 内部 product_id"""
        # 1. 从已有的 product_url 提取 (/token/xxx/4074508)
        p_url = item.get("product_url") or ""
        m = re.search(r'/token/[a-f0-9]+/(\d{7,8})', p_url)
        if m:
            return m.group(1)

        # 2. 如果 item 中的 raw_data 或 sku 本身就是 7 位商品主键 ID (如 4074508, 3702774)
        sku = (item.get("sku") or "").strip()
        if re.match(r'^[34]\d{6}$', sku):
            return sku

        # 3. 通过 SmartyCart 官方关键词搜索精确定位
        search_kw = sku if sku else (item.get("name") or "")[:30]
        if not search_kw:
            return None

        try:
            search_url = f"{base_url}/token/{token}?keyword={requests.utils.quote(search_kw)}"
            r = session.get(search_url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("div.item")
            for c in cards:
                inp = c.select_one("input.quantity[data-product-id], input.id")
                if inp:
                    pid = inp.get("data-product-id") or inp.get("value")
                    if pid:
                        return str(pid)
                c_id = c.get("id") or ""
                if c_id.startswith("item_"):
                    return c_id.replace("item_", "").strip()
        except Exception as e:
            logger.debug(f"Smarty 搜索商品失败: {e}")

        return None

    # ================================================================
    # 2. Diego (Distrinimay) 同步适配器
    # ================================================================
    def _sync_diego(self, supplier: dict, items: list[dict], auto_adjust: bool, cookies_str: str) -> dict:
        base_url = supplier.get("base_url") or "https://distrinimay.com.ar"
        clean_base = base_url.rstrip("/")
        cart_url = f"{clean_base}/carrito"
        api_url = f"{clean_base}/jsyphp/carrito.php"

        cookies = {}
        for part in cookies_str.split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                cookies[k] = v

        if not cookies.get("PHPSESSID"):
            return {
                "success": False,
                "message": "Diego (Distri-Nimay) 要求用户登录后方可操作购物车。请在供应商设置中填入有效 manual_cookies: PHPSESSID=xxx",
                "synced_count": 0,
                "total_items": len(items),
                "cart_url": cart_url,
                "adjusted_items": [],
                "failed_items": [],
            }

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Referer": f"{clean_base}/cat/",
            "Origin": clean_base,
            "X-Requested-With": "XMLHttpRequest",
        })
        session.cookies.update(cookies)

        synced_count = 0
        adjusted_items = []
        failed_items = []

        for item in items:
            p_name = item.get("name") or ""
            sku = (item.get("sku") or "").strip()
            orig_qty = int(item.get("quantity") or 1)
            min_q = int(item.get("min_qty") or 1)
            pkg_q = int(item.get("package_qty") or 1)
            price = float(item.get("price") or 0)

            # Diego 数量必须为 frac 的整数倍
            valid_qty = calc_valid_quantity(orig_qty, min_q, pkg_q) if auto_adjust else orig_qty
            if valid_qty != orig_qty:
                adjusted_items.append({
                    "product_id": item.get("product_id"),
                    "name": p_name,
                    "old_quantity": orig_qty,
                    "new_quantity": valid_qty,
                    "min_qty": min_q,
                    "package_qty": pkg_q,
                })
                if self.db and item.get("product_id"):
                    try:
                        self.db.update_cart_quantity(item["product_id"], valid_qty)
                    except Exception:
                        pass

            # 解析 Diego 的 produ 代码
            produ_id = sku
            if not produ_id:
                img_url = item.get("image_url") or ""
                m_img = re.search(r'/catalogo/(\d+)\.', img_url)
                if m_img:
                    produ_id = m_img.group(1)

            if not produ_id:
                failed_items.append({
                    "name": p_name,
                    "sku": sku,
                    "reason": "未找到 Diego 商品编号 (produ/Cod)",
                })
                continue

            if self.db and item.get("product_id") and not sku:
                try:
                    with self.db.connection() as conn:
                        conn.cursor().execute(
                            "UPDATE products SET sku=%s WHERE id=%s AND (sku IS NULL OR sku='')",
                            (produ_id, item["product_id"])
                        )
                except Exception:
                    pass

            try:
                data = {
                    "produ": str(produ_id),
                    "cantidad": str(valid_qty),
                    "descripcion": p_name,
                    "importe": str(price),
                    "accion": "compra",
                }
                resp = session.post(api_url, data=data, timeout=12)
                txt = resp.text.strip()
                if resp.status_code == 200 and (txt in ("1", "0", "") or '"producto"' in txt or (txt.startswith("[") and txt.endswith("]"))):
                    # 成功入车（返回 1, 0, 或当前购物车商品 JSON 数组）
                    synced_count += 1
                elif resp.status_code == 403:
                    failed_items.append({
                        "name": p_name,
                        "sku": sku,
                        "reason": "登录凭证已失效 (HTTP 403)，请重新从浏览器复制 PHPSESSID Cookie 更新到供应商配置中",
                    })
                else:
                    failed_items.append({
                        "name": p_name,
                        "sku": sku,
                        "reason": f"添加失败 HTTP {resp.status_code}: {resp.text[:100]}",
                    })
            except Exception as e:
                failed_items.append({
                    "name": p_name,
                    "sku": sku,
                    "reason": f"请求异常: {str(e)}",
                })

        return {
            "success": synced_count > 0,
            "message": f"成功将 {synced_count}/{len(items)} 件商品添加至 Diego 网站购物车",
            "synced_count": synced_count,
            "total_items": len(items),
            "cart_url": cart_url,
            "adjusted_items": adjusted_items,
            "failed_items": failed_items,
        }

    # ================================================================
    # 3. Bella Central (WooCommerce) 同步适配器
    # ================================================================
    def _sync_bella_central(self, supplier: dict, items: list[dict], auto_adjust: bool, cookies_str: str) -> dict:
        base_url = supplier.get("base_url") or "https://bellacentral.com.ar"
        clean_base = base_url.rstrip("/")
        cart_url = f"{clean_base}/carro/"

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        })

        if cookies_str:
            cookies = {}
            for part in cookies_str.split(";"):
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    cookies[k] = v
            session.cookies.update(cookies)

        synced_count = 0
        adjusted_items = []
        failed_items = []

        for item in items:
            p_name = item.get("name") or ""
            sku = (item.get("sku") or "").strip()
            orig_qty = int(item.get("quantity") or 1)
            min_q = int(item.get("min_qty") or 1)
            pkg_q = int(item.get("package_qty") or 1)

            valid_qty = calc_valid_quantity(orig_qty, min_q, pkg_q) if auto_adjust else orig_qty
            if valid_qty != orig_qty:
                adjusted_items.append({
                    "product_id": item.get("product_id"),
                    "name": p_name,
                    "old_quantity": orig_qty,
                    "new_quantity": valid_qty,
                    "min_qty": min_q,
                    "package_qty": pkg_q,
                })
                if self.db and item.get("product_id"):
                    try:
                        self.db.update_cart_quantity(item["product_id"], valid_qty)
                    except Exception:
                        pass

            # 解析 WooCommerce 产品 ID
            wc_id = self._resolve_bella_product_id(session, clean_base, item)
            if not wc_id:
                failed_items.append({
                    "name": p_name,
                    "sku": sku,
                    "reason": "未能解析到 Bella Central 的 WooCommerce 商品 ID",
                })
                continue

            item["_wc_id"] = wc_id
            item["_valid_qty"] = valid_qty

            try:
                # 使用 WooCommerce 标准快速加购链接: ?add-to-cart={id}&quantity={qty}
                add_url = f"{clean_base}/?add-to-cart={wc_id}&quantity={valid_qty}"
                resp = session.get(add_url, timeout=15, allow_redirects=True)
                if resp.status_code == 200:
                    synced_count += 1
                else:
                    failed_items.append({
                        "name": p_name,
                        "sku": sku,
                        "reason": f"加购返回 HTTP {resp.status_code}",
                    })
            except Exception as e:
                failed_items.append({
                    "name": p_name,
                    "sku": sku,
                    "reason": f"请求异常: {str(e)}",
                })

        # 构建供用户在浏览器 Console 中一键运行的加购脚本
        valid_items_for_script = [
            {"id": it["_wc_id"], "qty": it["_valid_qty"], "name": (it.get("name") or "")[:35]}
            for it in items if it.get("_wc_id")
        ]
        script_json = json.dumps(valid_items_for_script, ensure_ascii=False)
        browser_script = f"""(async () => {{
  const items = {script_json};
  console.log('🚀 开始向 Bella Central 购物车添加 ' + items.length + ' 件商品...');
  let added = 0;
  for (let i = 0; i < items.length; i++) {{
    const it = items[i];
    try {{
      const fd = new FormData();
      fd.append('product_id', it.id);
      fd.append('quantity', it.qty);
      const res = await fetch('/?wc-ajax=add_to_cart', {{ method: 'POST', body: fd }});
      if (res.ok) {{
        added++;
        console.log('[' + (i+1) + '/' + items.length + '] ✅ 已加购: ' + it.name + ' (' + it.qty + '件)');
      }} else {{
        await fetch('/?add-to-cart=' + it.id + '&quantity=' + it.qty);
        added++;
        console.log('[' + (i+1) + '/' + items.length + '] ✅ (GET)已加购: ' + it.name + ' (' + it.qty + '件)');
      }}
    }} catch(e) {{
      console.error('❌ 添加失败: ' + it.name, e);
    }}
  }}
  alert('🎉 成功将 ' + added + '/' + items.length + ' 件商品加入购物车！点击确定刷新购物车。');
  location.href = '/carro/';
}})();"""

        return {
            "success": synced_count > 0,
            "message": f"成功将 {synced_count}/{len(items)} 件商品添加至 Bella Central 网站购物车",
            "synced_count": synced_count,
            "total_items": len(items),
            "cart_url": cart_url,
            "adjusted_items": adjusted_items,
            "failed_items": failed_items,
            "browser_script": browser_script,
        }

    def _resolve_bella_product_id(self, session: requests.Session, base_url: str, item: dict) -> Optional[str]:
        # 1. sku 本身如果是数字 ID
        sku = (item.get("sku") or "").strip()
        if re.match(r'^\d+$', sku):
            return sku

        # 2. 从详情页获取 postid
        p_url = item.get("product_url") or ""
        if p_url:
            try:
                r = session.get(p_url, timeout=10)
                res_id = None
                m = re.search(r'postid-(\d+)', r.text)
                m2 = re.search(r'name=["\']add-to-cart["\']\s+value=["\'](\d+)["\']', r.text)
                if m:
                    res_id = m.group(1)
                elif m2:
                    res_id = m2.group(1)

                if res_id and self.db and item.get("product_id"):
                    try:
                        with self.db.connection() as conn:
                            conn.cursor().execute(
                                "UPDATE products SET sku=%s WHERE id=%s AND (sku IS NULL OR sku='')",
                                (res_id, item["product_id"])
                            )
                    except Exception:
                        pass
                return res_id
            except Exception:
                pass
        return None

    # ================================================================
    # 4. sfpanda (Jumpseller) 同步适配器
    # ================================================================
    def _sync_sfpanda(self, supplier: dict, items: list[dict], auto_adjust: bool) -> dict:
        base_url = supplier.get("base_url") or "https://www.sfpanda.com.ar"
        clean_base = "https://www.sfpanda.com.ar"
        cart_url = f"{clean_base}/cart"

        synced_count = 0
        adjusted_items = []
        failed_items = []

        # 准备入车数据
        prepared = []
        for item in items:
            p_name = item.get("name") or ""
            sku = (item.get("sku") or "").strip()
            orig_qty = int(item.get("quantity") or 1)
            min_q = int(item.get("min_qty") or 1)
            pkg_q = int(item.get("package_qty") or 1)

            valid_qty = calc_valid_quantity(orig_qty, min_q, pkg_q) if auto_adjust else orig_qty
            if valid_qty != orig_qty:
                adjusted_items.append({
                    "product_id": item.get("product_id"),
                    "name": p_name,
                    "old_quantity": orig_qty,
                    "new_quantity": valid_qty,
                    "min_qty": min_q,
                    "package_qty": pkg_q,
                })
                if self.db and item.get("product_id"):
                    try:
                        self.db.update_cart_quantity(item["product_id"], valid_qty)
                    except Exception:
                        pass

            # sfpanda SKU 就是 Jumpseller 商品 ID
            j_id = self._resolve_sfpanda_id(item)
            if not j_id:
                failed_items.append({
                    "name": p_name,
                    "sku": sku,
                    "reason": "未找到 sfpanda 商品 ID",
                })
                continue
            prepared.append((j_id, valid_qty, p_name, sku))

        if not prepared:
            return {
                "success": False,
                "message": "未能解析到任何合法的 sfpanda 商品 ID",
                "synced_count": 0,
                "total_items": len(items),
                "cart_url": cart_url,
                "adjusted_items": adjusted_items,
                "failed_items": failed_items,
            }

        # 使用 Playwright 批量执行 Jumpseller.addProductToCart
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                    locale="es-AR",
                )
                page = context.new_page()
                page.goto(f"{clean_base}/productos", wait_until="domcontentloaded", timeout=30000)

                for j_id, qty, p_name, sku in prepared:
                    try:
                        js_code = f"""
                        new Promise((resolve) => {{
                            if (typeof Jumpseller !== 'undefined' && Jumpseller.addProductToCart) {{
                                Jumpseller.addProductToCart('{j_id}', {qty}, {{}}, {{
                                    callback: function(cart) {{ resolve(true); }}
                                }});
                            }} else {{
                                resolve(false);
                            }}
                        }})
                        """
                        res = page.evaluate(js_code)
                        if res:
                            synced_count += 1
                        else:
                            failed_items.append({
                                "name": p_name,
                                "sku": sku,
                                "reason": "Jumpseller 客户端未初始化或加购失败",
                            })
                    except Exception as e:
                        failed_items.append({
                            "name": p_name,
                            "sku": sku,
                            "reason": f"加购异常: {str(e)}",
                        })

                browser.close()
        except Exception as e:
            logger.error(f"Playwright 执行 sfpanda 同步失败: {e}")
            return {
                "success": False,
                "message": f"sfpanda 同步执行失败: {str(e)}",
                "synced_count": synced_count,
                "total_items": len(items),
                "cart_url": cart_url,
                "adjusted_items": adjusted_items,
                "failed_items": failed_items,
            }

        return {
            "success": synced_count > 0,
            "message": f"成功将 {synced_count}/{len(items)} 件商品添加至 sfpanda 网站购物车",
            "synced_count": synced_count,
            "total_items": len(items),
            "cart_url": cart_url,
            "adjusted_items": adjusted_items,
            "failed_items": failed_items,
        }

    def _resolve_sfpanda_id(self, item: dict) -> Optional[str]:
        sku = (item.get("sku") or "").strip()
        if re.match(r'^\d+$', sku):
            return sku
        p_url = item.get("product_url") or ""
        if p_url:
            m = re.search(r'/cart/add/(\d+)', p_url)
            if m:
                return m.group(1)
        return None

    # ================================================================
    # 5. OSA (Tiendanube) 同步适配器
    # ================================================================
    def _sync_osa(self, supplier: dict, items: list[dict], auto_adjust: bool, cookies_str: str) -> dict:
        base_url = supplier.get("base_url") or "https://www.osadistribuidora.com.ar"
        clean_base = base_url.rstrip("/")
        cart_url = f"{clean_base}/carrito/"
        add_url = f"{clean_base}/comprar/"

        cookies = {}
        for part in cookies_str.split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                cookies[k] = v

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Referer": f"{clean_base}/productos/",
        })
        if cookies:
            session.cookies.update(cookies)

        synced_count = 0
        adjusted_items = []
        failed_items = []

        for item in items:
            p_name = item.get("name") or ""
            sku = (item.get("sku") or "").strip()
            orig_qty = int(item.get("quantity") or 1)
            min_q = int(item.get("min_qty") or 1)
            pkg_q = int(item.get("package_qty") or 1)

            valid_qty = calc_valid_quantity(orig_qty, min_q, pkg_q) if auto_adjust else orig_qty
            if valid_qty != orig_qty:
                adjusted_items.append({
                    "product_id": item.get("product_id"),
                    "name": p_name,
                    "old_quantity": orig_qty,
                    "new_quantity": valid_qty,
                    "min_qty": min_q,
                    "package_qty": pkg_q,
                })
                if self.db and item.get("product_id"):
                    try:
                        self.db.update_cart_quantity(item["product_id"], valid_qty)
                    except Exception:
                        pass

            # 解析 Tiendanube 的加购变体 ID (add_to_cart)
            cart_var_id = self._resolve_osa_variant_id(session, clean_base, item)
            if not cart_var_id:
                failed_items.append({
                    "name": p_name,
                    "sku": sku,
                    "reason": "未能解析到 OSA 的 Tiendanube 变体加购 ID",
                })
                continue

            try:
                data = {
                    "add_to_cart": str(cart_var_id),
                    "quantity": str(valid_qty),
                }
                resp = session.post(add_url, data=data, timeout=12, allow_redirects=False)
                if resp.status_code in (200, 302):
                    loc = resp.headers.get("Location") or ""
                    if "contacto" in loc:
                        failed_items.append({
                            "name": p_name,
                            "sku": sku,
                            "reason": "该商品处于待询价状态或需要专属批发账号登录，已跳转至询价页面",
                        })
                    else:
                        synced_count += 1
                else:
                    failed_items.append({
                        "name": p_name,
                        "sku": sku,
                        "reason": f"加购返回 HTTP {resp.status_code}",
                    })
            except Exception as e:
                failed_items.append({
                    "name": p_name,
                    "sku": sku,
                    "reason": f"请求异常: {str(e)}",
                })

        return {
            "success": synced_count > 0,
            "message": f"成功将 {synced_count}/{len(items)} 件商品添加至 OSA 网站购物车",
            "synced_count": synced_count,
            "total_items": len(items),
            "cart_url": cart_url,
            "adjusted_items": adjusted_items,
            "failed_items": failed_items,
        }

    def _resolve_osa_variant_id(self, session: requests.Session, base_url: str, item: dict) -> Optional[str]:
        sku = (item.get("sku") or "").strip()
        if re.match(r'^\d{7,10}$', sku):
            return sku
        p_url = item.get("product_url") or ""
        if p_url:
            try:
                r = session.get(p_url, timeout=10)
                m = re.search(r'name=["\']add_to_cart["\']\s+value=["\'](\d+)["\']', r.text)
                if m:
                    return m.group(1)
            except Exception:
                pass
        return None
