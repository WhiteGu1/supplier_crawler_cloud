"""
supplier_crawler/crawler/smartycart_spider.py
SmartyCart (catalog / *.smarty.com.ar) 专用异步高速爬虫

设计要点：
1. 未登录状态下 SmartyCart /token/<token> 根目录最多翻到第 30 页（720 条），第 31 页会 302 跳转到 /login。
2. 页面顶部 div.desktop-nav 暴露了完整公开分类树，每个分类内部数量远低于 720 条（通常 <= 18 页），
   通过按“叶子类目 -> 父类目(Ver Todo) -> Novedades/Oportunidades -> 根目录兜底”的优先级遍历并按商品 ID 去重，
   可以在不绕过登录鉴权的前提下完整抓取全店公开商品。
3. 支持优惠净价（data-unit-price / .discountPrice）或原价（prefer_original_price=true）提取，并解析 Bulto 包装数、
   跳过 /img/no_img.jpg 占位图，实时增量写入数据库与本地图片。
"""
import asyncio
import logging
import os
import re
from datetime import datetime
from typing import Optional
from urllib.parse import parse_qs, urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from .spider import ImageDownloader, ProductItem, SupplierConfig, USER_AGENTS, clean_price

logger = logging.getLogger(__name__)

_PROMO_SECTION_KEYWORDS = (
    "novedades",
    "oportunidades",
    "ofertas",
    "oferta",
    "promo",
    "promociones",
    "destacados",
    "liquidacion",
)


def resolve_smartycart_url(raw_url: str) -> tuple[str, str, str]:
    """
    解析 SmartyCart 入口链接（兼容 short links 如 share.google 以及子域 如 nativohome.smarty.com.ar）。
    返回: (base_url, list_url, token)
    统一将 base_url 定位到 Cloudflare 节点 https://catalog.smarty.com.ar 避免直连源站 IP 超时。
    """
    import requests
    target = (raw_url or "").strip()
    m_tok = re.search(r"/token/([a-f0-9]+)", target, re.I)
    if not m_tok:
        try:
            s = requests.Session()
            s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            cur = target
            for _ in range(5):
                r = s.get(cur, allow_redirects=False, timeout=8)
                loc = r.headers.get("Location") or ""
                m = re.search(r"/token/([a-f0-9]+)", loc, re.I)
                if m:
                    target = loc
                    m_tok = m
                    break
                if not loc:
                    break
                cur = loc
        except Exception as e:
            logger.warning(f"解析短链重定向失败 {raw_url}: {e}")

    token = m_tok.group(1) if m_tok else ""
    base_url = "https://catalog.smarty.com.ar"
    list_url = f"{base_url}/token/{token}" if token else target
    return base_url, list_url, token


