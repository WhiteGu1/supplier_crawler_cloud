"""
supplier_crawler/crawler/alibaba1688_spider.py

阿里巴巴1688爬虫 - CDP模式（单标签页导航）
- 连接已登录的本机Chrome/Edge浏览器（通过CDP调试端口）
- 支持两种页面类型：
  1. 旺铺商品列表页（shopxxx.1688.com/page/offerlist.htm）—— 翻页按钮分页
  2. 工厂直供页（sale.1688.com/factory/xxx.html）—— 无限滚动加载
- 详情页格式一致：detail.1688.com/offer/{offerId}.html
- 每个SKU颜色独立存一条记录

启动Chrome调试模式（先关闭所有Chrome窗口）：
  "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-debug"

或启动Edge调试模式：
  "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\edge-debug"

然后在浏览器里登录1688，再启动爬取。

供应商配置（旺铺）：
  base_url  = https://shop3096q62737308.1688.com
  list_url  = https://shop3096q62737308.1688.com/page/offerlist.htm
  use_js    = 1
  selectors = {"type": "alibaba1688", "cdp_url": "http://localhost:9222"}

供应商配置（工厂直供）：
  base_url  = https://sale.1688.com
  list_url  = https://sale.1688.com/factory/l6rr893d.html?memberId=b2b-xxx
  use_js    = 1
  selectors = {"type": "alibaba1688", "cdp_url": "http://localhost:9222", "page_type": "factory"}
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime

logger = logging.getLogger(__name__)

CARD_TITLE_SEL = "p[title]"
FACTORY_ITEM_SEL = "a.galleyItemLink"
_RE_OFFER_ID   = re.compile(r'/offer/(\d+)\.html')
_RE_FACTORY    = re.compile(r'sale\.1688\.com/factory/')
_RE_SUBJECT    = re.compile(r'"subject"\s*:\s*"([^"]+)"')
_RE_MIN_PRICE  = re.compile(r'"offerMinPrice"\s*:\s*"?([0-9.]+)"?')
_RE_SKU_PROPS  = re.compile(r'"skuProps"\s*:\s*(\[.*?\])\s*,\s*"', re.DOTALL)
_RE_SKU_MAP    = re.compile(r'"skuMap"\s*:\s*(\[.*?\])\s*,\s*"', re.DOTALL)
_RE_IMAGE_LIST = re.compile(r'"imageList"\s*:\s*(\[.*?\])\s*,\s*"', re.DOTALL)


# ── 详情页解析 ────────────────────────────────────────────────────────────────

def _extract_detail(html: str, offer_id: str, supplier_id: int) -> list[dict]:
    product_url = f"https://detail.1688.com/offer/{offer_id}.html"

    m = _RE_SUBJECT.search(html)
    if not m:
        logger.warning(f"[1688] offer={offer_id} 未找到subject，跳过")
        return []
    base_name = m.group(1).strip()

    m_min = _RE_MIN_PRICE.search(html)
    fallback_price = float(m_min.group(1)) if m_min else 0.0

    sku_props: list[dict] = []
    m_props = _RE_SKU_PROPS.search(html)
    if m_props:
        try:
            sku_props = json.loads(m_props.group(1))
        except Exception:
            pass

    sku_price_map: dict[str, float] = {}
    m_map = _RE_SKU_MAP.search(html)
    if m_map:
        try:
            for entry in json.loads(m_map.group(1)):
                spec  = entry.get("specAttrs", "")
                price = float(entry.get("price", 0) or entry.get("discountPrice", 0) or 0)
                if spec and price > 0:
                    sku_price_map[spec] = price
        except Exception:
            pass

    main_images: list[str] = []
    m_imgs = _RE_IMAGE_LIST.search(html)
    if m_imgs:
        try:
            for img in json.loads(m_imgs.group(1)):
                url = img.get("fullPathImageURI") or img.get("size310x310ImageURI", "")
                if url:
                    main_images.append(url)
        except Exception:
            pass

    results = []
    if sku_props:
        first_prop = sku_props[0]
        for v in first_prop.get("value", []):
            spec_name = v.get("name", "").strip()
            img_url   = v.get("imageUrl", "")
            if img_url and not img_url.startswith("http"):
                img_url = "https:" + img_url
            if img_url and "." not in img_url.split("/")[-1]:
                img_url += ".jpg"
            price = sku_price_map.get(spec_name, fallback_price)
            _clean   = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', spec_name)
            sku_code = f"{offer_id}_{_clean}"
            name     = f"{base_name} - {spec_name}" if spec_name else base_name
            # product_url加sku后缀，避免upsert时同一offer多个SKU互相覆盖
            sku_product_url = f"{product_url}?sku={sku_code}"
            results.append({
                "name": name, "price": price, "image_url": img_url,
                "sku": sku_code, "product_url": sku_product_url,
            })
        if all(not r["image_url"] for r in results) and main_images:
            for r in results:
                r["image_url"] = main_images[0]

    if not results:
        results.append({
            "name": base_name, "price": fallback_price,
            "image_url": main_images[0] if main_images else "",
            "sku": offer_id, "product_url": product_url,
        })
    return results


# ── 主爬虫类 ──────────────────────────────────────────────────────────────────

class Alibaba1688Spider:
    def __init__(self, config, db_manager, log_id: int = 0):
        self.config = config
        self.db     = db_manager
        self.log_id = log_id
        self._cancelled = False
        self.stats = {
            "pages_crawled": 0, "products_found": 0,
            "errors": 0, "start_time": None, "end_time": None,
        }
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.images_dir = os.path.join(base_dir, "images", f"1688_{config.id}")
        os.makedirs(self.images_dir, exist_ok=True)
        # 增量写库回调：每爬完一个offer立即写库，防止中断丢数据
        self.on_item_saved = None  # callable(products: list[ProductItem]) -> int
        # 断点续传：已爬offer_id集合（精确匹配，不依赖商品名）
        self._crawled_offer_ids: set[str] = set()
        try:
            if self.db:
                self._crawled_offer_ids = self.db.get_existing_offer_ids(self.config.id)
                if self._crawled_offer_ids:
                    logger.info(f"[1688] 断点续传：数据库已有 {len(self._crawled_offer_ids)} 个offer_id")
        except Exception as e:
            logger.warning(f"[1688] 加载已爬offer_id失败: {e}")

    def cancel(self):
        self._cancelled = True

    def _save_items(self, items: list[dict]) -> int:
        """增量写库：把刚爬完的一批item立即组装并写入数据库"""
        if not items or not self.on_item_saved:
            return 0
        from .spider import ProductItem
        products = []
        for item in items:
            products.append(ProductItem(
                name             = item["name"],
                price            = item["price"],
                sku              = item["sku"],
                image_url        = item.get("image_url", ""),
                image_local_path = item.get("image_local", ""),
                product_url      = item["product_url"],
                supplier_id      = self.config.id,
                currency         = "CNY",
            ))
        try:
            saved = self.on_item_saved(products)
            self.stats["products_found"] += saved
            logger.info(f"[1688] 增量入库 {saved} 条，累计 {self.stats['products_found']}")
            return saved
        except Exception as e:
            logger.error(f"[1688] 增量入库失败: {e}")
            return 0

    def _is_already_crawled(self, offer_id: str) -> bool:
        """断点续传：检查offer_id是否已在数据库中（精确匹配）"""
        return bool(offer_id and offer_id in self._crawled_offer_ids)

    def _mark_crawled(self, items: list[dict]):
        """爬完后把offer_id加入已爬集合，供后续比对"""
        import re as _re
        for item in items:
            url = item.get("product_url", "")
            m = _re.search(r'/offer/(\d+)\.html', url)
            if m:
                self._crawled_offer_ids.add(m.group(1))

    def _cdp_url(self):
        return self.config.selectors.get("cdp_url", "http://localhost:9222")

    def _is_factory_page(self) -> bool:
        """判断是否为工厂直供页（sale.1688.com/factory/）"""
        # 优先看 selectors 中的 page_type 配置
        page_type = self.config.selectors.get("page_type", "")
        if page_type == "factory":
            return True
        if page_type == "shop":
            return False
        # 自动判断：URL中包含 sale.1688.com/factory/
        return bool(_RE_FACTORY.search(self.config.product_list_url or ""))

    async def _download_image_http(self, session, url: str, sku: str) -> str:
        """用aiohttp下载图片"""
        if not url:
            return ""
        try:
            ext = ".jpg"
            m = re.search(r'\.(jpg|jpeg|png|webp)', url, re.IGNORECASE)
            if m:
                ext = "." + m.group(1).lower()
            fname_base = re.sub(r'[^a-zA-Z0-9_\-]', '', sku)[:60]
            if not fname_base:
                fname_base = str(abs(hash(url)))[:16]
            fname    = fname_base + ext
            fpath    = os.path.join(self.images_dir, fname)
            rel_path = f"images/1688_{self.config.id}/{fname}"
            if os.path.exists(fpath):
                return rel_path
            import aiohttp
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status == 200:
                    with open(fpath, "wb") as f:
                        f.write(await resp.read())
                    return rel_path
                else:
                    logger.debug(f"[1688] 图片下载失败 status={resp.status} {url}")
        except Exception as e:
            logger.debug(f"[1688] 图片下载失败 {url}: {e}")
        return ""

    async def _download_image(self, context, url: str, sku: str) -> str:
        if not url:
            return ""
        try:
            ext = ".jpg"
            m = re.search(r'\.(jpg|jpeg|png|webp)', url, re.IGNORECASE)
            if m:
                ext = "." + m.group(1).lower()
            fname_base = re.sub(r'[^a-zA-Z0-9_\-]', '', sku)[:60]
            if not fname_base:
                fname_base = re.sub(r'[^a-zA-Z0-9]', '', url.split('/')[-1])[:60]
            if not fname_base:
                fname_base = str(abs(hash(url)))[:16]
            fname    = fname_base + ext
            fpath    = os.path.join(self.images_dir, fname)
            rel_path = f"images/1688_{self.config.id}/{fname}"
            if os.path.exists(fpath):
                return rel_path
            # 用context.request直接发请求，带登录Cookie，不需要开新标签页
            resp = await context.request.get(
                url,
                headers={"Referer": "https://detail.1688.com/"},
                timeout=20000
            )
            if resp.status == 200:
                with open(fpath, "wb") as f:
                    f.write(await resp.body())
                return rel_path
            else:
                logger.debug(f"[1688] 图片下载失败 status={resp.status} {url}")
        except Exception as e:
            logger.debug(f"[1688] 图片下载失败 {url}: {e}")
        return ""

    # ── 工厂直供页爬取（无限滚动） ──────────────────────────────────────────

    async def _crawl_factory_page(self, context) -> list[dict]:
        """
        工厂直供页爬取（sale.1688.com/factory/xxx.html）：
        1. 打开工厂页，等待商品卡片加载
        2. 滚动到底部触发懒加载，直到没有新商品加载
        3. 收集所有商品链接（a.galleyItemLink → detail.1688.com/offer/xxx.html）
        4. 逐个打开详情页提取数据
        """
        all_items = []
        page = await context.new_page()
        list_url = self.config.product_list_url

        try:
            logger.info(f"[1688-factory] 打开工厂页: {list_url}")
            await page.goto(list_url, wait_until="domcontentloaded",
                            timeout=self.config.timeout * 1000)
            # 等待商品链接出现
            try:
                await page.wait_for_selector(FACTORY_ITEM_SEL, timeout=15000)
            except Exception:
                logger.warning("[1688-factory] 等待商品卡片超时")
            await page.wait_for_timeout(2000)

            # ── 滚动加载所有商品 ──
            visited_offer_ids = set()
            scroll_round = 0
            max_scroll_rounds = 50  # 安全上限，防止无限滚动

            while not self._cancelled and scroll_round < max_scroll_rounds:
                # 收集当前已加载的商品链接
                links_data = await page.evaluate("""() => {
                    const links = document.querySelectorAll('a.galleyItemLink');
                    return Array.from(links).map(a => ({
                        href: a.href,
                        img: (a.querySelector('img.galleyImg') || {}).src || ''
                    })).filter(x => x.href && x.href.indexOf('detail.1688.com/offer/') >= 0);
                }""")

                new_links = [x for x in links_data if x["href"] not in visited_offer_ids
                             or _RE_OFFER_ID.search(x["href"]).group(1) not in visited_offer_ids]

                # 提取offerId去重
                current_count = len(visited_offer_ids)
                for x in links_data:
                    m = _RE_OFFER_ID.search(x["href"])
                    if m:
                        visited_offer_ids.add(m.group(1))

                loaded_count = len(visited_offer_ids)
                logger.info(f"[1688-factory] 滚动第{scroll_round+1}轮，已加载 {loaded_count} 个商品")

                if len(new_links) == 0 and scroll_round > 0:
                    # 没有新商品加载了
                    logger.info("[1688-factory] 无更多商品，停止滚动")
                    break

                # 滚动到底部
                prev_height = await page.evaluate("document.body.scrollHeight")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
                new_height = await page.evaluate("document.body.scrollHeight")

                if new_height == prev_height and len(new_links) == 0:
                    logger.info("[1688-factory] 页面高度未变化且无新商品，停止滚动")
                    break

                scroll_round += 1

            logger.info(f"[1688-factory] 滚动完成，共 {len(visited_offer_ids)} 个商品，开始逐个爬取详情")

            # ── 收集所有商品链接（最终） ──
            all_links = await page.evaluate("""() => {
                const links = document.querySelectorAll('a.galleyItemLink');
                const seen = new Set();
                const result = [];
                for (const a of links) {
                    if (a.href && a.href.indexOf('detail.1688.com/offer/') >= 0) {
                        const m = a.href.match(/\/offer\/(\d+)\.html/);
                        const offerId = m ? m[1] : '';
                        if (offerId && !seen.has(offerId)) {
                            seen.add(offerId);
                            // 尝试获取商品名：galleyItem 元素的 title 属性或子元素文本
                            let title = a.getAttribute('title') || '';
                            if (!title) {
                                const nameEl = a.querySelector('.galleyItemName, .title, .name') ||
                                               a.parentElement.querySelector('.galleyItemName, .title, .name');
                                if (nameEl) title = nameEl.textContent.trim();
                            }
                            result.push({
                                href: a.href,
                                offerId: offerId,
                                title: title,
                                img: (a.querySelector('img.galleyImg') || {}).src || ''
                            });
                        }
                    }
                }
                return result;
            }""")

            logger.info(f"[1688-factory] 去重后共 {len(all_links)} 个商品")

            # ── 逐个打开详情页 ──
            for idx, link_info in enumerate(all_links):
                if self._cancelled:
                    break

                offer_id = link_info["offerId"]
                href = link_info["href"]
                list_title = link_info.get("title", "")
                list_img = link_info.get("img", "")

                # 断点续传：offer_id已在数据库中则跳过
                if self._is_already_crawled(offer_id):
                    logger.info(f"[1688-factory] ({idx+1}/{len(all_links)}) offer={offer_id} 已爬过，跳过")
                    continue

                logger.info(f"[1688-factory] ({idx+1}/{len(all_links)}) offer={offer_id}")

                try:
                    # 打开详情页（新标签页）
                    async with context.expect_page(timeout=15000) as new_page_info:
                        await page.evaluate(f"window.open('{href}', '_blank')")

                    new_page = await new_page_info.value
                    try:
                        await new_page.wait_for_load_state("domcontentloaded", timeout=15000)
                    except Exception:
                        pass

                    # 等待数据加载：优先等skuProps出现在HTML中（更可靠）
                    # window.context.result可能不再可用，改为直接检查HTML内容
                    data_ready = False
                    for _wait_round in range(3):
                        try:
                            await new_page.wait_for_function(
                                r"""() => /skuProps|"subject"\s*:\s*"/.test(document.documentElement.innerHTML)""",
                                timeout=8000
                            )
                            data_ready = True
                            break
                        except Exception:
                            logger.debug(f"[1688-factory] offer={offer_id} 第{_wait_round+1}轮等待数据超时，重试...")
                            try:
                                await new_page.reload(wait_until="domcontentloaded", timeout=15000)
                                await new_page.wait_for_timeout(3000)
                            except Exception:
                                pass
                    
                    if not data_ready:
                        logger.warning(f"[1688-factory] offer={offer_id} 数据未加载完成，跳过")
                        await new_page.close()
                        self.stats["errors"] += 1
                        continue
                    
                    # 额外等待确保JS渲染完成
                    await new_page.wait_for_timeout(2000)
                    
                    html = await new_page.content()
                    items = _extract_detail(html, offer_id, self.config.id)
                    
                    # 如果详情页没提取到图片，用列表页的缩略图
                    if items and all(not r.get("image_url") for r in items) and list_img:
                        for r in items:
                            r["image_url"] = list_img

                    # 在关闭标签页之前下载图片
                    for item in items:
                        if item.get("image_url"):
                            try:
                                ext = ".jpg"
                                mm = re.search(r'\.(jpg|jpeg|png|webp)', item["image_url"], re.IGNORECASE)
                                if mm:
                                    ext = "." + mm.group(1).lower()
                                # 用image_url的hash做文件名，避免不同SKU中文去掉后同名
                                fname_base = str(abs(hash(item["image_url"])))[:20]
                                fname = f"{offer_id}_{fname_base}{ext}"
                                fpath = os.path.join(self.images_dir, fname)
                                if not os.path.exists(fpath):
                                    resp = await new_page.request.get(
                                        item["image_url"],
                                        headers={"Referer": "https://detail.1688.com/"},
                                        timeout=20000
                                    )
                                    if resp.status == 200:
                                        with open(fpath, "wb") as f:
                                            f.write(await resp.body())
                                item["image_local"] = f"images/1688_{self.config.id}/{fname}"
                            except Exception as img_e:
                                logger.debug(f"[1688-factory] 图片下载失败: {img_e}")
                                item["image_local"] = ""
                        else:
                            item["image_local"] = ""

                    await new_page.close()
                    all_items.extend(items)
                    self._save_items(items)  # 增量写库
                    self._mark_crawled(items)  # 加入已爬集合
                    logger.info(f"[1688-factory] offer={offer_id} 提取到 {len(items)} 条SKU")

                except Exception as e:
                    logger.warning(f"[1688-factory] offer={offer_id} 处理失败: {e}")
                    self.stats["errors"] += 1
                    # 关闭可能残留的新标签页
                    try:
                        for p in context.pages:
                            if p != page:
                                await p.close()
                    except Exception:
                        pass
                    continue

                await asyncio.sleep(self.config.request_delay)

            self.stats["pages_crawled"] = 1  # 工厂页算1页

        except Exception as e:
            logger.error(f"[1688-factory] 爬取过程异常: {e}")
        finally:
            await page.close()

        return all_items

    # ── 旺铺列表页爬取（翻页按钮分页） ────────────────────────────────────────

    async def _crawl_with_single_page(self, context) -> list[dict]:
        """
        用单个标签页完成全部爬取：
        1. 打开列表页，收集所有商品卡片标题+顺序
        2. 点击第N个卡片 → 页面跳转到详情页 → 提取数据
        3. 返回列表页（browser.go_back）→ 点击第N+1个
        4. 列表页翻页后重复
        """
        all_items = []
        page = await context.new_page()
        list_url = self.config.product_list_url

        try:
            logger.info(f"[1688] 打开列表页: {list_url}")
            await page.goto(list_url, wait_until="domcontentloaded",
                            timeout=self.config.timeout * 1000)
            try:
                await page.wait_for_selector(CARD_TITLE_SEL, timeout=15000)
            except Exception:
                logger.warning("[1688] 等待商品卡片超时")
            await page.wait_for_timeout(2000)

            page_index = 1
            visited_offer_ids = set()

            while not self._cancelled:
                # 获取当前页所有卡片标题
                titles = await page.evaluate("""() => {
                    const ps = document.querySelectorAll('p[title]');
                    return Array.from(ps).map(p => p.title).filter(t => t.length > 0);
                }""")

                logger.info(f"[1688] 第{page_index}页共 {len(titles)} 个商品")
                if not titles:
                    break

                # 逐个点击卡片
                for card_index in range(len(titles)):
                    if self._cancelled:
                        break

                    title = titles[card_index]

                    # 回到列表页（如果不在列表页）
                    if list_url not in page.url and "offerlist" not in page.url:
                        await page.goto(list_url, wait_until="domcontentloaded",
                                        timeout=self.config.timeout * 1000)
                        await page.wait_for_selector(CARD_TITLE_SEL, timeout=10000)
                        await page.wait_for_timeout(1500)
                        # 翻到对应页
                        for _ in range(page_index - 1):
                            next_btn = await self._find_next_btn(page)
                            if next_btn:
                                await next_btn.click()
                                await page.wait_for_selector(CARD_TITLE_SEL, timeout=10000)
                                await page.wait_for_timeout(1500)

                    # 找到对应卡片并点击
                    try:
                        cards = await page.query_selector_all(CARD_TITLE_SEL)
                        if card_index >= len(cards):
                            logger.warning(f"[1688] 卡片索引越界 {card_index}/{len(cards)}")
                            continue

                        # 点击卡片，等待新标签页打开
                        logger.info(f"[1688] 点击第{card_index+1}/{len(titles)}个: {title[:30]}")
                        
                        async with context.expect_page(timeout=10000) as new_page_info:
                            await cards[card_index].click()
                        
                        new_page = await new_page_info.value
                        try:
                            await new_page.wait_for_load_state("domcontentloaded", timeout=15000)
                        except Exception:
                            pass

                        # 等待window.context注入
                        try:
                            await page.wait_for_function(
                                "() => window.context && window.context.result",
                                timeout=10000
                            )
                        except Exception:
                            pass

                        # 提取offerId和数据
                        current_url = new_page.url
                        m = _RE_OFFER_ID.search(current_url)
                        if not m:
                            logger.warning(f"[1688] 无法从URL提取offerId: {current_url}")
                            await new_page.close()
                            continue

                        offer_id = m.group(1)
                        if offer_id in visited_offer_ids:
                            logger.info(f"[1688] offer={offer_id} 已爬过（本轮），跳过")
                            await new_page.close()
                        else:
                            visited_offer_ids.add(offer_id)
                            # 等待skuProps出现在HTML中（数据加载完成）
                            data_ready = False
                            for _wait_round in range(3):
                                try:
                                    await new_page.wait_for_function(
                                        r"""() => /skuProps|"subject"\s*:\s*"/.test(document.documentElement.innerHTML)""",
                                        timeout=8000
                                    )
                                    data_ready = True
                                    break
                                except Exception:
                                    logger.debug(f"[1688] offer={offer_id} 第{_wait_round+1}轮等待数据超时，重试...")
                                    try:
                                        await new_page.reload(wait_until="domcontentloaded", timeout=15000)
                                        await new_page.wait_for_timeout(3000)
                                    except Exception:
                                        pass
                            
                            if not data_ready:
                                logger.warning(f"[1688] offer={offer_id} 数据未加载完成，跳过")
                                await new_page.close()
                                continue
                            
                            # 额外等待确保JS渲染完成
                            await new_page.wait_for_timeout(2000)
                            
                            html  = await new_page.content()
                            items = _extract_detail(html, offer_id, self.config.id)

                            # 在关闭标签页之前下载图片（页面还开着，Cookie有效）
                            for item in items:
                                if item.get("image_url"):
                                    try:
                                        ext = ".jpg"
                                        mm = re.search(r'\.(jpg|jpeg|png|webp)', item["image_url"], re.IGNORECASE)
                                        if mm:
                                            ext = "." + mm.group(1).lower()
                                        # 用image_url的hash做文件名，避免不同SKU中文去掉后同名
                                        fname_base = str(abs(hash(item["image_url"])))[:20]
                                        fname = f"{offer_id}_{fname_base}{ext}"
                                        fpath = os.path.join(self.images_dir, fname)
                                        if not os.path.exists(fpath):
                                            resp = await new_page.request.get(
                                                item["image_url"],
                                                headers={"Referer": "https://detail.1688.com/"},
                                                timeout=20000
                                            )
                                            if resp.status == 200:
                                                with open(fpath, "wb") as f:
                                                    f.write(await resp.body())
                                        item["image_local"] = f"images/1688_{self.config.id}/{fname}"
                                    except Exception as img_e:
                                        logger.debug(f"[1688] 图片下载失败: {img_e}")
                                        item["image_local"] = ""
                                else:
                                    item["image_local"] = ""

                            await new_page.close()  # 下载完再关闭
                            all_items.extend(items)
                            self._save_items(items)  # 增量写库
                            self._mark_crawled(items)  # 加入已爬集合
                            logger.info(f"[1688] offer={offer_id} 提取到 {len(items)} 条SKU")

                    except Exception as e:
                        logger.warning(f"[1688] 卡片 [{title[:20]}] 处理失败: {e}")
                        self.stats["errors"] += 1
                        # 关闭可能残留的新标签页
                        try:
                            for p in context.pages:
                                if p != page and "offerlist" not in p.url:
                                    await p.close()
                        except Exception:
                            pass
                        continue

                    await asyncio.sleep(self.config.request_delay)

                # 当前页全部爬完，找下一页
                self.stats["pages_crawled"] += 1
                next_btn = await self._find_next_btn(page)
                if not next_btn:
                    logger.info("[1688] 无下一页，爬取完成")
                    break

                await next_btn.click()
                await page.wait_for_selector(CARD_TITLE_SEL, timeout=10000)
                await page.wait_for_timeout(2000)
                page_index += 1
                logger.info(f"[1688] 翻到第{page_index}页")

        except Exception as e:
            logger.error(f"[1688] 爬取过程异常: {e}")
        finally:
            await page.close()

        return all_items

    async def _find_next_btn(self, page):
        """找下一页按钮"""
        try:
            # 1688旺铺翻页：找文字含"下一页"的button，且不是disabled状态
            btns = await page.query_selector_all("button")
            for btn in btns:
                text = await btn.inner_text()
                is_disabled = await btn.get_attribute("disabled")
                style = await btn.get_attribute("style") or ""
                # 颜色是灰色(204,204,204)说明是disabled状态
                if "下一页" in text and is_disabled is None and "204, 204, 204" not in style:
                    return btn
        except Exception:
            pass
        return None

    # ── 主入口 ────────────────────────────────────────────────────────────────

    async def run(self):
        from .spider import ProductItem

        self.stats["start_time"] = datetime.now()
        logger.info(f"[1688] 开始爬取（单标签页CDP模式）: {self.config.name}")

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("[1688] 未安装 Playwright")
            return []

        cdp_url  = self._cdp_url()
        products: list[ProductItem] = []

        async with async_playwright() as p:
            try:
                logger.info(f"[1688] 连接CDP: {cdp_url}")
                browser = await p.chromium.connect_over_cdp(cdp_url)
                logger.info(f"[1688] CDP连接成功")
            except Exception as e:
                logger.error(
                    f"[1688] CDP连接失败: {e}\n"
                    f"请先用调试模式启动Chrome:\n"
                    f'"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" '
                    f'--remote-debugging-port=9222 --user-data-dir="C:\\chrome-debug"'
                )
                return []

            context = browser.contexts[0] if browser.contexts else await browser.new_context()

            # 根据页面类型选择爬取策略
            if self._is_factory_page():
                logger.info("[1688] 检测到工厂直供页，使用无限滚动模式")
                raw_items = await self._crawl_factory_page(context)
            else:
                logger.info("[1688] 检测到旺铺列表页，使用翻页按钮模式")
                # 单标签页爬取所有商品（图片在详情页打开时同步下载）
                raw_items = await self._crawl_with_single_page(context)

            logger.info(f"[1688] 共提取 {len(raw_items)} 条原始数据")

            # 如果没有增量写库回调，则在此时一次性组装（原逻辑）
            if not self.on_item_saved:
                for item in raw_items:
                    if self._cancelled:
                        break
                    products.append(ProductItem(
                        name             = item["name"],
                        price            = item["price"],
                        sku              = item["sku"],
                        image_url        = item["image_url"],
                        image_local_path = item.get("image_local", ""),
                        product_url      = item["product_url"],
                        supplier_id      = self.config.id,
                        currency         = "CNY",
                    ))
                self.stats["products_found"] = len(products)
            else:
                # 增量写库模式：数据已在_save_items中写库，这里仅组装返回值供幂等upsert
                for item in raw_items:
                    if self._cancelled:
                        break
                    products.append(ProductItem(
                        name             = item["name"],
                        price            = item["price"],
                        sku              = item["sku"],
                        image_url        = item["image_url"],
                        image_local_path = item.get("image_local", ""),
                        product_url      = item["product_url"],
                        supplier_id      = self.config.id,
                        currency         = "CNY",
                    ))

        self.stats["end_time"] = datetime.now()
        duration = (self.stats["end_time"] - self.stats["start_time"]).seconds
        logger.info(
            f"[1688] 完成 | 商品:{len(products)} "
            f"耗时:{duration}s 错误:{self.stats['errors']}"
        )
        return products
