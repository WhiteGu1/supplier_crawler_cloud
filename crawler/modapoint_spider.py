"""
supplier_crawler/crawler/modapoint_spider.py
Moda Point (https://www.modapoint.com.ar/) PrestaShop 独立爬虫模块。

特点：
1. 采用 aiohttp 高并发异步抓取 PrestaShop 目录与商品卡片。
2. 优先解析页面内嵌的 cdcDatalayer 结构化数据（获取精准品牌、多级分类与价格）。
3. 结合 HTML article.product-miniature 提取高清大图(thickbox)、SKU(data-referencia)、包装数量(data-cantidad)；若卡片缺少货号退化为 MP-<id>，则结合本地已缓存映射及并发抓取详情页 `#product-details[data-product]` 补全真实货号与品牌。
4. 分页动态自适应识别（从 https://www.modapoint.com.ar/134-productos 逐页抓取）。
5. 异步并发下载高清图片并按页实时增量入库。
"""
import asyncio
import aiohttp
import json
import logging
import random
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .spider import ProductItem, SupplierConfig, ImageDownloader, USER_AGENTS, clean_price

logger = logging.getLogger(__name__)


class ModaPointSpider:
    """Moda Point 专有异步爬虫"""

    def __init__(self, config: SupplierConfig, db_manager=None, log_id: int = None):
        self.config = config
        self.db = db_manager
        self.log_id = log_id
        self.downloader = ImageDownloader()
        self.products: list[ProductItem] = []
        self.stats = {
            "pages_crawled": 0,
            "products_found": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }
        self._cancelled = False
        self.on_item_saved = None

        # 目录入口 URL
        self.list_url = (self.config.product_list_url or "").strip()
        if not self.list_url or "modapoint" not in self.list_url:
            self.list_url = "https://www.modapoint.com.ar/134-productos"

    def _make_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }

    async def _report_progress(self):
        """实时回写爬取进度到数据库"""
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

    def _extract_cdc_datalayer_items(self, html: str) -> dict[str, dict]:
        """从页面内嵌 cdcDatalayer 脚本提取 item_id -> item 字典"""
        dl_items: dict[str, dict] = {}
        m_dl = re.search(r"let\s+cdcDatalayer\s*=\s*(\{.*?\});\s*(?:/\*|let|\n)", html, re.S)
        if m_dl:
            try:
                dl_json = json.loads(m_dl.group(1))
                for it in dl_json.get("ecommerce", {}).get("items", []):
                    dl_items[str(it.get("item_id"))] = it
            except Exception as e:
                logger.debug(f"[{self.config.name}] cdcDatalayer 解析异常: {e}")
        return dl_items

    def _parse_detail_fields(self, html: str) -> dict:
        """从商品详情页提取真实 SKU(reference)、品牌、分类与库存/简介"""
        soup = BeautifulSoup(html, "html.parser")
        info: dict = {}

        dp = soup.select_one("#product-details")
        if dp and dp.get("data-product"):
            try:
                data = json.loads(dp["data-product"])
                ref = str(data.get("reference") or "").strip()
                if ref:
                    info["sku"] = ref[:100]
                qty = data.get("quantity")
                if qty is not None:
                    try:
                        info["stock"] = int(qty)
                    except (TypeError, ValueError):
                        pass
                desc_html = data.get("description_short") or data.get("description") or ""
                if desc_html:
                    desc_txt = BeautifulSoup(desc_html, "html.parser").get_text(" ", strip=True)
                    if desc_txt:
                        info["description"] = desc_txt[:500]
            except Exception as e:
                logger.debug(f"[{self.config.name}] 详情页 data-product 解析异常: {e}")

        if not info.get("sku"):
            sku_el = soup.select_one('[itemprop="sku"]')
            if sku_el:
                sku_txt = (sku_el.get("content") or sku_el.get_text(strip=True) or "").strip()
                if sku_txt:
                    info["sku"] = sku_txt[:100]

        dl_items = self._extract_cdc_datalayer_items(html)
        if dl_items:
            dl = next(iter(dl_items.values()))
            brand = (dl.get("item_brand") or "").strip()
            if brand and brand not in ("No Especificada", "Otro"):
                info["brand"] = brand[:100]
            cats = [dl.get("item_category2"), dl.get("item_category3"), dl.get("item_category4")]
            cats = [c.strip() for c in cats if c and c.strip() and c.strip() != "Productos"]
            if cats:
                info["category"] = " > ".join(cats)[:100]
        return info

    def _parse_page(self, html: str) -> tuple[list[ProductItem], Optional[str], int]:
        """
        解析单页 HTML：
        返回: (商品列表, 下一页 URL, 检测到的总页数)
        """
        soup = BeautifulSoup(html, "html.parser")

        # 1. 提取 cdcDatalayer 字典
        dl_items = self._extract_cdc_datalayer_items(html)

        # 2. 查找所有商品卡片
        articles = soup.find_all("article", class_="product-miniature")
        page_items: list[ProductItem] = []

        for a in articles:
            try:
                pid = str(a.get("data-id-product") or "")
                dl = dl_items.get(pid, {})

                # 商品名称
                title = dl.get("item_name")
                if not title:
                    t_el = a.select_one(".for-list.product-title a") or a.select_one(".product-title a")
                    title = t_el.get_text(strip=True) if t_el else ""
                title = title.strip()
                if not title:
                    continue

                # 价格提取 (优先 cdcDatalayer -> precio-unitario-data -> span.price)
                price = 0.0
                if dl.get("price"):
                    try:
                        price = float(dl["price"])
                    except Exception:
                        pass
                u_data = a.select_one(".precio-unitario-data")
                if price <= 0 and u_data and u_data.get("data-precio-total"):
                    try:
                        price = float(u_data.get("data-precio-total"))
                    except Exception:
                        pass
                if price <= 0:
                    p_el = a.select_one("span.price")
                    price = clean_price(p_el.get_text(strip=True) if p_el else "")

                if price <= 0:
                    continue

                # SKU / 货号 (优先 data-referencia -> MP-{pid})
                sku = u_data.get("data-referencia") if u_data else ""
                if not sku:
                    sku = f"MP-{pid}" if pid else ""

                # 品牌
                brand = (dl.get("item_brand") or "").strip()
                if brand in ("No Especificada", "Otro"):
                    brand = ""

                # 分类层级 (item_category2 > item_category3 > item_category4)
                cats = [dl.get("item_category2"), dl.get("item_category3"), dl.get("item_category4")]
                cats = [c.strip() for c in cats if c and c.strip() and c.strip() != "Productos"]
                category = " > ".join(cats)

                # 起订量与包装数 (data-cantidad 或 X6/X12 正则)
                pkg_qty = 1
                if u_data and u_data.get("data-cantidad"):
                    try:
                        pkg_qty = int(u_data.get("data-cantidad"))
                    except Exception:
                        pass
                if pkg_qty <= 1:
                    m_pkg = re.search(r"[xX](\d+)\b", title)
                    if m_pkg:
                        pkg_qty = int(m_pkg.group(1))

                min_qty = pkg_qty if pkg_qty > 1 else 1

                # 商品链接
                link_el = a.select_one("a.product-thumbnail, .product-title a")
                raw_href = link_el.get("href") if link_el else ""
                prod_url = urljoin(self.config.base_url, raw_href) if raw_href else ""

                # 若分类仍为空，从 URL slug 推测
                if not category and prod_url:
                    slug_match = re.search(r"https?://[^/]+/([^/]+)/\d+-", prod_url)
                    if slug_match:
                        category = slug_match.group(1).replace("-", " ").title()

                # 商品图片 (优先 thickbox 原图 -> src)
                img_el = a.select_one("img.img-cover") or a.select_one("img")
                img_raw = ""
                if img_el:
                    img_raw = img_el.get("data-full-size-image-url") or img_el.get("src") or ""
                img_url = urljoin(self.config.base_url, img_raw) if img_raw else ""

                item = ProductItem(
                    name=title[:300],
                    price=price,
                    currency="ARS",
                    sku=sku[:100],
                    category=category[:100],
                    description="",
                    image_url=img_url,
                    image_local_path="",
                    product_url=prod_url,
                    supplier_id=self.config.id,
                    stock=None,
                    unit="C/U",
                    brand=brand[:100],
                    min_qty=min_qty,
                    package_qty=pkg_qty,
                    raw_data=dl if dl else {"data_id": pid},
                    crawled_at=datetime.now(),
                )
                page_items.append(item)
            except Exception as e:
                logger.debug(f"[{self.config.name}] 商品卡片解析异常: {e}")
                self.stats["errors"] += 1

        # 3. 提取分页信息
        next_url = None
        next_btn = soup.select_one(".ce-pagination a[rel='next'], a.ce-pagination__arrow[rel='next'], a[rel='next']")
        if next_btn and next_btn.get("href"):
            next_url = urljoin(self.config.base_url, next_btn.get("href"))

        max_detected_page = 1
        page_nums = []
        for p_link in soup.select(".ce-pagination a, .pagination a"):
            txt = p_link.get_text(strip=True)
            if txt.isdigit():
                page_nums.append(int(txt))
        if page_nums:
            max_detected_page = max(page_nums)

        return page_items, next_url, max_detected_page

    def _load_known_meta(self) -> dict[str, tuple[str, str]]:
        """从数据库加载已解析的真实货号与品牌映射（product_url -> (sku, brand)），避免重复请求详情页"""
        meta: dict[str, tuple[str, str]] = {}
        if not self.db or not self.config.id:
            return meta
        try:
            with self.db.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT product_url, sku, brand FROM products
                       WHERE supplier_id=%s AND product_url IS NOT NULL AND product_url != ''
                         AND sku != '' AND sku NOT LIKE 'MP-%'""",
                    (self.config.id,),
                )
                for url, sku, brand in cursor.fetchall():
                    if url and sku:
                        meta[url.strip()] = (sku.strip(), (brand or "").strip())
        except Exception as e:
            logger.debug(f"[{self.config.name}] 加载已有 SKU 映射跳过: {e}")
        return meta

    async def _enrich_items_from_details(
        self,
        session: aiohttp.ClientSession,
        items: list[ProductItem],
        known_meta: dict[str, tuple[str, str]],
        include_missing_brand: bool = False,
    ) -> int:
        """
        对于列表卡片缺少 data-referencia（退化为 MP-<id>）的商品，
        优先命中数据库缓存，未命中则并发请求详情页补全真实 SKU、品牌与分类。
        返回从详情页新补全的条数。
        """
        targets: list[ProductItem] = []
        for it in items:
            missing_sku = (not it.sku) or it.sku.startswith("MP-")
            missing_brand = include_missing_brand and (not it.brand)
            if not (missing_sku or missing_brand):
                continue

            cached = known_meta.get(it.product_url)
            if cached and cached[0] and not missing_brand:
                it.sku = cached[0][:100]
                if not it.brand and cached[1]:
                    it.brand = cached[1][:100]
                continue

            if it.product_url:
                targets.append(it)

        if not targets:
            return 0

        sem = asyncio.Semaphore(6)
        enriched = 0

        async def _fetch_one(it: ProductItem):
            nonlocal enriched
            if self._cancelled:
                return
            async with sem:
                for attempt in range(2):
                    try:
                        async with session.get(it.product_url) as resp:
                            if resp.status != 200:
                                if attempt == 0 and resp.status >= 500:
                                    await asyncio.sleep(1)
                                    continue
                                return
                            d_html = await resp.text(errors="replace")
                            fields = self._parse_detail_fields(d_html)
                            if fields.get("sku"):
                                it.sku = fields["sku"]
                            if fields.get("brand") and not it.brand:
                                it.brand = fields["brand"]
                            if fields.get("category") and (not it.category or ">" not in it.category):
                                it.category = fields["category"]
                            if "stock" in fields and it.stock is None:
                                it.stock = fields["stock"]
                            if fields.get("description") and not it.description:
                                it.description = fields["description"]
                            if it.sku and not it.sku.startswith("MP-"):
                                known_meta[it.product_url] = (it.sku, it.brand)
                                enriched += 1
                            return
                    except asyncio.CancelledError:
                        self._cancelled = True
                        return
                    except Exception as e:
                        if attempt == 1:
                            logger.debug(f"[{self.config.name}] 详情页补全失败 {it.product_url}: {e}")
                        else:
                            await asyncio.sleep(1)

        await asyncio.gather(*[_fetch_one(it) for it in targets])
        return enriched

    async def run(self) -> list[ProductItem]:
        self.stats["start_time"] = datetime.now()
        logger.info(f"开始抓取 Moda Point 供应商: {self.config.name} -> {self.list_url}")
        known_meta = self._load_known_meta()

        connector = aiohttp.TCPConnector(limit=8, ssl=False, enable_cleanup_closed=True)
        timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=15)

        async with aiohttp.ClientSession(
            headers=self._make_headers(),
            connector=connector,
            timeout=timeout,
        ) as session:
            page = 1
            max_pages = self.config.max_pages or 500  # 兜底最大页
            current_url = self.list_url
            visited_urls = set()

            while page <= max_pages:
                if self._cancelled or current_url in visited_urls:
                    logger.info(f"[{self.config.name}] 抓取终止或 URL 已访问: {current_url}")
                    break
                visited_urls.add(current_url)

                logger.info(f"[{self.config.name}] 抓取第 {page} 页: {current_url}")

                html = None
                for attempt in range(3):
                    try:
                        async with session.get(current_url) as resp:
                            if resp.status == 200:
                                html = await resp.text(errors="replace")
                                break
                            elif resp.status in (400, 404):
                                logger.info(f"[{self.config.name}] 达到尾页 (HTTP {resp.status})")
                                html = None
                                break
                            else:
                                logger.warning(f"[{self.config.name}] 第 {page} 页返回 HTTP {resp.status}，重试 ({attempt+1}/3)...")
                                await asyncio.sleep(2)
                    except asyncio.CancelledError:
                        self._cancelled = True
                        break
                    except Exception as e:
                        logger.warning(f"[{self.config.name}] 第 {page} 页请求失败: {e}，重试 ({attempt+1}/3)...")
                        await asyncio.sleep(2)

                if self._cancelled:
                    break

                if not html:
                    logger.info(f"[{self.config.name}] 第 {page} 页无有效响应，结束抓取")
                    break

                page_items, next_url, detected_max = self._parse_page(html)

                if detected_max > 1:
                    if self.config.max_pages:
                        if page == 1:
                            max_pages = min(self.config.max_pages, detected_max)
                    elif page == 1 or detected_max > max_pages:
                        max_pages = detected_max
                        if page == 1:
                            logger.info(f"[{self.config.name}] 检测到总页数约为 {max_pages} 页")

                if not page_items:
                    logger.info(f"[{self.config.name}] 第 {page} 页未提取到商品，结束抓取")
                    break

                # 异步并发下载图片 + 详情页补全缺失真实 SKU (MP-<id>)
                sem = asyncio.Semaphore(12)
                async def _dl(it):
                    if not self._cancelled and it.image_url:
                        async with sem:
                            it.image_local_path = await self.downloader.download(
                                session, it.image_url, self.config.name
                            )
                _, enriched_cnt = await asyncio.gather(
                    asyncio.gather(*[_dl(it) for it in page_items]),
                    self._enrich_items_from_details(session, page_items, known_meta),
                )
                if enriched_cnt:
                    logger.info(f"[{self.config.name}] 第 {page} 页详情页补全真实货号: +{enriched_cnt} 条")

                # 实时回写入库
                if callable(self.on_item_saved):
                    try:
                        self.on_item_saved(page_items)
                    except Exception as e:
                        logger.error(f"[{self.config.name}] 增量写入数据库失败: {e}")

                self.products.extend(page_items)
                self.stats["products_found"] += len(page_items)
                self.stats["pages_crawled"] += 1
                await self._report_progress()

                logger.info(f"[{self.config.name}] 第 {page}/{max_pages} 页完成: +{len(page_items)} 商品 (累计: {self.stats['products_found']})")

                # 判断下一页
                if next_url and next_url not in visited_urls:
                    current_url = next_url
                else:
                    if page < max_pages:
                        current_url = f"{self.list_url}?page={page + 1}"
                    else:
                        logger.info(f"[{self.config.name}] 已到达最后一页 ({page})")
                        break

                page += 1
                delay = max(0.5, float(self.config.request_delay or 1.0))
                await asyncio.sleep(delay)

        self.stats["end_time"] = datetime.now()
        duration = (self.stats["end_time"] - self.stats["start_time"]).seconds
        logger.info(
            f"[{self.config.name}] 爬取完成 | 商品数:{len(self.products)} "
            f"页数:{self.stats['pages_crawled']} 耗时:{duration}s 错误数:{self.stats['errors']}"
        )
        return self.products
