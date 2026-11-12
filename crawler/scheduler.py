"""
supplier_crawler/crawler/scheduler.py
定时任务调度器
"""
import asyncio
import json
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .spider import SupplierConfig, SupplierSpider

logger = logging.getLogger(__name__)


def _is_alibaba1688(supplier: dict) -> bool:
    """判断供应商是否是1688旺铺类型"""
    selectors = supplier.get("selectors") or {}
    if isinstance(selectors, str):
        try:
            selectors = json.loads(selectors)
        except Exception:
            selectors = {}
    return selectors.get("type") == "alibaba1688"


def _is_wc_store(supplier: dict) -> bool:
    """判断供应商是否是 WooCommerce Store API 类型"""
    selectors = supplier.get("selectors") or {}
    if isinstance(selectors, str):
        try:
            selectors = json.loads(selectors)
        except Exception:
            selectors = {}
    stype = selectors.get("type", "")
    return (
        stype in ("wc_store", "wc_store_api", "woocommerce")
        or "wp-json/wc/store" in (supplier.get("list_url") or "")
        or "bellacentral" in (supplier.get("base_url") or "")
    )


def _is_tiendanube(supplier: dict) -> bool:
    """判断供应商是否是 Tiendanube (Nuvemshop) 平台类型，如 OSA"""
    selectors = supplier.get("selectors") or {}
    if isinstance(selectors, str):
        try:
            selectors = json.loads(selectors)
        except Exception:
            selectors = {}
    stype = selectors.get("type", "")
    base_url = (supplier.get("base_url") or "").lower()
    name = (supplier.get("name") or "").lower()
    return (
        stype in ("tiendanube", "nuvemshop")
        or "osadistribuidora" in base_url
        or name == "osa"
    )


def _is_modapoint(supplier: dict) -> bool:
    """判断供应商是否是 Moda Point (PrestaShop) 平台类型"""
    selectors = supplier.get("selectors") or {}
    if isinstance(selectors, str):
        try:
            selectors = json.loads(selectors)
        except Exception:
            selectors = {}
    stype = selectors.get("type", "")
    base_url = (supplier.get("base_url") or "").lower()
    name = (supplier.get("name") or "").lower()
    return (
        stype in ("modapoint", "prestashop")
        or "modapoint" in base_url
        or "modapoint" in name
    )


def _is_smartycart(supplier: dict) -> bool:
    """判断供应商是否显式启用 SmartyCart 专用异步爬虫"""
    selectors = supplier.get("selectors") or {}
    if isinstance(selectors, str):
        try:
            selectors = json.loads(selectors)
        except Exception:
            selectors = {}
    stype = selectors.get("type", "")
    sid = supplier.get("id")
    name = (supplier.get("name") or "").lower()
    # 明确保留 benabi (4) 和 Trapoman (3) 的既有爬虫行为
    if sid in (3, 4) or name in ("benabi", "trapoman"):
        return False
    return (
        stype == "smartycart"
        or "nativo" in name
        or "randy" in name
    )


