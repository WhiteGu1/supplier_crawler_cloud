"""
supplier_crawler/crawler/wc_store_spider.py
WooCommerce Store REST API 专用爬虫模块
适用于支持 /wp-json/wc/store/v1/products 的 WooCommerce 网站（如 Bella Central）
高效、直接获取结构化数据，自动并发下载图片并实时增量写库。
"""
import asyncio
import aiohttp
import logging
import random
import re
from datetime import datetime
from typing import Optional

from .spider import ProductItem, SupplierConfig, ImageDownloader, USER_AGENTS

logger = logging.getLogger(__name__)


class WooCommerceStoreSpider:
    """WooCommerce Store REST API 爬虫"""

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

        # API 地址配置
        api_url = (self.config.selectors or {}).get("api_url")
        if not api_url:
            base = self.config.base_url.rstrip("/")
            api_url = f"{base}/wp-json/wc/store/v1/products"
        self.api_url = api_url

    def _make_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
        }

    async def _report_progress(self):
        """实时回写进度到数据库"""
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

    def _parse_product(self, p: dict) -> Optional[ProductItem]:
        try:
            name = (p.get("name") or "").strip()
            if not name:
                return None

            prices = p.get("prices") or {}
            minor = prices.get("currency_minor_unit", 2)
            raw_price = prices.get("price") or prices.get("regular_price") or 0
            try:
                price = float(raw_price) / (10 ** minor)
            except Exception:
                price = 0.0

            # 若单价为0但存在价格区间，取 min_amount 作为基准单价
            if price <= 0:
                min_amt = (prices.get("price_range") or {}).get("min_amount")
                if min_amt:
                    try:
                        price = float(min_amt) / (10 ** minor)
                    except Exception:
                        price = 0.0

            currency = prices.get("currency_code") or "ARS"
            sku = (p.get("sku") or "").strip()

            # 分类路径，用 ' > ' 连接各级分类
            categories = [c["name"].strip() for c in p.get("categories", []) if c.get("name")]
            category = " > ".join(categories)[:100]

            # 品牌
            brand = ""
            if p.get("brands"):
                brand = (p["brands"][0].get("name") or "").strip()[:100]

            # 简介/描述（去除 HTML 标签）
            desc_raw = p.get("short_description") or p.get("description") or ""
            description = re.sub(r'<[^>]+>', ' ', desc_raw).strip()[:500]

            # 图片链接（优先取原图）
            images = p.get("images") or []
            image_url = images[0].get("src", "").strip() if images else ""

            # 详情链接
            product_url = (p.get("permalink") or "").strip()

            add_to_cart = p.get("add_to_cart") or {}
            min_qty = int(add_to_cart.get("minimum") or 1)
            package_qty = int(add_to_cart.get("multiple_of") or 1)
            raw_id = str(p.get("id") or "")
            if not sku:
                sku = raw_id

            return ProductItem(
                name=name,
                price=price,
                currency=currency,
                sku=sku,
                category=category,
                description=description,
                image_url=image_url,
                image_local_path="",
                product_url=product_url,
                supplier_id=self.config.id,
                stock=None,
                unit="C/U",
                brand=brand,
                min_qty=min_qty,
                package_qty=package_qty,
                raw_data=p,
                crawled_at=datetime.now(),
            )
        except Exception as e:
            logger.error(f"[{self.config.name}] 解析商品异常: {e}")
            self.stats["errors"] += 1
            return None

    async def run(self) -> list[ProductItem]:
        self.stats["start_time"] = datetime.now()
        logger.info(f"开始爬取 WooCommerce Store: {self.config.name} -> {self.api_url}")

        connector = aiohttp.TCPConnector(limit=15, ssl=False)
        timeout = aiohttp.ClientTimeout(total=45)

        async with aiohttp.ClientSession(
            headers=self._make_headers(),
            connector=connector,
            timeout=timeout,
        ) as session:
            page = 1
            total_pages = 1
            per_page = 100

            while page <= total_pages:
                if self._cancelled:
                    logger.info(f"[{self.config.name}] 爬取已取消")
                    break

                page_url = f"{self.api_url}?per_page={per_page}&page={page}"
                logger.info(f"[{self.config.name}] 正在请求第 {page}/{total_pages} 页: {page_url}")

                data = None
                for attempt in range(3):
                    try:
                        async with session.get(page_url) as resp:
                            if resp.status == 200:
                                if page == 1:
                                    try:
                                        wp_pages = int(resp.headers.get("x-wp-totalpages", 1))
                                        total_products = int(resp.headers.get("x-wp-total", 0))
                                        total_pages = min(wp_pages, self.config.max_pages or 500)
                                        logger.info(f"[{self.config.name}] 共计发现 {total_products} 件商品，共 {wp_pages} 页（计划爬取 {total_pages} 页）")
                                    except Exception:
                                        total_pages = self.config.max_pages or 500
                                data = await resp.json()
                                break
                            elif resp.status in (400, 404):
                                logger.info(f"[{self.config.name}] 到达末尾页（HTTP {resp.status}）")
                                data = []
                                total_pages = page - 1
                                break
                            else:
                                logger.warning(f"[{self.config.name}] 请求第 {page} 页返回 HTTP {resp.status}，重试中({attempt+1}/3)...")
                                await asyncio.sleep(2)
                    except asyncio.CancelledError:
                        self._cancelled = True
                        break
                    except Exception as e:
                        logger.warning(f"[{self.config.name}] 请求第 {page} 页失败: {e}，重试中({attempt+1}/3)...")
                        await asyncio.sleep(2)

                if self._cancelled:
                    break

                if data is None:
                    logger.error(f"[{self.config.name}] 第 {page} 页重试3次均失败，跳过")
                    self.stats["errors"] += 1
                    page += 1
                    continue

                if not data:
                    logger.info(f"[{self.config.name}] 第 {page} 页无数据，结束爬取")
                    break

                # 解析本页商品
                page_items: list[ProductItem] = []
                for p_raw in data:
                    item = self._parse_product(p_raw)
                    if item:
                        page_items.append(item)

                # 并发下载图片
                if page_items:
                    sem = asyncio.Semaphore(12)
                    async def _dl(it):
                        if not self._cancelled and it.image_url:
                            async with sem:
                                it.image_local_path = await self.downloader.download(
                                    session, it.image_url, self.config.name
                                )
                    await asyncio.gather(*[_dl(it) for it in page_items])

                    # 增量回调写库
                    if callable(self.on_item_saved):
                        try:
                            self.on_item_saved(page_items)
                        except Exception as e:
                            logger.error(f"[{self.config.name}] 增量写库失败: {e}")

                    self.products.extend(page_items)
                    self.stats["products_found"] += len(page_items)

                self.stats["pages_crawled"] += 1
                await self._report_progress()

                page += 1
                delay = max(0.2, self.config.request_delay)
                await asyncio.sleep(delay)

        self.stats["end_time"] = datetime.now()
        duration = (self.stats["end_time"] - self.stats["start_time"]).seconds
        logger.info(
            f"[{self.config.name}] 完成 | 商品:{len(self.products)} 页面:{self.stats['pages_crawled']} "
            f"耗时:{duration}s 错误:{self.stats['errors']}"
        )
        return self.products
