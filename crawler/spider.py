"""
supplier_crawler/crawler/spider.py
通用供应商网站爬虫核心模块
"""
import asyncio
import aiohttp
import hashlib
import logging
import os
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 随机UA池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]


@dataclass
class ProductItem:
    name: str
    price: float
    currency: str = "ARS"
    sku: str = ""
    category: str = ""
    description: str = ""
    image_url: str = ""
    image_local_path: str = ""
    product_url: str = ""
    supplier_id: int = 0
    stock: Optional[int] = None
    unit: str = ""
    brand: str = ""
    min_qty: int = 1
    package_qty: int = 1
    raw_data: dict = field(default_factory=dict)
    crawled_at: datetime = field(default_factory=datetime.now)


@dataclass
class SupplierConfig:
    id: int
    name: str
    base_url: str
    product_list_url: str
    selectors: dict = field(default_factory=dict)
    use_js_render: bool = False
    use_chrome_cookies: bool = False
    request_delay: float = 1.5
    max_pages: int = 500
    timeout: int = 30


def get_chrome_cookies(domain: str) -> list[dict]:
    """从本机Chrome读取指定域名的Cookie，返回Playwright格式列表。"""
    try:
        import browser_cookie3
        from urllib.parse import urlparse
        parsed = urlparse(domain if "://" in domain else "https://" + domain)
        host = parsed.netloc or parsed.path
        jar = browser_cookie3.chrome(domain_name=host)
        cookies = []
        for c in jar:
            cookies.append({
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "secure": bool(c.secure),
                "httpOnly": False,
                "sameSite": "Lax",
            })
        logger.info(f"从Chrome读取到 {len(cookies)} 个Cookie（域名: {host}）")
        return cookies
    except ImportError:
        logger.error("未安装 browser_cookie3，请运行: pip install browser_cookie3")
        return []
    except Exception as e:
        logger.error(f"读取Chrome Cookie失败: {e}")
        return []


def parse_manual_cookies(cookie_str: str, domain: str) -> list[dict]:
    """
    解析手动填写的Cookie字符串，格式：name=value; name2=value2
    返回Playwright格式列表。
    """
    from urllib.parse import urlparse
    parsed = urlparse(domain if "://" in domain else "https://" + domain)
    host = parsed.netloc or parsed.path
    cookies = []
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            name, _, value = part.partition("=")
            cookies.append({
                "name": name.strip(),
                "value": value.strip(),
                "domain": host,
                "path": "/",
                "secure": False,
                "httpOnly": False,
                "sameSite": "Lax",
            })
    logger.info(f"手动Cookie解析到 {len(cookies)} 个（域名: {host}）")
    return cookies


def clean_price(text: str) -> float:
    """从字符串中提取价格数字"""
    if not text:
        return 0.0
    # 移除货币符号、空格（含&nbsp;）和价格后的单位说明如 "x Un."
    text = re.sub(r'[¥$€£\s\u00a0]', '', text)
    text = re.sub(r'[xX][A-Za-z\.]+.*$', '', text).strip()
    # 处理阿根廷比索格式 1.234,56 → 1234.56
    if re.search(r'\d+\.\d{3},\d{2}', text):
        text = text.replace('.', '').replace(',', '.')
    # 处理阿根廷格式 1.234 或 35.000（千位用点，无小数）
    elif re.search(r'^\d+\.\d{3}$', text.strip()):
        text = text.replace('.', '')
    elif ',' in text and '.' in text:
        # 1,234.56 格式
        text = text.replace(',', '')
    elif ',' in text:
        text = text.replace(',', '.')
    nums = re.findall(r'\d+\.?\d*', text)
    return float(nums[0]) if nums else 0.0


class ImageDownloader:
    def __init__(self, save_dir: str = ""):
        if not save_dir:
            # 默认保存到 spider.py 所在项目根目录的 images/
            save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    # Content-Type -> 扩展名映射
    _CT_EXT = {
        "image/jpeg": ".jpg", "image/jpg": ".jpg",
        "image/png": ".png", "image/webp": ".webp",
        "image/gif": ".gif", "image/avif": ".avif",
    }
    # 文件头魔数 -> 扩展名
    _MAGIC = [
        (b"\xff\xd8\xff", ".jpg"),
        (b"\x89PNG\r\n\x1a\n", ".png"),
        (b"RIFF", ".webp"),   # RIFF????WEBP
        (b"GIF8", ".gif"),
    ]

    def _detect_ext(self, data: bytes, content_type: str) -> str:
        """根据Content-Type和文件头魔数判断真实图片格式"""
        ct = (content_type or "").split(";")[0].strip().lower()
        if ct in self._CT_EXT:
            return self._CT_EXT[ct]
        for magic, ext in self._MAGIC:
            if data[:len(magic)] == magic:
                return ext
        return ".jpg"  # 最终兜底

    async def download(self, session: aiohttp.ClientSession, url: str, supplier_name: str) -> str:
        if not url or not url.startswith("http"):
            return ""
        try:
            # 以 spider.py 所在目录为基准，保存到项目根目录的 images/
            base = self.save_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
            subdir = os.path.join(base, supplier_name)
            os.makedirs(subdir, exist_ok=True)
            # 先用URL hash作为临时文件名（不带扩展名）
            name_hash = hashlib.md5(url.encode()).hexdigest()

            # 检查是否已下载过（任意扩展名），返回相对路径
            for ext in (".jpg", ".png", ".webp", ".gif", ".avif"):
                fp = os.path.join(subdir, name_hash + ext)
                if os.path.exists(fp):
                    return f"images/{supplier_name}/{name_hash}{ext}"

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15),
                                   allow_redirects=True) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    if len(data) < 100:
                        logger.debug(f"图片内容过小({len(data)}字节)，跳过: {url}")
                        return ""
                    ct = resp.headers.get("Content-Type", "")
                    ext = self._detect_ext(data, ct)
                    filepath = os.path.join(subdir, name_hash + ext)
                    with open(filepath, "wb") as f:
                        f.write(data)
                    return f"images/{supplier_name}/{name_hash}{ext}"
                else:
                    logger.debug(f"图片下载失败 HTTP {resp.status}: {url}")
        except Exception as e:
            logger.debug(f"图片下载失败 {url}: {e}")
        return ""