class CrawlerScheduler:
    def __init__(self, db_manager):
        self.db = db_manager
        self.scheduler = AsyncIOScheduler(timezone="UTC")
        self.running_tasks: dict[int, asyncio.Task] = {}

    def _build_config(self, supplier: dict) -> SupplierConfig:
        selectors = supplier.get("selectors") or {}
        if isinstance(selectors, str):
            try:
                selectors = json.loads(selectors)
            except Exception:
                selectors = {}
        return SupplierConfig(
            id=supplier["id"],
            name=supplier["name"],
            base_url=supplier["base_url"],
            product_list_url=supplier["list_url"],
            selectors=selectors,
            use_js_render=bool(supplier.get("use_js", 0)),
            use_chrome_cookies=bool(supplier.get("use_chrome_cookies", 0)),
            request_delay=float(supplier.get("request_delay") or 1.5),
        )

    def _make_spider(self, supplier: dict, config: SupplierConfig, log_id: int):
        """
        根据供应商类型返回对应的爬虫实例。
        1688旺铺          → Alibaba1688Spider
        WooCommerce Store → WooCommerceStoreSpider
        Tiendanube (OSA)  → TiendanubeSpider
        其他              → SupplierSpider（原有）
        """
        if _is_alibaba1688(supplier):
            from .alibaba1688_spider import Alibaba1688Spider
            logger.info(f"[{supplier['name']}] 使用 Alibaba1688Spider")
            return Alibaba1688Spider(config, self.db, log_id=log_id)
        if _is_wc_store(supplier):
            from .wc_store_spider import WooCommerceStoreSpider
            logger.info(f"[{supplier['name']}] 使用 WooCommerceStoreSpider")
            return WooCommerceStoreSpider(config, self.db, log_id=log_id)
        if _is_tiendanube(supplier):
            from .tiendanube_spider import TiendanubeSpider
            logger.info(f"[{supplier['name']}] 使用 TiendanubeSpider (极速异步模式)")
            return TiendanubeSpider(config, self.db, log_id=log_id)
        if _is_modapoint(supplier):
            from .modapoint_spider import ModaPointSpider
            logger.info(f"[{supplier['name']}] 使用 ModaPointSpider (PrestaShop 极速异步模式)")
            return ModaPointSpider(config, self.db, log_id=log_id)
        if _is_smartycart(supplier):
            from .smartycart_spider import SmartyCartSpider
            logger.info(f"[{supplier['name']}] 使用 SmartyCartSpider (SmartyCart 分类树异步模式)")
            return SmartyCartSpider(config, self.db, log_id=log_id)
        return SupplierSpider(config, self.db, log_id=log_id)

    async def run_supplier(self, supplier_id: int):
        """运行单个供应商爬虫，含日志记录"""
        suppliers = self.db.get_all_suppliers()
        supplier = next((s for s in suppliers if s["id"] == supplier_id), None)
        if not supplier:
            logger.error(f"供应商 ID={supplier_id} 不存在")
            return

        log_id = self.db.create_crawl_log(supplier_id)
        config = self._build_config(supplier)
        spider = self._make_spider(supplier, config, log_id)

        try:
            # 增量写库回调：每爬完一个offer立即写库，防止中断丢数据
            def on_item_saved(items):
                return self.db.bulk_upsert_products(items)
            spider.on_item_saved = on_item_saved

            products = await spider.run()
            saved = self.db.bulk_upsert_products(products)
            # 标记缺失商品
            missing_count = self.db.mark_missing_products(supplier_id, products)
            missing_msg = ""
            if missing_count == -1:
                missing_msg = "（爬取不完整，跳过缺失标记）"
            elif missing_count > 0:
                missing_msg = f"，标记缺失{missing_count}条"
            self.db.finish_crawl_log(
                log_id, "success",
                spider.stats["pages_crawled"],
                saved,
                spider.stats["errors"],
                f"成功入库 {saved} 条商品，共爬取 {spider.stats['pages_crawled']} 页{missing_msg}"
            )
            logger.info(f"[{supplier['name']}] 完成，入库 {saved} 条{missing_msg}")
        except asyncio.CancelledError:
            self.db.finish_crawl_log(
                log_id, "paused",
                spider.stats["pages_crawled"],
                spider.stats["products_found"],
                spider.stats["errors"],
                f"手动停止，已增量入库 {spider.stats['products_found']} 条"
            )
            logger.info(f"[{supplier['name']}] 任务已取消，已入库 {spider.stats['products_found']} 条")
        except Exception as e:
            logger.exception(f"[{supplier['name']}] 爬取失败")
            self.db.finish_crawl_log(
                log_id, "failed",
                spider.stats.get("pages_crawled", 0),
                spider.stats.get("products_found", 0),
                1, str(e)[:500]
            )
        finally:
            self.running_tasks.pop(supplier_id, None)

    async def run_all(self):
        suppliers = self.db.get_all_suppliers()
        tasks = []
        for s in suppliers:
            if s["id"] not in self.running_tasks:
                task = asyncio.create_task(self.run_supplier(s["id"]))
                self.running_tasks[s["id"]] = task
                tasks.append(task)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def schedule_supplier(self, supplier_id: int, cron_expr: str = "0 2 * * *"):
        try:
            parts = cron_expr.strip().split()
            if len(parts) != 5:
                raise ValueError(f"无效cron表达式: {cron_expr}")
            trigger = CronTrigger(
                minute=parts[0], hour=parts[1],
                day=parts[2], month=parts[3], day_of_week=parts[4]
            )
            self.scheduler.add_job(
                self.run_supplier, trigger=trigger,
                args=[supplier_id],
                id=f"supplier_{supplier_id}",
                replace_existing=True,
            )
            logger.info(f"供应商 {supplier_id} 定时任务: {cron_expr}")
        except Exception as e:
            logger.error(f"设置定时任务失败: {e}")

    def start(self):
        self.scheduler.start()
        logger.info("调度器已启动")

    def stop(self):
        try:
            self.scheduler.shutdown(wait=False)
        except Exception:
            pass