class SmartyCartSpider:
    """SmartyCart token 目录专用异步爬虫（兼容 Scheduler 接口）。"""

    def __init__(self, config: SupplierConfig, db_manager=None, log_id: int = None):
        self.config = config
        self.db = db_manager
        self.log_id = log_id

        # 统一通过 resolve_smartycart_url 规范化为 Cloudflare 节点与有效 token
        raw_target = config.product_list_url or config.base_url or ""
        base_url, list_url, token = resolve_smartycart_url(raw_target)

        self.base_url = base_url.rstrip("/")
        self.list_url = list_url.rstrip("/")
        self.token_base = f"{self.base_url}/token/{token}" if token else ""

        self.request_delay = max(0.15, float(config.request_delay or 0.4))
        self.img_downloader = ImageDownloader()
        self.stats = {
            "pages_crawled": 0,
            "products_found": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }
        self.on_item_saved = None
        self._cancelled = False

    def _make_headers(self) -> dict:
        import random
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
            "Referer": self.list_url,
        }

    def _prefer_original_price(self) -> bool:
        selectors = self.config.selectors or {}
        if "prefer_original_price" in selectors:
            return bool(selectors.get("prefer_original_price"))
        return "benabi" in (self.config.name or "").lower()

    async def _report_progress(self):
        """实时回写爬取进度到数据库。"""
        if self.db and self.log_id:
            try:
                self.db.update_crawl_log_progress(
                    self.log_id,
                    self.stats["pages_crawled"],
                    self.stats["products_found"],
                    self.stats["errors"],
                )
            except Exception:
                pass

    async def _fetch_html(self, session: aiohttp.ClientSession, url: str) -> tuple[Optional[str], str]:
        """请求页面 HTML；若被重定向到 /login 或返回鉴权状态则干净停止当前分支。"""
        for attempt in range(4):
            if self._cancelled:
                return None, url
            try:
                req_timeout = max(15, int(self.config.timeout or 30))
                timeout = aiohttp.ClientTimeout(total=req_timeout, connect=10)
                async with session.get(url, timeout=timeout, allow_redirects=True) as resp:
                    final_url = str(resp.url)
                    if "/login" in urlparse(final_url).path.lower() or resp.status in (401, 403):
                        logger.info(f"[{self.config.name}] 遇到登录跳转({resp.status} -> {final_url})，停止该分支翻页")
                        return None, final_url
                    if resp.status == 200:
                        return await resp.text(errors="replace"), final_url
                    if resp.status in (429, 500, 502, 503, 504):
                        wait = 2.0 * (2 ** attempt)
                        logger.warning(f"[{self.config.name}] HTTP {resp.status} ({url})，{wait:.1f}s 后重试")
                        await asyncio.sleep(wait)
                        continue
                    logger.warning(f"[{self.config.name}] 请求失败 HTTP {resp.status}: {url}")
                    self.stats["errors"] += 1
                    return None, final_url
            except asyncio.CancelledError:
                raise
            except Exception as e:
                if attempt < 3:
                    wait = 5.0 * (attempt + 1)
                    logger.warning(f"[{self.config.name}] 连接异常重试({attempt + 1}/3, {wait:.0f}s后) {url}: {e}")
                    await asyncio.sleep(wait)
                else:
                    logger.error(f"[{self.config.name}] 请求异常 {url}: {e}")
                    self.stats["errors"] += 1
                    return None, url
        return None, url

    @staticmethod
    def _clean_cat_label(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "")).strip()

    @staticmethod
    def _extract_category_id(url: str) -> str:
        qs = parse_qs(urlparse(url).query)
        vals = qs.get("category_id")
        return vals[0].strip() if vals else ""

    def _extract_category_targets(self, soup: BeautifulSoup) -> list[tuple[str, str, int]]:
        """
        从 div.desktop-nav 提取公开分类链接并按 (priority DESC, 出现顺序) 排序：
        priority=3: 常规部门下的细分子类（如 Libreria > Escolar）
        priority=2: 常规部门父类 / Ver Todo（如 Libreria）
        priority=1: 促销/新品合集（如 Novedades, OPORTUNIDADES）
        priority=0: 根目录全量页（兜底抓取未归类商品）
        """
        raw_targets: list[tuple[str, str, int]] = []
        nav = soup.select_one("div.desktop-nav")
        top_items = nav.find_all("div", class_="nav-list-item", recursive=False) if nav else []

        for ti in top_items:
            top_a = ti.find("a", recursive=False)
            top_label = self._clean_cat_label(top_a.get_text(" ", strip=True) if top_a else "")
            top_href = (top_a.get("href") or "").strip() if top_a else ""
            is_promo = any(kw in top_label.lower() for kw in _PROMO_SECTION_KEYWORDS)

            sub_links: list[tuple[str, str]] = []
            ver_todo_url = ""
            for a in ti.select(".dropdown-menu a[href*='category_id']"):
                href = (a.get("href") or "").strip()
                if not href or href.startswith("#"):
                    continue
                abs_url = urljoin(self.base_url + "/", href)
                sub_label = self._clean_cat_label(a.get_text(" ", strip=True))
                if not sub_label:
                    continue
                if "todo" in sub_label.lower():
                    if not ver_todo_url:
                        ver_todo_url = abs_url
                    continue
                if top_label and sub_label.lower() != top_label.lower():
                    cat_path = f"{top_label} > {sub_label}"
                else:
                    cat_path = sub_label or top_label
                sub_links.append((abs_url, cat_path))

            if sub_links:
                sub_prio = 1 if is_promo else 3
                for sub_url, cat_path in sub_links:
                    raw_targets.append((sub_url, cat_path, sub_prio))

            parent_url = ver_todo_url
            if not parent_url and "category_id" in top_href:
                parent_url = urljoin(self.base_url + "/", top_href)
            if parent_url and top_label:
                parent_prio = 1 if is_promo else 2
                raw_targets.append((parent_url, top_label, parent_prio))

        # 排序并按 category_id 去重，保证高优先级分类先出现
        raw_targets.sort(key=lambda t: -t[2])
        deduped: list[tuple[str, str, int]] = []
        seen_cat_ids: set[str] = set()
        seen_urls: set[str] = set()
        for url, cat_path, prio in raw_targets:
            cid = self._extract_category_id(url)
            if cid:
                if cid in seen_cat_ids:
                    continue
                seen_cat_ids.add(cid)
            elif url in seen_urls:
                continue
            seen_urls.add(url)
            deduped.append((url, cat_path, prio))

        # 根目录兜底放在最后
        deduped.append((self.list_url, "", 0))
        return deduped

    def _extract_price(self, card) -> float:
        prefer_orig = self._prefer_original_price()
        price_el = card.select_one("div.item-price")
        btn_el = card.select_one(".selectQuantityButton[data-unit-price]")
        unit_price = 0.0
        if btn_el:
            raw_up = (btn_el.get("data-unit-price") or "").strip()
            if re.fullmatch(r"\d+(?:\.\d+)?", raw_up):
                unit_price = float(raw_up)
            elif raw_up:
                unit_price = clean_price(raw_up)

        if not prefer_orig and unit_price > 0:
            return unit_price

        if price_el:
            selectors_order = (
                [".origDiscountPrice", ".origPrice", ".discountPrice", ".product-price"]
                if prefer_orig
                else [".discountPrice", ".origPrice", ".origDiscountPrice", ".product-price"]
            )
            for sel in selectors_order:
                el = price_el.select_one(sel)
                if el:
                    val = clean_price(el.get_text(" ", strip=True))
                    if val > 0:
                        return val
            val = clean_price(price_el.get_text(" ", strip=True))
            if val > 0:
                return val

        return unit_price

    def _extract_image_url(self, card) -> str:
        candidates = []
        gal = card.select_one("a.lnkGallery")
        if gal and gal.get("data-src"):
            candidates.append(gal.get("data-src"))
        for img_sel in ("img.item-image-primary", "img"):
            img = card.select_one(img_sel)
            if img:
                candidates.extend([img.get("data-src"), img.get("src")])
                break

        for raw in candidates:
            raw = (raw or "").strip()
            if not raw or raw.startswith("data:") or "no_img" in raw.lower():
                continue
            return urljoin(self.base_url + "/", raw)
        return ""

    def _parse_page(self, html: str, category_path: str = "", category_prio: int = 0) -> tuple[list[ProductItem], Optional[str], Optional[int]]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("div.item")
        items: list[ProductItem] = []

        for card in cards:
            raw_id = (card.get("id") or "").strip()
            m_id = re.search(r"item_(\d+)", raw_id)
            if not m_id:
                btn = card.select_one(".selectQuantityButton[data-prod-id], [data-prod-id]")
                prod_id = (btn.get("data-prod-id") or "").strip() if btn else ""
            else:
                prod_id = m_id.group(1)

            name_el = card.select_one("h5.item-name")
            name = name_el.get_text(" ", strip=True) if name_el else ""
            if not name:
                continue

            price = self._extract_price(card)
            if price <= 0:
                continue

            sku_el = card.select_one("span.reference, .reference")
            sku = sku_el.get_text(strip=True) if sku_el else ""
            if not sku:
                sku = prod_id

            img_url = self._extract_image_url(card)

            min_qty = 1
            package_qty = 1
            qty_el = card.select_one(".quantity_restrictions")
            if qty_el:
                qtext = qty_el.get_text(" ", strip=True)
                m_bulto = re.search(r"Bulto\s*:\s*(\d+)", qtext, re.I)
                if m_bulto:
                    package_qty = max(1, int(m_bulto.group(1)))
                m_min = re.search(r"M[íi]nimo\s*:\s*(\d+)", qtext, re.I)
                if m_min:
                    min_qty = max(1, int(m_min.group(1)))

            cat_el = card.select_one("span.item-categories")
            card_cat = self._clean_cat_label(cat_el.get_text(" ", strip=True) if cat_el else "")
            if card_cat and "," in card_cat:
                card_cat = " > ".join(p.strip() for p in card_cat.split(",") if p.strip())
            final_category = category_path or card_cat

            if self.token_base and prod_id:
                product_url = f"{self.token_base}/{prod_id}"
            else:
                link_el = card.select_one("a[href]:not(.lnkGallery)")
                href = (link_el.get("href") or "").strip() if link_el else ""
                product_url = urljoin(self.base_url + "/", href) if href else f"{self.list_url}#item_{prod_id or len(items)}"

            items.append(ProductItem(
                name=name[:200],
                price=price,
                currency="ARS",
                sku=sku[:100],
                category=final_category[:100],
                image_url=img_url,
                product_url=product_url[:500],
                supplier_id=self.config.id,
                min_qty=min_qty,
                package_qty=package_qty,
                raw_data={
                    "smarty_id": prod_id or name,
                    "cat_prio": category_prio,
                    "source": "smartycart_spider",
                },
            ))

        next_url = None
        next_el = soup.select_one("a[rel=next]")
        if next_el and next_el.get("href"):
            next_url = urljoin(self.base_url + "/", next_el["href"].strip())

        total_count = None
        cnt_el = soup.select_one(".counter")
        if cnt_el:
            m_tot = re.search(r"\bde\s+(\d+)\b", cnt_el.get_text(" ", strip=True), re.I)
            if m_tot:
                total_count = int(m_tot.group(1))

        return items, next_url, total_count

    def _load_known_images(self) -> dict[str, str]:
        """从数据库加载已存在且磁盘可见的本地图片（product_url -> image_local），避免重复下载。"""
        known: dict[str, str] = {}
        if not self.db or not self.config.id:
            return known
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            with self.db.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT product_url, image_local FROM products WHERE supplier_id=%s AND image_local IS NOT NULL AND image_local != ''",
                    (self.config.id,),
                )
                for p_url, img_local in cursor.fetchall():
                    if not p_url or not img_local:
                        continue
                    abs_path = os.path.join(root_dir, img_local.lstrip("/\\").replace("/", os.sep))
                    if os.path.isfile(abs_path):
                        known[p_url.strip()] = img_local.strip()
        except Exception as e:
            logger.debug(f"[{self.config.name}] 加载已有图片缓存跳过: {e}")
        return known

    async def _download_images(self, session: aiohttp.ClientSession, items: list[ProductItem]):
        targets = [it for it in items if it.image_url and not it.image_local_path]
        if not targets:
            return
        sem = asyncio.Semaphore(3)

        async def _dl(it: ProductItem):
            async with sem:
                local = await self.img_downloader.download(session, it.image_url, self.config.name)
                if local:
                    it.image_local_path = local
                await asyncio.sleep(0.05)

        await asyncio.gather(*[_dl(it) for it in targets])

    def _save_batch(self, batch: list[ProductItem]):
        if not batch or not callable(self.on_item_saved):
            return
        try:
            self.on_item_saved(batch)
        except Exception as e:
            logger.error(f"[{self.config.name}] 增量保存回调失败: {e}")

    async def run(self) -> list[ProductItem]:
        self.stats["start_time"] = datetime.now()
        seen_items: dict[str, ProductItem] = {}
        known_images = self._load_known_images()
        if known_images:
            logger.info(f"[{self.config.name}] 已加载 {len(known_images)} 条本地图片缓存")
        per_branch_max_pages = min(int(self.config.max_pages or 500), 35)

        connector = aiohttp.TCPConnector(limit=6, limit_per_host=4, ttl_dns_cache=300, ssl=False, enable_cleanup_closed=True)
        async with aiohttp.ClientSession(headers=self._make_headers(), connector=connector) as session:
            logger.info(f"[{self.config.name}] 开始爬取 SmartyCart 目录: {self.list_url}")
            first_html, _ = await self._fetch_html(session, self.list_url)
            if not first_html:
                self.stats["end_time"] = datetime.now()
                return []

            soup = BeautifulSoup(first_html, "html.parser")
            targets = self._extract_category_targets(soup)
            logger.info(f"[{self.config.name}] 识别到 {len(targets)} 个抓取分支（含分类树与根目录兜底）")

            for idx, (start_url, cat_path, cat_prio) in enumerate(targets, 1):
                if self._cancelled:
                    break

                current_url = start_url
                branch_visited: set[str] = set()
                prev_page_keys: tuple[str, ...] = ()
                page = 1
                branch_label = cat_path or "根目录兜底"

                while current_url and page <= per_branch_max_pages and not self._cancelled:
                    if current_url in branch_visited:
                        break
                    branch_visited.add(current_url)

                    # 复用首次抓取的首页根目录 HTML，省去一次重复请求
                    if start_url == self.list_url and page == 1:
                        html = first_html
                    else:
                        if self.stats["pages_crawled"] > 0:
                            await asyncio.sleep(self.request_delay)
                        html, _ = await self._fetch_html(session, current_url)
                        if not html:
                            break

                    page_items, next_url, _ = self._parse_page(html, cat_path, cat_prio)
                    if not page_items:
                        break

                    page_keys = tuple(it.raw_data.get("smarty_id", it.name) for it in page_items)
                    if page_keys == prev_page_keys:
                        break
                    prev_page_keys = page_keys

                    to_save: list[ProductItem] = []
                    for it in page_items:
                        if it.product_url in known_images and not it.image_local_path:
                            it.image_local_path = known_images[it.product_url]
                        dedup_key = it.raw_data.get("smarty_id") or it.product_url or it.name
                        prev = seen_items.get(dedup_key)
                        if prev is None:
                            seen_items[dedup_key] = it
                            to_save.append(it)
                        else:
                            # 仅当新分类优先级严格更高且之前没有有效高优先级分类时补充分类
                            prev_prio = int(prev.raw_data.get("cat_prio", 0))
                            if it.category and cat_prio > prev_prio:
                                prev.category = it.category
                                prev.raw_data["cat_prio"] = cat_prio
                                to_save.append(prev)

                    if to_save:
                        await self._download_images(session, to_save)
                        self._save_batch(to_save)

                    self.stats["pages_crawled"] += 1
                    self.stats["products_found"] = len(seen_items)
                    await self._report_progress()

                    logger.info(
                        f"[{self.config.name}] [{idx}/{len(targets)}] {branch_label} "
                        f"第{page}页: 页面{len(page_items)}条, 新增/更新{len(to_save)}条 (累计去重: {len(seen_items)})"
                    )

                    if not next_url or next_url in branch_visited:
                        break
                    current_url = next_url
                    page += 1

        self.stats["end_time"] = datetime.now()
        duration = (self.stats["end_time"] - self.stats["start_time"]).seconds
        logger.info(
            f"[{self.config.name}] SmartyCart 爬取完成! 去重商品: {len(seen_items)} | "
            f"页数: {self.stats['pages_crawled']} | 耗时: {duration}s | 错误数: {self.stats['errors']}"
        )
        return list(seen_items.values())