class SupplierSpider:
    """供应商爬虫主类"""

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

    def _make_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    def _get_selector(self, key: str) -> str:
        return self.config.selectors.get(key, "")

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

    async def crawl_static(self) -> list[ProductItem]:
        connector = aiohttp.TCPConnector(limit=3, ssl=False)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        async with aiohttp.ClientSession(
            headers=self._make_headers(),
            connector=connector,
            timeout=timeout,
        ) as session:
            page_url = self.config.product_list_url
            visited = set()

            for page_num in range(1, self.config.max_pages + 1):
                if self._cancelled or page_url in visited:
                    break
                visited.add(page_url)
                logger.info(f"[{self.config.name}] 第 {page_num} 页: {page_url}")

                try:
                    async with session.get(page_url) as resp:
                        resp.raise_for_status()
                        html = await resp.text(errors="replace")
                    soup = BeautifulSoup(html, "lxml")

                    # ── 策略1: 内嵌JSON（Tiendanube等平台，优先）──────────
                    json_items = self._extract_from_page_json(html, page_url)
                    if json_items:
                        logger.info(f"[{self.config.name}] 第{page_num}页 JSON提取 {len(json_items)} 条，开始下载图片...")
                        sem = asyncio.Semaphore(8)
                        async def _dl_s(it, _sem=sem, _session=session):
                            if not self._cancelled and it.image_url:
                                async with _sem:
                                    it.image_local_path = await self.downloader.download(
                                        _session, it.image_url, self.config.name
                                    )
                        await asyncio.gather(*[_dl_s(it) for it in json_items])
                        for item in json_items:
                            if self._cancelled:
                                break
                            self.products.append(item)
                            self.stats["products_found"] += 1
                        logger.info(f"[{self.config.name}] 第{page_num}页图片下载完成")

                    else:
                        # ── 策略1.5: Jumpseller平台提取 ──────────────────
                        jump_items = self._extract_from_jumpseller(soup)
                        if jump_items:
                            logger.info(f"[{self.config.name}] 第{page_num}页 Jumpseller提取 {len(jump_items)} 条，开始下载图片...")
                            sem = asyncio.Semaphore(8)
                            async def _dl_j(it, _sem=sem, _session=session):
                                if not self._cancelled and it.image_url:
                                    async with _sem:
                                        it.image_local_path = await self.downloader.download(
                                            _session, it.image_url, self.config.name
                                        )
                            await asyncio.gather(*[_dl_j(it) for it in jump_items])
                            for item in jump_items:
                                if self._cancelled:
                                    break
                                self.products.append(item)
                                self.stats["products_found"] += 1
                            logger.info(f"[{self.config.name}] 第{page_num}页图片下载完成")

                        else:
                            # ── 策略2/3: CSS选择器提取 ────────────────────────
                            link_sel = self._get_selector("product_links")
                            links_els = soup.select(link_sel) if link_sel else []

                            if not links_els:
                                # 尝试卡片容器直提模式
                                card_items = self._extract_from_list_page(soup)
                                if card_items:
                                    sem = asyncio.Semaphore(8)
                                    async def _dl_c(it, _sem=sem, _session=session):
                                        if not self._cancelled and it.image_url:
                                            async with _sem:
                                                it.image_local_path = await self.downloader.download(
                                                    _session, it.image_url, self.config.name
                                                )
                                    await asyncio.gather(*[_dl_c(it) for it in card_items])
                                    for item in card_items:
                                        if self._cancelled:
                                            break
                                        self.products.append(item)
                                        self.stats["products_found"] += 1
                                    logger.info(f"[{self.config.name}] 第{page_num}页卡片直提 {len(card_items)} 条")
                                else:
                                    snippet = soup.get_text()[:400].strip()
                                    logger.error(f"[{self.config.name}] 第{page_num}页未找到商品链接")
                                    logger.error(f"  选择器: {link_sel!r}")
                                    logger.error(f"  页面片段: {snippet!r}")
                                    break

                            product_urls = list(dict.fromkeys(
                                urljoin(self.config.base_url, el.get("href") or el.get("data-href", ""))
                                for el in links_els if (el.get("href") or el.get("data-href"))
                            ))
                            logger.info(f"[{self.config.name}] 第{page_num}页发现 {len(product_urls)} 个商品链接")

                            for url in product_urls:
                                if self._cancelled:
                                    break
                                if self._get_selector("product_name") == link_sel:
                                    product = await self._parse_product_from_list(session, soup, url, links_els)
                                else:
                                    product = await self._parse_product_page(session, url)
                                if product:
                                    self.products.append(product)
                                    self.stats["products_found"] += 1

                    self.stats["pages_crawled"] += 1
                    await self._report_progress()

                    # 翻页
                    pag_sel = self._get_selector("pagination")
                    next_btn = soup.select_one(pag_sel) if pag_sel else None
                    if not next_btn:
                        logger.info(f"[{self.config.name}] 已到最后一页")
                        break
                    next_href = next_btn.get("href")
                    if not next_href:
                        break
                    next_url = urljoin(self.config.base_url, next_href)
                    if next_url == page_url or next_url in visited:
                        break
                    page_url = next_url

                    # 随机延迟（防反爬）
                    delay = self.config.request_delay + random.uniform(0, 1.0)
                    await asyncio.sleep(delay)

                except asyncio.CancelledError:
                    self._cancelled = True
                    break
                except Exception as e:
                    logger.error(f"[{self.config.name}] 页面爬取失败: {e}")
                    self.stats["errors"] += 1
                    await asyncio.sleep(2)

        return self.products

    async def _parse_product_page(self, session: aiohttp.ClientSession, url: str) -> Optional[ProductItem]:
        try:
            async with session.get(url) as resp:
                resp.raise_for_status()
                html = await resp.text(errors="replace")
            soup = BeautifulSoup(html, "lxml")
            return self._extract_product(soup, url)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"商品页解析失败 {url}: {type(e).__name__}: {e}")
            self.stats["errors"] += 1
            return None

    async def _parse_product_from_list(self, session, list_soup, url, all_link_els) -> Optional[ProductItem]:
        """先尝试从列表页的商品容器提取，失败则进入详情页"""
        link_el = next((el for el in all_link_els if urljoin(self.config.base_url, el.get("href", "")) == url), None)
        if link_el:
            name_text = link_el.get_text(strip=True)
            if name_text:
                price_sel = self._get_selector("price")
                img_sel = self._get_selector("image")

                # 向上逐层找含价格的最近祖先容器（最多8层）
                caption_container = None
                node = link_el
                for _ in range(8):
                    node = node.parent
                    if node is None or node.name in ("body", "html", "[document]"):
                        break
                    if price_sel and node.select_one(price_sel):
                        caption_container = node
                        break

                # 再向上一层找更宽的卡片容器（含图片）
                outer_container = caption_container.parent if caption_container is not None else None

                # 提取价格：在 caption_container 内找，取最内层嵌套的同名元素
                price_el = caption_container.select_one(price_sel) if (caption_container and price_sel) else None
                if price_el:
                    # 处理嵌套 span.price 的情况（如 sfpanda），取最深层
                    inner = price_el.select_one(price_sel)
                    if inner:
                        price_el = inner
                price_text = price_el.get_text(strip=True) if price_el else ""
                price = clean_price(price_text)

                # 提取图片：优先在 outer_container，其次 caption_container
                img_el = None
                for search_root in [outer_container, caption_container]:
                    if search_root is None:
                        continue
                    img_el = search_root.select_one(img_sel) if img_sel else None
                    if not img_el:
                        img_el = search_root.select_one("img")
                    if img_el:
                        break
                img_url = ""
                if img_el:
                    img_url = img_el.get("src") or img_el.get("data-src") or img_el.get("data-lazy-src") or ""
                    if img_url:
                        img_url = urljoin(self.config.base_url, img_url)

                if name_text and price > 0:
                    logger.info(f"[{self.config.name}] 列表页提取: {name_text[:40]} | 价格: {price}")
                    return ProductItem(
                        name=name_text, price=price, product_url=url,
                        image_url=img_url, supplier_id=self.config.id,
                    )
                else:
                    logger.warning(f"[{self.config.name}] 列表页价格提取失败(={price_text!r})，回退详情页: {url[:60]}")
        # 回退到详情页
        return await self._parse_product_page(session, url)

    def _extract_product(self, soup: BeautifulSoup, url: str) -> Optional[ProductItem]:
        s = self.config.selectors

        def get_text(sel):
            if not sel:
                return ""
            el = soup.select_one(sel)
            return el.get_text(strip=True) if el else ""

        name = get_text(s.get("product_name"))
        if not name:
            for fallback in ["h1", "h1.product_title", ".product-title", ".entry-title", "[itemprop=name]"]:
                name = get_text(fallback)
                if name:
                    break
        if not name:
            logger.error(f"[{self.config.name}] 商品名未找到，选择器={s.get('product_name')!r}，URL={url}")
            # 打印页面前500字符帮助诊断
            logger.error(f"  页面片段: {soup.get_text()[:300].strip()!r}")
            return None

        price_text = get_text(s.get("price"))
        if not price_text:
            for fallback in [".price", ".woocommerce-Price-amount", "span.price", "[itemprop=price]"]:
                price_text = get_text(fallback)
                if price_text:
                    break
        price = clean_price(price_text)
        if price <= 0:
            logger.error(f"[{self.config.name}] 价格未找到/为0，选择器={s.get('price')!r}，原始文本={price_text!r}，URL={url}")
            return None

        img_el = soup.select_one(s.get("image", "")) if s.get("image") else None
        if not img_el:
            img_el = soup.select_one(".product img, .woocommerce-product-gallery img, img.wp-post-image")
        image_url = ""
        if img_el:
            image_url = (img_el.get("src") or img_el.get("data-src") or img_el.get("data-lazy-src") or "")
            image_url = urljoin(self.config.base_url, image_url)

        item = ProductItem(
            name=name[:300],
            price=price,
            product_url=url,
            image_url=image_url,
            supplier_id=self.config.id,
            sku=get_text(s.get("sku"))[:100],
            category=get_text(s.get("category"))[:100],
            description=get_text(s.get("description"))[:500],
        )
        logger.info(f"[{self.config.name}] 解析商品: {name[:40]} | 价格: {price} | {url[:60]}")
        return item

    def _should_prefer_original_price(self) -> bool:
        """判断是否优先抓取原价（避免将单品特价再次叠加整店折扣）。"""
        selectors = self.config.selectors or {}
        if "prefer_original_price" in selectors:
            return bool(selectors.get("prefer_original_price"))
        return (
            "benabi" in (self.config.name or "").lower()
            or "smarty" in (self.config.base_url or "").lower()
            or "smarty" in (self.config.product_list_url or "").lower()
        )

    def _extract_price_text_from_el(self, price_el) -> str:
        """从列表卡片价格容器按配置提取价格文本。"""
        if not price_el:
            return ""
        if self._should_prefer_original_price():
            for sel in (".origDiscountPrice", ".origPrice", ".product-price-compare", ".discountPrice, .product-price-discounted"):
                el = price_el.select_one(sel)
                if el:
                    return el.get_text(strip=True)
            return price_el.get_text(strip=True)

        discount_el = price_el.select_one(".discountPrice")
        if discount_el:
            return discount_el.get_text(strip=True)
        orig_el = price_el.select_one(".origPrice, .origDiscountPrice")
        if orig_el:
            return orig_el.get_text(strip=True)
        return price_el.get_text(strip=True)

    def _extract_from_list_page(self, soup: BeautifulSoup) -> list[ProductItem]:
        """
        从列表页卡片容器直接提取商品（无需进详情页）。
        需要在 selectors 中配置 card_container 选择器。
        """
        card_sel  = self._get_selector("card_container")
        name_sel  = self._get_selector("product_name")
        price_sel = self._get_selector("price")
        img_sel   = self._get_selector("image")
        sku_sel   = self._get_selector("sku")
        cat_sel   = self._get_selector("category")

        if not card_sel:
            return []

        cards = soup.select(card_sel)
        items = []
        for card in cards:
            try:
                name_el  = card.select_one(name_sel)  if name_sel  else None
                price_el = card.select_one(price_sel) if price_sel else None
                img_el   = card.select_one(img_sel)   if img_sel   else None
                sku_el   = card.select_one(sku_sel)   if sku_sel   else None
                cat_el   = card.select_one(cat_sel)   if cat_sel   else None

                name = name_el.get_text(strip=True) if name_el else ""
                if not name:
                    continue

                # 对于 benabi / Smarty 等含有店铺折扣的供应商，prefer_original_price 控制是否优先爬原价
                price_text = self._extract_price_text_from_el(price_el)
                price = clean_price(price_text)
                if price <= 0:
                    continue

                img_url = ""
                if img_el:
                    raw = img_el.get("src") or img_el.get("data-src") or ""
                    img_url = urljoin(self.config.base_url, raw) if raw else ""

                sku = ""
                if sku_el:
                    sku_text = sku_el.get_text(strip=True)
                    sku = re.sub(r'(?i)cod[:\s]*', '', sku_text).strip()
                if not sku:
                    # 尝试 Diego 的 span.fcod (如 Cod: 689)
                    fcod_el = card.select_one("span.fcod")
                    if fcod_el:
                        sku = re.sub(r'(?i)cod[:\s]*', '', fcod_el.get_text(strip=True)).strip()
                if not sku:
                    ref_el = card.select_one(".reference, span.reference")
                    if ref_el:
                        sku = ref_el.get_text(strip=True).strip()

                # 提取卡片内嵌商品 ID（如 SmartyCart 的 id="item_4036431" 或 input.id）
                card_id_attr = card.get("id") or ""
                item_prod_id = ""
                if card_id_attr.startswith("item_"):
                    item_prod_id = card_id_attr.replace("item_", "").strip()
                if not item_prod_id:
                    inp_id = card.select_one("input.id, input[data-product-id]")
                    if inp_id:
                        item_prod_id = inp_id.get("value") or inp_id.get("data-product-id") or ""

                if not sku and item_prod_id:
                    sku = item_prod_id

                # 补全 SmartyCart 的 product_url，格式：{base_url}/token/{token}/{item_prod_id}
                product_url = ""
                token_match = re.search(r'/token/([a-f0-9]+)', self.config.product_list_url or "")
                if token_match and item_prod_id:
                    clean_base = self.config.base_url.rstrip("/")
                    product_url = f"{clean_base}/token/{token_match.group(1)}/{item_prod_id}"
                elif "distrinimay" in (self.config.base_url or "").lower() and sku:
                    product_url = f"{self.config.base_url.rstrip('/')}/cat/#prod-{sku}"

                category = cat_el.get_text(strip=True) if cat_el else ""

                # 提取起订量(min_qty)与箱规/步进倍数(package_qty)
                min_qty = 1
                package_qty = 1

                # 1. 检查输入框属性（SmartyCart 的 min/step，或 Diego 的 fcant）
                qty_input = card.select_one('input.quantity, input.fcant, input[name="qty"], input[name="quantity"]')
                if qty_input:
                    try:
                        inp_min = int(qty_input.get('min') or qty_input.get('data-min') or 0)
                        if inp_min > 0:
                            min_qty = inp_min
                    except (ValueError, TypeError):
                        pass
                    try:
                        inp_step = int(qty_input.get('step') or 0)
                        if inp_step > 0:
                            package_qty = inp_step
                    except (ValueError, TypeError):
                        pass

                # 2. 检查 Diego (Distrinimay) 的 fraccion 属性（span.ffrac 或 [frac]）
                frac_el = card.select_one('span.ffrac, [frac]')
                if frac_el:
                    try:
                        frac_val = int(frac_el.get('frac') or 0)
                        if frac_val > 0:
                            package_qty = frac_val
                            min_qty = frac_val
                    except (ValueError, TypeError):
                        pass

                # 3. 文本正则辅助提取 (Bulto: X, Paquete: Y, Min: Z)
                card_text = card.get_text(' ', strip=True)
                m_bulto = re.search(r'Bulto[:\s]*(\d+)', card_text, re.I)
                m_paq = re.search(r'Paquete[:\s]*(\d+)', card_text, re.I)
                m_min = re.search(r'(?:M[ií]nimo|Min)[\.:\s]*(\d+)', card_text, re.I)

                if package_qty <= 1:
                    if m_paq:
                        package_qty = int(m_paq.group(1))
                    elif m_bulto:
                        package_qty = int(m_bulto.group(1))

                if min_qty <= 1 and m_min:
                    min_qty = int(m_min.group(1))

                item = ProductItem(
                    name=name[:300],
                    price=price,
                    sku=sku[:100],
                    category=category[:100],
                    image_url=img_url,
                    product_url=product_url,
                    supplier_id=self.config.id,
                    min_qty=min_qty,
                    package_qty=package_qty,
                )
                items.append(item)
                logger.info(f"[{self.config.name}] 列表提取: {name[:40]} | {price} | min={min_qty} pkg={package_qty}")
            except Exception as e:
                logger.debug(f"卡片解析失败: {e}")
        return items

    def _extract_from_page_json(self, html: str, page_url: str) -> list[ProductItem]:
        """
        优先策略：从页面内嵌的 window.data.products JSON 提取商品数据。
        适用于 Tiendanube / ekShops 等平台，无需进入详情页。
        返回空列表表示此页面不含内嵌 JSON，应回退到其他策略。
        """
        import json as _json

        # 先尝试 window.data.products（sfpanda等）
        m = re.search(
            r'window\.data\.products\s*=\s*Object\.assign\(window\.data\.products\s*,\s*(\{.*?\})\s*\)\s*;',
            html, re.DOTALL
        )
        if not m:
            # 诊断：看看页面里有没有window.data相关内容
            m2 = re.search(r'window\.data[^\n]{0,100}', html)
            if m2:
                logger.info(f"[{self.config.name}] window.data片段: {m2.group(0)[:150]!r}")
            else:
                logger.debug(f"[{self.config.name}] 页面无window.data")

            # 尝试 data-variants（Tiendanube/linkedstore平台）
            soup = BeautifulSoup(html, "lxml")
            items = self._extract_from_data_variants(soup)
            if items:
                logger.info(f"[{self.config.name}] data-variants提取 {len(items)} 条")
            return items

        try:
            data = _json.loads(m.group(1))
        except Exception as e:
            logger.warning(f"[{self.config.name}] JSON解析失败: {e}")
            return []

        items = []
        for p in data.values():
            try:
                name = (p.get("name") or "").strip()
                if not name:
                    continue

                price = float(p.get("sellingPrice") or p.get("price") or 0)
                if price <= 0:
                    continue

                currency = p.get("currencyCode") or "ARS"
                sku = (p.get("sku") or (p.get("product") or {}).get("sku") or "").strip()
                # categoriesBreadcrumb = ["MASCOTAS > CAMAS"]，取第一个
                _cat_breadcrumb = p.get("categoriesBreadcrumb") or []
                _cat_name_path = p.get("categoryNamePath") or []
                category = (_cat_breadcrumb[0] if _cat_breadcrumb else
                            " > ".join(_cat_name_path) if _cat_name_path else
                            (p.get("category") or "")).strip()
                description = (p.get("descriptionPlainText") or "").strip()[:500]

                urls = p.get("urls") or {}
                detail_path = urls.get("detail") or ""
                product_url = urljoin(self.config.base_url, detail_path) if detail_path else ""

                img_paths = urls.get("images") or []
                image_url = urljoin(self.config.base_url, img_paths[0]) if img_paths else ""

                item = ProductItem(
                    name=name[:300],
                    price=price,
                    currency=currency,
                    sku=sku[:100],
                    category=category[:100],
                    description=description,
                    image_url=image_url,
                    product_url=product_url,
                    supplier_id=self.config.id,
                )
                items.append(item)
                logger.info(f"[{self.config.name}] JSON提取: {name[:40]} | {currency} {price}")
            except Exception as e:
                logger.warning(f"[{self.config.name}] 单条商品JSON解析失败: {e}")
                self.stats["errors"] += 1

        return items

    @staticmethod
    def _parse_variant_price(v: dict) -> float:
        """从 Tiendanube variant dict 中解析价格，支持多种字段格式。"""
        # 优先 price_number（元）
        pn = v.get('price_number')
        if pn and float(pn) > 0:
            return float(pn)
        # 回退 price_number_raw（分）
        pr = v.get('price_number_raw')
        if pr and float(pr) > 0:
            return float(pr) / 100.0 if float(pr) > 100 else float(pr)
        # 回退 price_short（如 "$595"、"$1.234"）
        ps = v.get('price_short') or v.get('price_long') or ''
        if ps:
            cleaned = re.sub(r'[^\d,.]', '', ps.replace('.', '').replace(',', '.'))
            try:
                val = float(cleaned)
                if val > 0:
                    return val
            except ValueError:
                pass
        return 0.0

    def _extract_from_data_variants(self, soup: BeautifulSoup) -> list[ProductItem]:
        """
        从 data-variants 属性提取商品（Tiendanube/linkedstore平台）。
        每个 div.js-item-product 包含 data-variants JSON。
        """
        import json as _json
        items = []
        # 只取有data-variants属性的卡片，避免重复div
        cards = soup.select('div[data-variants]')
        if not cards:
            cards = soup.select('div.js-item-product')
        logger.info(f"[{self.config.name}] [data-variants] 卡片数: {len(cards)}")
        skip_reasons = {"empty_raw": 0, "json_fail": 0, "empty_variants": 0, "no_name": 0, "no_price": 0, "ok": 0}
        for idx, card in enumerate(cards):
            try:
                variants_raw = card.get('data-variants') or ''
                if not variants_raw:
                    skip_reasons["empty_raw"] += 1
                    continue
                variants = _json.loads(variants_raw)
                if not variants:
                    skip_reasons["empty_variants"] += 1
                    continue
                v = variants[0]  # 取第一个变体

                # 名字：优先从HTML元素取，回退到JSON
                name_el = card.select_one('.item-name, h2.item-name, h3.item-name, .js-item-name')
                name = name_el.get_text(strip=True) if name_el else (v.get('name') or '').strip()
                if not name:
                    skip_reasons["no_name"] += 1
                    if idx < 2:
                        logger.warning(f"[{self.config.name}] 卡片{idx}无name: variant={list(v.keys())[:8]}, name_el={name_el is not None}")
                    continue

                # 价格：支持多种字段格式
                price = self._parse_variant_price(v)
                is_contact = v.get('contact', False)
                if price <= 0 and not is_contact:
                    skip_reasons["no_price"] += 1
                    if idx < 2:
                        logger.warning(f"[{self.config.name}] 卡片{idx}价格<=0: price_number={v.get('price_number')}, price_short={v.get('price_short')!r}")
                    continue
                if price <= 0 and is_contact:
                    # contact模式：价格可能在详情页，先返回price=0，后续补价
                    skip_reasons["ok"] += 1
                    if idx < 2:
                        logger.info(f"[{self.config.name}] 卡片{idx}contact模式价格null，保留待详情页补价")

                # SKU
                sku = str(v.get('sku') or '').strip()

                # 图片
                img_url = v.get('image_url') or ''
                if img_url:
                    img_url = 'https:' + img_url if img_url.startswith('//') else img_url
                    img_url = urljoin(self.config.base_url, img_url)

                # 商品链接
                link_el = card.select_one('a[href]')
                product_url = urljoin(self.config.base_url, link_el['href']) if link_el else ''

                # 分类
                cat_el = card.select_one('.item-category, .item-categories')
                category = cat_el.get_text(strip=True) if cat_el else ''

                item = ProductItem(
                    name=name[:300],
                    price=price,
                    sku=sku[:100],
                    category=category[:100],
                    image_url=img_url,
                    product_url=product_url,
                    supplier_id=self.config.id,
                )
                items.append(item)
                skip_reasons["ok"] += 1
                logger.info(f"[{self.config.name}] variants提取: {name[:40]} | {price}")
            except Exception as e:
                logger.warning(f"[{self.config.name}] data-variants解析失败(card#{idx}): {e}")
                if idx < 2:
                    import traceback
                    logger.warning(traceback.format_exc())
        if not items:
            logger.warning(f"[{self.config.name}] [data-variants] 全部跳过: {skip_reasons}")
        return items

    async def _extract_from_data_variants_js(self, page) -> list[ProductItem]:
        """
        通过 JavaScript 直接从活 DOM 读取 data-variants 属性。
        返回原始 variant JSON 数据，由 Python 侧用 _parse_variant_price 解析价格。
        """
        import json as _json
        try:
            raw_data = await page.evaluate("""() => {
                const cards = document.querySelectorAll('div[data-variants]');
                const results = [];
                for (const card of cards) {
                    const raw = card.getAttribute('data-variants');
                    if (!raw) continue;
                    try {
                        const variants = JSON.parse(raw);
                        if (!variants || variants.length === 0) continue;
                        const v = variants[0];
                        const nameEl = card.querySelector('.item-name, .js-item-name, h2.item-name, h3.item-name');
                        const name = nameEl ? nameEl.textContent.trim() : (v.name || '');
                        if (!name) continue;
                        const linkEl = card.querySelector('a[href]');
                        const href = linkEl ? linkEl.getAttribute('href') : '';
                        results.push({
                            name,
                            price_number: v.price_number || null,
                            price_number_raw: v.price_number_raw || null,
                            price_short: v.price_short || null,
                            price_long: v.price_long || null,
                            sku: v.sku || '',
                            image_url: v.image_url || '',
                            href,
                            product_id: v.product_id || ''
                        });
                    } catch(e) { /* skip card */ }
                }
                return results;
            }""")
        except Exception as e:
            logger.warning(f"[{self.config.name}] JS提取data-variants失败: {e}")
            return []

        if not raw_data:
            logger.info(f"[{self.config.name}] JS-variants: DOM中无有效商品数据")
            return []

        items = []
        contact_items = []  # contact模式price=0的商品
        for r in raw_data:
            try:
                price = self._parse_variant_price(r)
                img_url = r.get('image_url', '')
                if img_url:
                    img_url = 'https:' + img_url if img_url.startswith('//') else img_url
                    img_url = urljoin(self.config.base_url, img_url)
                href = r.get('href', '')
                product_url = urljoin(self.config.base_url, href) if href else ''
                item = ProductItem(
                    name=r['name'][:300],
                    price=price if price > 0 else 0,
                    sku=str(r.get('sku', ''))[:100],
                    image_url=img_url,
                    product_url=product_url,
                    supplier_id=self.config.id,
                )
                if price > 0:
                    items.append(item)
                    logger.info(f"[{self.config.name}] JS-variants提取: {r['name'][:40]} | {price}")
                else:
                    contact_items.append(item)
                    logger.debug(f"[{self.config.name}] JS-variants价格<=0(可能contact模式): {r['name'][:40]}")
            except Exception as e:
                logger.warning(f"[{self.config.name}] JS-variants单条失败: {e}")

        if not items and raw_data:
            logger.warning(f"[{self.config.name}] JS读取到{len(raw_data)}条但全部转换失败，样本: {str(raw_data[0])[:300]}")
        elif items:
            logger.info(f"[{self.config.name}] JS-variants成功提取 {len(items)} 条")
        if contact_items:
            logger.info(f"[{self.config.name}] JS-variants另有{len(contact_items)}条contact模式商品(price=0)，待详情页补价")
        return items + contact_items

    async def _fetch_detail_prices_js(self, pw_page, items: list[ProductItem], concurrency: int = 5) -> None:
        """
        在浏览器上下文中并发 fetch 商品详情页，补充 contact 模式商品的价格。
        直接用 page.evaluate 发 fetch 请求，无需导航。
        """
        if not items:
            return
        logger.info(f"[{self.config.name}] 开始从详情页补价，共{len(items)}条商品，并发{concurrency}")
        
        # 分批处理
        sem = asyncio.Semaphore(concurrency)
        ok_count = 0
        fail_count = 0
        
        async def fetch_price(item: ProductItem):
            nonlocal ok_count, fail_count
            if not item.product_url or item.price > 0:
                return
            async with sem:
                try:
                    # 在浏览器页面中发fetch请求获取详情页HTML
                    result = await pw_page.evaluate("""async (url) => {
                        try {
                            const resp = await fetch(url, {credentials: 'include'});
                            const html = await resp.text();
                            // 解析价格
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(html, 'text/html');
                            // 优先 js-price-without-taxes（不含税价）
                            const pwt = doc.querySelector('.js-price-without-taxes');
                            // js-price-with-discount（含折扣价）
                            const pwd = doc.querySelector('.js-price-with-discount');
                            // js-price-display（标准价格）
                            const pd = doc.querySelector('.js-price-display');
                            // js-compare-price-display（比较价）
                            const cpd = doc.querySelector('.js-compare-price-display');
                            return {
                                price_without_taxes: pwt ? pwt.textContent.trim() : '',
                                price_with_discount: pwd ? pwd.textContent.trim() : '',
                                price_display: pd ? pd.textContent.trim() : '',
                                compare_price: cpd ? cpd.textContent.trim() : '',
                            };
                        } catch(e) {
                            return {error: e.message};
                        }
                    }""", item.product_url)
                    
                    if result and result.get('error'):
                        logger.debug(f"[{self.config.name}] 详情页fetch失败 {item.product_url[-40:]}: {result['error']}")
                        fail_count += 1
                        return
                    
                    if not result:
                        fail_count += 1
                        return
                    
                    # 解析价格：优先 price_with_discount > price_without_taxes > compare_price > price_display
                    price = 0
                    for key in ['price_with_discount', 'price_without_taxes', 'compare_price', 'price_display']:
                        val = result.get(key, '')
                        if val and val != '$0':
                            # 阿根廷比索格式: $11.990 或 $9.909,09
                            cleaned = val.replace('$', '').replace('.', '').replace(',', '.').strip()
                            try:
                                price = float(cleaned)
                                if price > 0:
                                    break
                            except ValueError:
                                continue
                    
                    if price > 0:
                        item.price = price
                        ok_count += 1
                        logger.info(f"[{self.config.name}] 详情页补价成功: {item.name[:40]} | {price}")
                    else:
                        fail_count += 1
                        logger.debug(f"[{self.config.name}] 详情页无价格 {item.product_url[-40:]}: {result}")
                except Exception as e:
                    fail_count += 1
                    logger.debug(f"[{self.config.name}] 详情页补价异常 {item.product_url[-40:]}: {e}")
        
        # 并发执行
        await asyncio.gather(*[fetch_price(it) for it in items])
        logger.info(f"[{self.config.name}] 详情页补价完成: 成功{ok_count}，失败{fail_count}")

    def _extract_from_jumpseller(self, soup: BeautifulSoup) -> list[ProductItem]:
        """
        从 Jumpseller 平台列表页提取商品。
        特征：article.product-block[data-product-id] 容器，
        a.product-block__anchor 链接，span.product-block__price 价格。
        """
        items = []
        cards = soup.select('article.product-block[data-product-id]')
        if not cards:
            return items
        logger.info(f"[{self.config.name}] Jumpseller提取: 发现 {len(cards)} 个商品卡片")
        for card in cards:
            try:
                # 商品链接和名称
                anchor = card.select_one('a.product-block__anchor')
                if not anchor:
                    continue
                title = (anchor.get('title') or anchor.get_text(strip=True) or '').strip()
                # 去掉 Jumpseller 的 "Ir a " 前缀
                if title.startswith('Ir a '):
                    title = title[5:]
                if not title:
                    continue

                # 价格：优先 span.product-block__price，回退 input[data-price]
                price_el = card.select_one('span.product-block__price')
                price_text = price_el.get_text(strip=True) if price_el else ''
                price = clean_price(price_text)
                if price <= 0:
                    input_el = card.select_one('input.product-block__input')
                    if input_el:
                        try:
                            price = float(input_el.get('data-price', 0))
                        except (ValueError, TypeError):
                            pass
                if price <= 0:
                    continue

                # 图片
                img_el = card.select_one('img.product-block__image')
                img_url = ''
                if img_el:
                    img_url = img_el.get('src') or img_el.get('data-src') or ''
                    if img_url:
                        img_url = urljoin(self.config.base_url, img_url)

                # 商品链接
                href = anchor.get('href', '')
                product_url = urljoin(self.config.base_url, href) if href else ''

                # SKU: 用 data-product-id
                product_id = card.get('data-product-id', '')

                # 提取起订量
                min_qty = 1
                input_el = card.select_one('input.product-block__input')
                if input_el:
                    try:
                        dmin = int(input_el.get('data-min') or input_el.get('min') or 1)
                        if dmin > 0:
                            min_qty = dmin
                    except (ValueError, TypeError):
                        pass

                item = ProductItem(
                    name=title[:300],
                    price=price,
                    sku=product_id[:100],
                    image_url=img_url,
                    product_url=product_url,
                    supplier_id=self.config.id,
                    min_qty=min_qty,
                    package_qty=1,
                )
                items.append(item)
                logger.info(f"[{self.config.name}] Jumpseller: {title[:40]} | {price} | min={min_qty}")
            except Exception as e:
                logger.debug(f"Jumpseller卡片解析失败: {e}")
        return items

        """
        从列表页卡片直接提取商品（无详情页模式）。
        适用于 Distri-Nimay 等自建网站：每个卡片含名称/价格/图片/SKU。
        需要在 selectors 中配置 card_container 选择器。
        """
        card_sel   = self._get_selector("card_container")   # 卡片容器，如 div.divprodnuevos
        name_sel   = self._get_selector("product_name")     # 名称，如 span.fdes
        price_sel  = self._get_selector("price")            # 价格，如 span.fimpo
        img_sel    = self._get_selector("image")            # 图片，如 img.imgcat
        sku_sel    = self._get_selector("sku")              # SKU，如 span.fcod（可选）
        cat_sel    = self._get_selector("category")         # 分类，如 span.frub（可选）

        if not card_sel:
            return []

        cards = soup.select(card_sel)
        items = []
        for card in cards:
            try:
                name_el  = card.select_one(name_sel)  if name_sel  else None
                price_el = card.select_one(price_sel) if price_sel else None
                img_el   = card.select_one(img_sel)   if img_sel   else None
                sku_el   = card.select_one(sku_sel)   if sku_sel   else None
                cat_el   = card.select_one(cat_sel)   if cat_sel   else None

                name = name_el.get_text(strip=True) if name_el else ""
                if not name:
                    continue

                price_text = self._extract_price_text_from_el(price_el)
                price = clean_price(price_text)
                if price <= 0:
                    continue

                img_url = ""
                if img_el:
                    raw = img_el.get("src") or img_el.get("data-src") or ""
                    img_url = urljoin(self.config.base_url, raw) if raw else ""

                sku = ""
                if sku_el:
                    sku_text = sku_el.get_text(strip=True)
                    sku = re.sub(r'(?i)cod[:\s]*', '', sku_text).strip()
                if not sku:
                    ref_el = card.select_one(".reference, span.reference")
                    if ref_el:
                        sku = ref_el.get_text(strip=True).strip()

                category = cat_el.get_text(strip=True) if cat_el else ""

                item = ProductItem(
                    name=name[:300],
                    price=price,
                    sku=sku[:100],
                    category=category[:100],
                    image_url=img_url,
                    supplier_id=self.config.id,
                )
                items.append(item)
                logger.info(f"[{self.config.name}] 列表提取: {name[:40]} | {price}")
            except Exception as e:
                logger.debug(f"卡片解析失败: {e}")
        return items

    async def crawl_js(self) -> list[ProductItem]:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright未安装，回退到静态爬虫")
            return await self.crawl_static()

        # 判断是否使用"JS按钮翻页"模式
        # 条件1：配置了 pagination_btn（旧方式，selectors JSON）
        # 条件2：翻页选择器不是 a 标签（如 button#siguiente1）→ 自动当按钮处理
        btn_sel = self._get_selector("pagination_btn")
        if not btn_sel:
            pag_sel = self._get_selector("pagination")
            if pag_sel and not pag_sel.strip().startswith("a"):
                btn_sel = pag_sel
            elif pag_sel and "load-more" in pag_sel:
                # a.js-load-more 是加载更多按钮，不是普通翻页链接
                btn_sel = pag_sel
        if btn_sel:
            return await self._crawl_js_btn_pagination(btn_sel)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=[
                "--no-sandbox", "--disable-dev-shm-usage",
                "--disable-gpu", "--disable-extensions",
                "--disable-background-networking",
                "--js-flags=--max-old-space-size=512",
            ])
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1280, "height": 800},
            )
            if self.config.use_chrome_cookies:
                cookies = get_chrome_cookies(self.config.base_url)
                if not cookies:
                    # Chrome读取失败，尝试手动Cookie
                    manual = self.config.selectors.get("manual_cookies", "")
                    if manual:
                        cookies = parse_manual_cookies(manual, self.config.base_url)
                if cookies:
                    await context.add_cookies(cookies)
            page = await context.new_page()
            page_url = self.config.product_list_url
            visited = set()

            async with aiohttp.ClientSession(headers=self._make_headers(), connector=aiohttp.TCPConnector(ssl=False)) as session:
                for page_num in range(1, self.config.max_pages + 1):
                    if self._cancelled or page_url in visited:
                        break
                    visited.add(page_url)
                    logger.info(f"[{self.config.name}] JS渲染 第{page_num}页: {page_url}")
                    try:
                        await page.goto(page_url, wait_until="domcontentloaded", timeout=self.config.timeout * 1000)
                        await page.wait_for_timeout(3000)
                        # 等待 window.data.products 注入（Tiendanube平台）
                        try:
                            await page.wait_for_function("() => window.data && window.data.products && Object.keys(window.data.products).length > 0", timeout=8000)
                        except Exception:
                            pass
                        # 等待商品元素或window.data出现
                        try:
                            await page.wait_for_function("typeof window.data !== 'undefined' && window.data.products", timeout=8000)
                        except Exception:
                            pass
                        # 诊断：保存页面截图和HTML
                        try:
                            import os as _os
                            _diag_dir = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "images")
                            await page.screenshot(path=_os.path.join(_diag_dir, f"diag_{self.config.name}.png"), full_page=False)
                            _html_snap = await page.content()
                            with open(_os.path.join(_diag_dir, f"diag_{self.config.name}.html"), "w", encoding="utf-8") as _f:
                                _f.write(_html_snap)
                            logger.info(f"[{self.config.name}] 诊断文件已保存到 images/diag_*.png/html")
                        except Exception as _e:
                            logger.debug(f"诊断保存失败: {_e}")
                        html = await page.content()
                        # 诊断：看页面里有没有商品数据特征
                        if 'data-variants' in html:
                            logger.info(f"[{self.config.name}] 检测到data-variants，使用卡片提取模式")
                        elif 'window.data' in html:
                            logger.info(f"[{self.config.name}] 检测到window.data")
                        else:
                            snippet = BeautifulSoup(html, 'lxml').get_text()[:300].strip()
                            logger.info(f"[{self.config.name}] 页面片段: {snippet!r}")
                        html = await page.content()
                        soup = BeautifulSoup(html, "lxml")

                        # ── 策略1: 内嵌JSON（Tiendanube等平台）──────────────
                        json_items = self._extract_from_page_json(html, page_url)
                        if json_items:
                            logger.info(f"[{self.config.name}] 第{page_num}页 JSON提取 {len(json_items)} 条，开始下载图片...")
                            sem = asyncio.Semaphore(8)
                            async def _dl(it, _sem=sem, _session=session):
                                if not self._cancelled and it.image_url:
                                    async with _sem:
                                        it.image_local_path = await self.downloader.download(
                                            _session, it.image_url, self.config.name
                                        )
                            await asyncio.gather(*[_dl(it) for it in json_items])
                            for item in json_items:
                                if self._cancelled:
                                    break
                                self.products.append(item)
                                self.stats["products_found"] += 1
                            logger.info(f"[{self.config.name}] 第{page_num}页图片下载完成")

                        else:
                            # ── 策略1.5: Jumpseller平台提取 ──────────────────
                            jump_items = self._extract_from_jumpseller(soup)
                            if jump_items:
                                logger.info(f"[{self.config.name}] 第{page_num}页 Jumpseller提取 {len(jump_items)} 条，开始下载图片...")
                                sem = asyncio.Semaphore(8)
                                async def _dl_j(it, _sem=sem, _session=session):
                                    if not self._cancelled and it.image_url:
                                        async with _sem:
                                            it.image_local_path = await self.downloader.download(
                                                _session, it.image_url, self.config.name
                                            )
                                await asyncio.gather(*[_dl_j(it) for it in jump_items])
                                for item in jump_items:
                                    if self._cancelled:
                                        break
                                    self.products.append(item)
                                    self.stats["products_found"] += 1
                                logger.info(f"[{self.config.name}] 第{page_num}页图片下载完成")

                            else:
                                # ── 策略2: 从列表页HTML提取（含容器匹配）──────────
                                link_sel = self._get_selector("product_links")
                                links_els = soup.select(link_sel) if link_sel else []

                                if links_els and self._get_selector("product_name") == link_sel:
                                    product_urls = list(dict.fromkeys(
                                        urljoin(self.config.base_url, el.get("href"))
                                        for el in links_els if el.get("href")
                                    ))
                                    for url in product_urls:
                                        if self._cancelled:
                                            break
                                        item = await self._parse_product_from_list(session, soup, url, links_els)
                                        if item:
                                            self.products.append(item)
                                            self.stats["products_found"] += 1

                                elif links_els:
                                    # ── 策略3: 进详情页逐个提取 ─────────────────
                                    for el in links_els:
                                        if self._cancelled:
                                            break
                                        href = el.get("href")
                                        if href:
                                            url = urljoin(self.config.base_url, href)
                                            item = await self._parse_product_page(session, url)
                                            if item:
                                                self.products.append(item)
                                                self.stats["products_found"] += 1
                                else:
                                    logger.error(f"[{self.config.name}] 第{page_num}页未找到商品，选择器={link_sel!r}")
                                    break

                        self.stats["pages_crawled"] += 1
                        await self._report_progress()

                        # 翻页（href模式）
                        pag_sel = self._get_selector("pagination")
                        next_btn = soup.select_one(pag_sel) if pag_sel else None
                        if not next_btn:
                            logger.info(f"[{self.config.name}] 已到最后一页（第{page_num}页）")
                            break
                        next_href = next_btn.get("href")
                        if not next_href:
                            break
                        next_url = urljoin(self.config.base_url, next_href)
                        if next_url == page_url or next_url in visited:
                            break
                        page_url = next_url
                        await asyncio.sleep(self.config.request_delay + random.uniform(0, 1))

                    except asyncio.CancelledError:
                        self._cancelled = True
                        break
                    except Exception as e:
                        logger.error(f"[{self.config.name}] JS页面爬取失败: {e}")
                        self.stats["errors"] += 1
                        break

            await browser.close()
        return self.products

    async def _crawl_js_btn_pagination(self, btn_sel: str) -> list[ProductItem]:
        """
        JS按钮翻页模式（适用于Distri-Nimay等）：
        - 点击按钮翻页，无URL变化
        - 通过对比第一条商品名称检测是否回到第一页（循环翻页检测）
        - 从列表页卡片直接提取商品（无需进详情页）
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright未安装")
            return []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=[
                "--no-sandbox", "--disable-dev-shm-usage",
                "--disable-gpu", "--disable-extensions",
                "--disable-background-networking",
                "--js-flags=--max-old-space-size=512",
            ])
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1280, "height": 800},
            )
            if self.config.use_chrome_cookies:
                cookies = get_chrome_cookies(self.config.base_url)
                if not cookies:
                    manual = self.config.selectors.get("manual_cookies", "")
                    if manual:
                        cookies = parse_manual_cookies(manual, self.config.base_url)
                if cookies:
                    await context.add_cookies(cookies)
            pw_page = await context.new_page()

            async with aiohttp.ClientSession(headers=self._make_headers(), connector=aiohttp.TCPConnector(ssl=False)) as session:
                try:
                    logger.info(f"[{self.config.name}] JS按钮翻页模式，加载页面...")
                    await pw_page.goto(
                        self.config.product_list_url,
                        wait_until="domcontentloaded",
                        timeout=120000,  # 大页面给120秒加载
                    )
                    await pw_page.wait_for_timeout(2500)

                    name_sel  = self._get_selector("product_name")
                    card_sel  = self._get_selector("card_container")
                    first_page_first_name = None  # 第一页第一个商品名，用于检测循环

                    # load-more模式：等待页面初始化即可，后续通过点击按钮加载更多
                    is_load_more_init = "load-more" in btn_sel or "loadmore" in btn_sel
                    if is_load_more_init:
                        logger.info(f"[{self.config.name}] load-more模式：等待页面初始化(15秒)...")
                        await pw_page.wait_for_timeout(15000)
                        cur_count = await pw_page.evaluate(
                            "() => document.querySelectorAll('div[data-variants]').length"
                        )
                        logger.info(f"[{self.config.name}] 初始商品数={cur_count}，将通过点击load-more按钮加载更多")

                    for page_num in range(1, self.config.max_pages + 1):
                        if self._cancelled:
                            break

                        # load-more模式：等DOM稳定（连续500ms无新商品）再提取
                        is_load_more_mode = "load-more" in btn_sel or "loadmore" in btn_sel
                        if is_load_more_mode:
                            stable_count = await pw_page.evaluate(
                                "() => document.querySelectorAll('div.js-item-product, div[data-variants]').length"
                            )
                            for _ in range(6):  # 最多等3秒
                                await pw_page.wait_for_timeout(500)
                                new_count = await pw_page.evaluate(
                                    "() => document.querySelectorAll('div.js-item-product, div[data-variants]').length"
                                )
                                if new_count == stable_count:
                                    break
                                stable_count = new_count
                            logger.info(f"[{self.config.name}] DOM稳定，共{stable_count}个商品卡片")

                        html = await pw_page.content()
                        soup = BeautifulSoup(html, "lxml")

                        # 检测是否回到第一页（循环翻页检测）
                        current_first_name = ""
                        if name_sel:
                            el = soup.select_one(name_sel)
                            current_first_name = el.get_text(strip=True) if el else ""
                        elif card_sel:
                            card = soup.select_one(card_sel)
                            current_first_name = card.get_text(strip=True)[:30] if card else ""

                        if page_num == 1:
                            first_page_first_name = current_first_name
                            logger.info(f"[{self.config.name}] 第一页标记: {first_page_first_name!r}")
                            _seen_urls: set = set()  # 追加加载去重
                        elif current_first_name and current_first_name == first_page_first_name and not is_load_more_mode:
                            logger.info(f"[{self.config.name}] 检测到回到第一页，已爬完所有页面（共{page_num-1}页）")
                            break
                        else:
                            logger.info(f"[{self.config.name}] 第{page_num}页首条商品: {current_first_name!r}")

                        # 提取当前页商品（优先JSON → data-variants → JS读取 → CSS选择器）
                        logger.info(f"[{self.config.name}] 第{page_num}页开始提取，card_sel={card_sel!r}")

                        # 策略1: window.data.products JSON
                        all_items = self._extract_from_page_json(html, page_url if 'page_url' in dir() else self.config.product_list_url)

                        # 策略2: data-variants（HTML解析）
                        if not all_items:
                            all_items = self._extract_from_data_variants(soup)

                        # 策略3: 通过JS直接从活DOM读取data-variants（Tiendanube平台数据由JS填充）
                        if not all_items and is_load_more_mode:
                            all_items = await self._extract_from_data_variants_js(pw_page)

                        # 策略4: CSS选择器
                        if not all_items:
                            all_items = self._extract_from_list_page(soup)

                        if not all_items:
                            cards_found = soup.select(card_sel) if card_sel else []
                            first_card_text = cards_found[0].get_text(strip=True)[:100] if cards_found else "无卡片"
                            logger.error(f"[{self.config.name}] 第{page_num}页未提取到商品，card_sel={card_sel!r}，找到{len(cards_found)}个卡片，第一个: {first_card_text!r}")
                            break

                        # load-more追加式：跳过已处理的商品（按URL或名称去重）
                        is_load_more = "load-more" in btn_sel or "loadmore" in btn_sel
                        if is_load_more and page_num > 1:
                            new_items = [it for it in all_items if (it.product_url or it.name) not in _seen_urls]
                            logger.info(f"[{self.config.name}] 追加去重：总{len(all_items)}条，新增{len(new_items)}条")
                        else:
                            new_items = all_items
                        # 记录已见
                        for it in all_items:
                            _seen_urls.add(it.product_url or it.name)
                        items = new_items

                        # contact模式补价：对price=0的商品从详情页获取价格
                        zero_price_items = [it for it in items if it.price <= 0 and it.product_url]
                        if zero_price_items:
                            logger.info(f"[{self.config.name}] {len(zero_price_items)}条商品price=0，尝试从详情页补价")
                            await self._fetch_detail_prices_js(pw_page, zero_price_items, concurrency=5)
                            # 过滤掉补价仍失败的商品
                            still_zero = [it for it in items if it.price <= 0]
                            if still_zero:
                                logger.warning(f"[{self.config.name}] {len(still_zero)}条商品补价后仍为0，过滤掉")
                                items = [it for it in items if it.price > 0]

                        # 下载图片
                        sem = asyncio.Semaphore(4)
                        async def _dl_btn(it, _sem=sem, _sess=session):
                            if not self._cancelled and it.image_url:
                                async with _sem:
                                    it.image_local_path = await self.downloader.download(
                                        _sess, it.image_url, self.config.name
                                    )
                        try:
                            await asyncio.gather(*[_dl_btn(it) for it in items])
                        except Exception as e:
                            logger.error(f"[{self.config.name}] 图片下载异常: {e}")
                            import traceback; logger.error(traceback.format_exc())

                        for item in items:
                            if self._cancelled:
                                break
                            self.products.append(item)
                            self.stats["products_found"] += 1

                        self.stats["pages_crawled"] += 1
                        await self._report_progress()
                        logger.info(f"[{self.config.name}] 第{page_num}页完成，提取{len(items)}条，累计{self.stats['products_found']}条")

                        # 点击翻页/加载更多按钮
                        btn = await pw_page.query_selector(btn_sel)
                        if not btn:
                            logger.info(f"[{self.config.name}] 翻页按钮未找到，等待10秒确认...")
                            await pw_page.wait_for_timeout(10000)
                            btn = await pw_page.query_selector(btn_sel)
                            if not btn:
                                logger.info(f"[{self.config.name}] 确认无翻页按钮({btn_sel!r})，已到最后页")
                                break
                        # 等待按钮可见
                        try:
                            await pw_page.wait_for_selector(f"{btn_sel}:visible", timeout=10000)
                        except Exception:
                            pass
                        # 记录点击前商品数量（用于load-more追加检测）
                        count_before = await pw_page.evaluate(
                            "() => document.querySelectorAll('div.js-item-product, div[data-variants]').length"
                        )
                        # load-more模式：滚动加载更多，追加提取
                        if is_load_more_mode:
                            # 滚到底部触发infinite scroll或显示load-more按钮
                            await pw_page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                            await pw_page.wait_for_timeout(3000)
                            # 尝试点击load-more按钮（可能是div或a，且可能自动触发了滚动加载）
                            try:
                                btn_exists = await pw_page.evaluate(
                                    f"() => {{ const b = document.querySelector('{btn_sel}'); return b && b.offsetParent !== null && getComputedStyle(b).display !== 'none'; }}"
                                )
                            except Exception:
                                btn_exists = False
                            if btn_exists:
                                try:
                                    await btn.click()
                                except Exception:
                                    await pw_page.evaluate(f'document.querySelector("{btn_sel}").click()')
                                logger.info(f"[{self.config.name}] 点击load-more按钮（当前商品数={count_before}）")
                            # 等待新商品出现
                            try:
                                await pw_page.wait_for_function(
                                    f"() => document.querySelectorAll('div.js-item-product, div[data-variants]').length > {count_before}",
                                    timeout=20000
                                )
                                await pw_page.wait_for_timeout(1000)
                                count_after = await pw_page.evaluate(
                                    "() => document.querySelectorAll('div.js-item-product, div[data-variants]').length"
                                )
                                logger.info(f"[{self.config.name}] load-more追加成功，商品数 {count_before} → {count_after}")
                            except Exception:
                                logger.info(f"[{self.config.name}] load-more无新商品，已加载全部")
                                break
                            continue  # 回到循环顶部提取新一批商品
                        # 非load-more：滚到底部找按钮
                        for _scroll in range(3):
                            await pw_page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                            await pw_page.wait_for_timeout(1000)
                        btn_visible = False
                        try:
                            await pw_page.wait_for_function(
                                f"() => {{ const b = document.querySelector('{btn_sel}'); return b && b.offsetParent !== null && getComputedStyle(b).display !== 'none'; }}",
                                timeout=8000
                            )
                            btn_visible = True
                            logger.info(f"[{self.config.name}] 按钮已可见，准备点击")
                        except Exception:
                            pass
                        if not btn_visible:
                            logger.info(f"[{self.config.name}] 按钮不可见，已加载全部商品，停止")
                            break
                        try:
                            await btn.scroll_into_view_if_needed()
                        except Exception:
                            pass
                        await pw_page.wait_for_timeout(500)
                        try:
                            await btn.click()
                        except Exception:
                            await pw_page.evaluate(f'document.querySelector("{btn_sel}").click()')
                        logger.info(f"[{self.config.name}] 已点击翻页按钮（点击前商品数={count_before}）")
                        # 替换式翻页：等固定时间
                        await pw_page.wait_for_timeout(int(self.config.request_delay * 1000) + random.randint(800, 2000))
                        if card_sel:
                            try:
                                await pw_page.wait_for_selector(card_sel, timeout=8000)
                                await pw_page.wait_for_timeout(500)
                            except Exception:
                                html_snap = await pw_page.content()
                                soup_snap = BeautifulSoup(html_snap, "lxml")
                                logger.error(f"[{self.config.name}] 翻页后等待{card_sel!r}超时，页面片段: {soup_snap.get_text()[:200].strip()!r}")

                except asyncio.CancelledError:
                    self._cancelled = True
                except Exception as e:
                    logger.error(f"[{self.config.name}] JS按钮翻页失败: {e}")
                    self.stats["errors"] += 1
                finally:
                    await browser.close()

        return self.products

    async def run(self) -> list[ProductItem]:
        self.stats["start_time"] = datetime.now()
        logger.info(f"开始爬取: {self.config.name} | JS={self.config.use_js_render}")
        try:
            sel_type = (self.config.selectors or {}).get("type", "")
            if (
                sel_type in ("wc_store", "wc_store_api", "woocommerce")
                or "wp-json/wc/store" in (self.config.product_list_url or "")
                or "bellacentral" in (self.config.base_url or "")
            ):
                from .wc_store_spider import WooCommerceStoreSpider
                spider = WooCommerceStoreSpider(self.config, self.db, self.log_id)
                spider.on_item_saved = getattr(self, "on_item_saved", None)
                products = await spider.run()
                self.stats = spider.stats
                return products
            elif (
                sel_type in ("tiendanube", "nuvemshop")
                or "osadistribuidora" in (self.config.base_url or "").lower()
                or self.config.name.lower() == "osa"
            ):
                from .tiendanube_spider import TiendanubeSpider
                spider = TiendanubeSpider(self.config, self.db, self.log_id)
                spider.on_item_saved = getattr(self, "on_item_saved", None)
                products = await spider.run()
                self.stats = spider.stats
                return products
            elif self.config.use_js_render:
                products = await self.crawl_js()
            else:
                products = await self.crawl_static()
        except asyncio.CancelledError:
            logger.info(f"[{self.config.name}] 爬取已取消")
            products = self.products
        self.stats["end_time"] = datetime.now()
        duration = (self.stats["end_time"] - self.stats["start_time"]).seconds
        logger.info(f"[{self.config.name}] 完成 | 商品:{len(products)} 页面:{self.stats['pages_crawled']} 耗时:{duration}s 错误:{self.stats['errors']}")
        return products
