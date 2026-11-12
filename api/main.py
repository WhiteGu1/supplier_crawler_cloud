"""
supplier_crawler/api/main.py
FastAPI 后端 API
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import DatabaseManager
from crawler.scheduler import CrawlerScheduler

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("crawler.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)

# 压制底层库的噪音日志
for _noisy in ("pdfminer", "pdfplumber", "PIL", "urllib3", "asyncio", "multipart"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)

app = FastAPI(title="供应商爬虫管理系统", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os
images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
app.mount("/images", StaticFiles(directory=images_dir), name="images")
_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=_frontend_dir), name="static")

db: DatabaseManager = None
scheduler: CrawlerScheduler = None


# ── Pydantic 模型 ────────────────────────────────────────────
class SupplierCreate(BaseModel):
    name: str
    base_url: str
    list_url: str
    selectors: Optional[dict] = None
    use_js: bool = False
    use_chrome_cookies: bool = False
    request_delay: float = 1.5
    cron_expr: str = "0 2 * * *"
    price_adjustment: float = 0.0
    missing_threshold: int = 80

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    list_url: Optional[str] = None
    selectors: Optional[dict] = None
    use_js: Optional[bool] = None
    use_chrome_cookies: Optional[bool] = None
    request_delay: Optional[float] = None
    is_active: Optional[bool] = None
    cron_expr: Optional[str] = None
    price_adjustment: Optional[float] = None
    missing_threshold: Optional[int] = None

class ProductBatchDelete(BaseModel):
    ids: List[int]

class CartItemAdd(BaseModel):
    product_id: Optional[int] = None
    sku: Optional[str] = None
    quantity: int = 1
    mode: str = "add"

class CartItemUpdate(BaseModel):
    quantity: int

class CartBatchAdd(BaseModel):
    items: Optional[List[dict]] = None
    text: Optional[str] = None

class CartSyncRequest(BaseModel):
    auto_adjust: bool = True
    session_cookies: Optional[str] = None
    product_ids: Optional[List[int]] = None

class CartValidateRequest(BaseModel):
    auto_fix: bool = False
    supplier_id: Optional[int] = None


# ── 仪表盘 ──────────────────────────────────────────────────
@app.get("/api/dashboard")
async def get_dashboard():
    try:
        return db.get_dashboard_stats()
    except Exception as e:
        raise HTTPException(500, str(e))


# ── 供应商 ──────────────────────────────────────────────────
@app.get("/api/suppliers")
async def list_suppliers():
    return db.get_all_suppliers()

@app.post("/api/suppliers", status_code=201)
async def create_supplier(data: SupplierCreate):
    sid = db.upsert_supplier(
        name=data.name, base_url=data.base_url, list_url=data.list_url,
        selectors=data.selectors, use_js=data.use_js,
        use_chrome_cookies=data.use_chrome_cookies,
        request_delay=data.request_delay, cron_expr=data.cron_expr,
        price_adjustment=data.price_adjustment,
        missing_threshold=data.missing_threshold,
    )
    scheduler.schedule_supplier(sid, data.cron_expr)
    return {"id": sid, "message": "供应商添加成功"}

@app.put("/api/suppliers/{supplier_id}")
async def update_supplier(supplier_id: int, data: SupplierUpdate):
    updates = {}
    if data.name         is not None: updates["name"]          = data.name
    if data.base_url     is not None: updates["base_url"]       = data.base_url
    if data.list_url     is not None: updates["list_url"]       = data.list_url
    if data.selectors    is not None:
        # 保留数据库里已有的 type/cdp_url/manual_cookies 等特殊字段，防止前端表单覆盖
        try:
            with db.connection() as _conn:
                _cur = _conn.cursor()
                _cur.execute("SELECT selectors FROM suppliers WHERE id=%s", (supplier_id,))
                _row = _cur.fetchone()
                _existing = json.loads(_row[0]) if _row and _row[0] else {}
        except Exception:
            _existing = {}
        _new_sel = data.selectors
        for _keep_key in ("type", "cdp_url", "manual_cookies", "api_url"):
            if _keep_key not in _new_sel and _keep_key in _existing:
                _new_sel[_keep_key] = _existing[_keep_key]
        updates["selectors"] = json.dumps(_new_sel, ensure_ascii=False)
    if data.use_js       is not None: updates["use_js"]         = int(data.use_js)
    if data.use_chrome_cookies is not None: updates["use_chrome_cookies"] = int(data.use_chrome_cookies)
    if data.request_delay is not None: updates["request_delay"] = data.request_delay
    if data.is_active    is not None: updates["is_active"]      = int(data.is_active)
    if data.cron_expr    is not None: updates["cron_expr"]      = data.cron_expr
    if data.price_adjustment is not None: updates["price_adjustment"] = data.price_adjustment
    if data.missing_threshold is not None: updates["missing_threshold"] = data.missing_threshold

    if not updates:
        raise HTTPException(400, "没有要更新的字段")

    fields = ", ".join(f"{k}=%s" for k in updates)
    params = list(updates.values()) + [supplier_id]
    with db.connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE suppliers SET {fields} WHERE id=%s", params)

    if data.cron_expr:
        scheduler.schedule_supplier(supplier_id, data.cron_expr)
    return {"message": "更新成功"}

@app.delete("/api/suppliers/{supplier_id}")
async def delete_supplier(supplier_id: int):
    with db.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE suppliers SET is_active=0 WHERE id=%s", (supplier_id,))
    return {"message": "已禁用"}


# ── 爬虫控制 ────────────────────────────────────────────────
@app.post("/api/crawl/start/{supplier_id}")
async def start_crawl(supplier_id: int):
    if supplier_id in scheduler.running_tasks:
        raise HTTPException(409, "该供应商爬虫正在运行中")
    task = asyncio.create_task(scheduler.run_supplier(supplier_id))
    scheduler.running_tasks[supplier_id] = task
    return {"message": "已启动"}

@app.post("/api/crawl/stop/{supplier_id}")
async def stop_crawl(supplier_id: int):
    task = scheduler.running_tasks.get(supplier_id)
    if task and not task.done():
        task.cancel()
        await asyncio.sleep(0.1)
    scheduler.running_tasks.pop(supplier_id, None)
    return {"message": "已停止"}

@app.post("/api/crawl/start-all")
async def start_all_crawl(background_tasks: BackgroundTasks):
    background_tasks.add_task(scheduler.run_all)
    return {"message": "全量爬取已启动"}

@app.get("/api/crawl/status")
async def crawl_status():
    # 清理已完成的任务
    done = [sid for sid, t in scheduler.running_tasks.items() if t.done()]
    for sid in done:
        scheduler.running_tasks.pop(sid, None)
    return {"running": list(scheduler.running_tasks.keys())}


# ── 日志 ────────────────────────────────────────────────────
@app.get("/api/crawl-logs")
async def get_crawl_logs(limit: int = 100):
    with db.connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT cl.*, s.name as supplier_name
            FROM crawl_logs cl JOIN suppliers s ON cl.supplier_id=s.id
            ORDER BY cl.started_at DESC LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
    for r in rows:
        for f in ("started_at", "finished_at"):
            if isinstance(r.get(f), datetime):
                r[f] = r[f].strftime("%Y-%m-%d %H:%M:%S")
    return rows


# ── 商品 ────────────────────────────────────────────────────
@app.get("/api/products")
async def list_products(
    supplier_id: Optional[int] = None,
    category: Optional[str] = None,
    category_prefix: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    product_ids: Optional[str] = None,
    include_missing: bool = False,
):
    # category=__none__ 表示筛选无分类商品
    cat = category if category and category.strip() else None
    cat_prefix = category_prefix if category_prefix and category_prefix.strip() else None
    # 批量按ID查询
    if product_ids:
        ids = [int(x) for x in product_ids.split(',') if x.strip().isdigit()]
        rows = db.get_products_by_ids(ids)
        return {"total": len(rows), "page": 1, "page_size": len(rows), "data": rows}

    return db.get_products(
        supplier_id=supplier_id,
        category=cat,
        category_prefix=cat_prefix,
        no_category=(cat == '__none__'),
        keyword=keyword, page=page, page_size=page_size,
        sort=sort, min_price=min_price, max_price=max_price,
        include_missing=include_missing,
    )

# 注意：分类接口必须在 {product_id} 之前声明，否则会被匹配为 product_id="categories"
@app.get("/api/products/categories")
async def get_categories(supplier_id: Optional[int] = None):
    with db.connection() as conn:
        cursor = conn.cursor(dictionary=True)
        if supplier_id:
            cursor.execute(
                """SELECT DISTINCT category FROM (
                    SELECT category FROM products WHERE supplier_id=%s AND category!='' AND is_available=1
                    UNION
                    SELECT pc.category FROM product_categories pc
                    JOIN products p ON pc.product_id=p.id
                    WHERE p.supplier_id=%s AND p.is_available=1 AND pc.category!=''
                ) t ORDER BY category""",
                (supplier_id, supplier_id)
            )
        else:
            cursor.execute(
                """SELECT DISTINCT category FROM (
                    SELECT category FROM products WHERE category!='' AND is_available=1
                    UNION
                    SELECT category FROM product_categories WHERE category!=''
                ) t ORDER BY category"""
            )
        return [r["category"] for r in cursor.fetchall()]


# ── 导出Excel（含嵌入图片） ───────────────────────────────────
@app.get("/api/products/export-xlsx")
async def export_xlsx(
    supplier_id: Optional[int] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
):
    """导出商品为xlsx，图片列嵌入真实图片"""
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _do_export_xlsx_sync, supplier_id, category, keyword)
    except Exception as e:
        logger.exception(f"导出xlsx失败: {e}")
        raise HTTPException(500, f"导出失败: {str(e)}")

def _do_export_xlsx_sync(supplier_id, category, keyword):
    import requests as req_lib  # 保留备用
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.drawing.image import Image as XLImage
    from openpyxl.utils import get_column_letter
    from PIL import Image as PILImage
    import io as _io
    from fastapi.responses import StreamingResponse

    # 获取所有商品（最多5000条）
    cat = category if category and category.strip() else None
    result = db.get_products(
        supplier_id=supplier_id,
        category=cat,
        no_category=(cat == '__none__'),
        keyword=keyword,
        page=1, page_size=5000,
    )
    products = result.get("data", [])

    # 获取供应商价格修正
    with db.connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, price_adjustment FROM suppliers")
        adj_map = {r["id"]: float(r["price_adjustment"] or 0) for r in cursor.fetchall()}

    wb = Workbook()
    ws = wb.active
    ws.title = "商品数据"

    # 表头
    headers = ["图片", "商品名称", "SKU", "分类", "供应商", "价格", "商品URL", "更新时间"]
    header_fill = PatternFill("solid", start_color="1F2937")
    header_font = Font(bold=True, color="00D4AA", name="Arial", size=11)
    thin = Side(style="thin", color="30363D")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border

    ws.row_dimensions[1].height = 22

    # 图片列宽 + 其他列宽
    col_widths = [18, 50, 20, 25, 15, 12, 40, 18]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    IMG_H = 150  # 行高（像素等效点）
    IMG_PX = 200  # 图片尺寸

    images_base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")

    for row_idx, p in enumerate(products, 2):
        ws.row_dimensions[row_idx].height = IMG_H * 0.75

        adj = adj_map.get(p.get("supplier_id"), 0)
        price = float(p.get("price", 0)) * (1 + adj / 100)

        # 尝试嵌入图片
        img_inserted = False
        img_local = p.get("image_local", "")
        img_url = p.get("image_url", "")

        if img_local:
            rel = img_local.replace("\\", "/")
            if rel.startswith("/images/"):
                rel = rel[len("/images/"):]
            elif rel.startswith("images/"):
                rel = rel[len("images/"):]
            local_path = os.path.join(images_base, rel)
            try:
                if os.path.exists(local_path):
                    pil_img = PILImage.open(local_path).convert("RGB")
                    img_buf = _io.BytesIO()
                    pil_img.save(img_buf, format="JPEG", quality=95)
                    img_buf.seek(0)
                    xl_img = XLImage(img_buf)
                    xl_img.width  = IMG_PX
                    xl_img.height = IMG_PX
                    ws.add_image(xl_img, f"A{row_idx}")
                    img_inserted = True
            except Exception as e:
                logger.debug(f"嵌入本地图片失败: {e}")
        # 远程图片不下载（避免超时导致导出失败）

        # 填写其他列
        row_data = [
            "",  # A: 图片占位
            p.get("name", ""),
            p.get("sku", ""),
            p.get("category", ""),
            p.get("supplier_name", ""),
            round(price, 2),
            p.get("product_url", ""),
            str(p.get("updated_at", ""))[:16],
        ]
        for col_idx, val in enumerate(row_data, 1):
            if col_idx == 1:
                continue  # 图片列不写文字
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.alignment = Alignment(vertical="center", wrap_text=(col_idx == 2))
            cell.border = border
            cell.font = Font(name="Arial", size=10)
            if col_idx == 6:
                cell.font = Font(name="Arial", size=11, bold=True, color="F59E0B")

    # 冻结首行
    ws.freeze_panes = "A2"

    # 保存到项目目录下的临时文件
    import uuid
    export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
    os.makedirs(export_dir, exist_ok=True)
    suffix = f"_{category.replace(' > ', '-')}" if category and category != "__none__" else ""
    fname = f"products{suffix}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    tmp_path = os.path.join(export_dir, f"_export_{uuid.uuid4().hex}.xlsx")
    wb.save(tmp_path)

    return FileResponse(
        tmp_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=fname,
        background=None,
    )


# ── 分类CSV导入 ───────────────────────────────────────────────
@app.post("/api/products/import-categories")
async def import_categories(file: UploadFile = File(...)):
    """上传CSV，按SKU或商品名批量覆盖分类"""
    import csv, io, chardet

    content = await file.read()

    # 自动检测编码
    detected = chardet.detect(content[:4096])
    encoding = detected.get('encoding') or 'utf-8'
    try:
        text = content.decode(encoding)
    except Exception:
        text = content.decode('gbk', errors='replace')

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise HTTPException(400, "CSV文件为空")

    # 识别列头（兼容中英文）
    headers = list(rows[0].keys())
    def find_col(patterns):
        for h in headers:
            for p in patterns:
                if p.lower() in h.lower():
                    return h
        return None

    col_cat  = find_col(['分类', 'category', 'cat'])
    col_sku  = find_col(['sku', '货号', '编号', 'code'])
    col_name = find_col(['商品名称', '名称', '品名', 'name'])

    if not col_cat:
        raise HTTPException(400, f"未找到分类列，现有列头: {headers}")
    if not col_sku and not col_name:
        raise HTTPException(400, f"未找到SKU或名称列，现有列头: {headers}")

    updated = skipped = errors = 0
    with db.connection() as conn:
        cursor = conn.cursor(buffered=True)
        for row in rows:
            cat = (row.get(col_cat) or '').strip()
            sku  = (row.get(col_sku)  or '').strip() if col_sku  else ''
            name = (row.get(col_name) or '').strip() if col_name else ''

            if not cat:
                skipped += 1
                continue

            try:
                # 优先按SKU匹配，其次按名称
                if sku:
                    cursor.execute(
                        "SELECT id FROM products WHERE sku=%s AND sku!='' LIMIT 1", (sku,)
                    )
                    r = cursor.fetchone()
                    if not r and name:
                        cursor.execute(
                            "SELECT id FROM products WHERE name=%s LIMIT 1", (name,)
                        )
                        r = cursor.fetchone()
                elif name:
                    cursor.execute(
                        "SELECT id FROM products WHERE name=%s LIMIT 1", (name,)
                    )
                    r = cursor.fetchone()
                else:
                    skipped += 1
                    continue

                if r:
                    cursor.execute(
                        "UPDATE products SET category=%s, updated_at=NOW() WHERE id=%s",
                        (cat, r[0])
                    )
                    updated += 1
                else:
                    skipped += 1
            except Exception as e:
                errors += 1
                logger.error(f"分类更新失败 sku={sku} name={name}: {e}")

    return {
        "message": f"分类更新完成：更新{updated}条，跳过{skipped}条，错误{errors}条",
        "updated": updated, "skipped": skipped, "errors": errors
    }

@app.get("/api/products/new")
async def get_new_products(supplier_id: Optional[int] = None, page: int = 1, page_size: int = 20):
    """获取新商品（原有供应商最近新增的）"""
    conditions = ["p.is_available=1", "p.is_new=1"]
    params = []
    if supplier_id:
        conditions.append("p.supplier_id=%s"); params.append(supplier_id)
    where = "WHERE " + " AND ".join(conditions)
    offset = (page - 1) * page_size
    with db.connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT COUNT(*) as total FROM products p {where}", params)
        total = cursor.fetchone()["total"]
        cursor.execute(
            f"""SELECT p.*, s.name as supplier_name
                FROM products p JOIN suppliers s ON p.supplier_id=s.id
                {where} ORDER BY p.created_at DESC LIMIT %s OFFSET %s""",
            params + [page_size, offset]
        )
        rows = cursor.fetchall()
    from datetime import datetime
    for r in rows:
        for f in ("created_at", "updated_at"):
            if isinstance(r.get(f), datetime): r[f] = r[f].strftime("%Y-%m-%d %H:%M:%S")
    return {"total": total, "page": page, "page_size": page_size, "data": rows}

@app.post("/api/products/new/clear")
async def clear_new_products(supplier_id: Optional[int] = None):
    """清空新商品标记"""
    with db.connection() as conn:
        cursor = conn.cursor()
        if supplier_id:
            cursor.execute("UPDATE products SET is_new=0 WHERE supplier_id=%s", (supplier_id,))
        else:
            cursor.execute("UPDATE products SET is_new=0")
    return {"message": "已清空新商品标记"}


@app.get("/api/products/missing")
async def get_missing_products(supplier_id: Optional[int] = None, page: int = 1, page_size: int = 20):
    """获取缺失商品（上次爬取中未出现的商品）"""
    conditions = ["p.is_available=1", "p.is_missing=1"]
    params = []
    if supplier_id:
        conditions.append("p.supplier_id=%s"); params.append(supplier_id)
    where = "WHERE " + " AND ".join(conditions)
    offset = (page - 1) * page_size
    with db.connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT COUNT(*) as total FROM products p {where}", params)
        total = cursor.fetchone()["total"]
        cursor.execute(
            f"""SELECT p.*, s.name as supplier_name
                FROM products p JOIN suppliers s ON p.supplier_id=s.id
                {where} ORDER BY p.updated_at DESC LIMIT %s OFFSET %s""",
            params + [page_size, offset]
        )
        rows = cursor.fetchall()
    from datetime import datetime
    for r in rows:
        for f in ("created_at", "updated_at"):
            if isinstance(r.get(f), datetime): r[f] = r[f].strftime("%Y-%m-%d %H:%M:%S")
    return {"total": total, "page": page, "page_size": page_size, "data": rows}

@app.post("/api/products/missing/clear")
async def clear_missing_products(supplier_id: Optional[int] = None):
    """清空缺失标记"""
    with db.connection() as conn:
        cursor = conn.cursor()
        if supplier_id:
            cursor.execute("UPDATE products SET is_missing=0 WHERE supplier_id=%s", (supplier_id,))
        else:
            cursor.execute("UPDATE products SET is_missing=0")
    return {"message": "已清空缺失标记"}


@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    with db.connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, s.name as supplier_name
            FROM products p LEFT JOIN suppliers s ON s.id = p.supplier_id
            WHERE p.id = %s
        """, (product_id,))
        row = cursor.fetchone()
    if not row:
        raise HTTPException(404, "商品不存在")
    return row

@app.get("/api/products/{product_id}/price-history")
async def get_price_history(product_id: int, days: int = 30):
    return db.get_price_history(product_id, days)

@app.put("/api/products/{product_id}/category")
async def update_product_category(product_id: int, data: dict):
    """设置商品的分类（单分类模式，兼容旧接口）
    会覆盖该商品的所有分类为这一个"""
    category = (data.get("category") or "").strip()
    with db.connection() as conn:
        cursor = conn.cursor()
        # 更新 products.category 字段（兼容旧查询）
        cursor.execute(
            "UPDATE products SET category=%s, updated_at=NOW() WHERE id=%s",
            (category, product_id)
        )
        # 清除旧的多分类记录，写入新的
        cursor.execute("DELETE FROM product_categories WHERE product_id=%s", (product_id,))
        if category:
            cursor.execute(
                "INSERT INTO product_categories (product_id, category) VALUES (%s, %s)",
                (product_id, category)
            )
        conn.commit()
    return {"message": "分类已更新"}

@app.get("/api/products/{product_id}/categories")
async def get_product_categories(product_id: int):
    """获取商品的所有分类路径（全部并列，无主次）"""
    with db.connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT category FROM product_categories WHERE product_id=%s ORDER BY id",
            (product_id,)
        )
        return cursor.fetchall()

@app.post("/api/products/{product_id}/categories")
async def add_product_category(product_id: int, data: dict):
    """给商品添加一个分类路径"""
    category = (data.get("category") or "").strip()
    if not category:
        raise HTTPException(400, "分类不能为空")
    with db.connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT IGNORE INTO product_categories (product_id, category) VALUES (%s, %s)",
            (product_id, category)
        )
        # 同步到 products.category（如果当前为空，写入第一个）
        cursor.execute("SELECT category FROM products WHERE id=%s", (product_id,))
        row = cursor.fetchone()
        if row and not row[0]:
            cursor.execute(
                "UPDATE products SET category=%s, updated_at=NOW() WHERE id=%s",
                (category, product_id)
            )
        conn.commit()
    return {"message": "分类已添加"}

@app.delete("/api/products/{product_id}/categories/{category_path}")
async def remove_product_category(product_id: int, category_path: str):
    """删除商品的某个分类路径"""
    from urllib.parse import unquote
    category = unquote(category_path).strip()
    with db.connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM product_categories WHERE product_id=%s AND category=%s",
            (product_id, category)
        )
        # 同步到 products.category：如果删的正好是 products.category 的值，换一个
        cursor.execute("SELECT category FROM products WHERE id=%s", (product_id,))
        row = cursor.fetchone()
        if row and row[0] == category:
            cursor.execute(
                "SELECT category FROM product_categories WHERE product_id=%s ORDER BY id LIMIT 1",
                (product_id,)
            )
            new_cat = cursor.fetchone()
            cursor.execute(
                "UPDATE products SET category=%s, updated_at=NOW() WHERE id=%s",
                (new_cat[0] if new_cat else '', product_id)
            )
        conn.commit()
    return {"message": "分类已删除"}


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    with db.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM price_history WHERE product_id=%s", (product_id,))
        cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    return {"message": "已删除"}

@app.post("/api/products/delete-batch")
async def delete_products_batch(data: ProductBatchDelete):
    if not data.ids:
        raise HTTPException(400, "未提供ID")
    placeholders = ",".join(["%s"] * len(data.ids))
    with db.connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM price_history WHERE product_id IN ({placeholders})", data.ids)
        cursor.execute(f"DELETE FROM products WHERE id IN ({placeholders})", data.ids)
    return {"message": f"已删除 {len(data.ids)} 条"}



# ── PDF 解析器插件系统 ────────────────────────────────────────
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from pdf_parsers import list_parsers, get_parser
except ImportError:
    from crawler.pdf_parsers import list_parsers, get_parser

@app.get("/api/pdf-parsers")
async def get_pdf_parsers():
    """列出所有可用的PDF解析器"""
    return list_parsers()

@app.post("/api/suppliers/{supplier_id}/import-pdf")
async def import_pdf(supplier_id: int, parser_id: str, file: UploadFile = File(...)):
    """上传PDF目录，用指定解析器解析后入库"""
    import tempfile

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "请上传PDF文件")

    suppliers = db.get_all_suppliers()
    if not any(s["id"] == supplier_id for s in suppliers):
        raise HTTPException(404, "供应商不存在")

    parser = get_parser(parser_id)
    if parser is None:
        raise HTTPException(400, f"未找到解析器: {parser_id}，请检查 pdf_parsers/ 目录")

    try:
        import pdfplumber  # noqa — 确保已安装
        from PIL import Image  # noqa
    except ImportError as e:
        raise HTTPException(500, f"缺少依赖: {e} — 请运行 pip install pdfplumber pillow")

    content_bytes = await file.read()
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(content_bytes)
        tmp_path = tmp.name

    try:
        # 调用解析器
        all_products = parser.parse(tmp_path, images_dir, supplier_id)

        # 入库
        inserted = updated = skipped = errors = 0
        with db.connection() as conn:
            cursor = conn.cursor(buffered=True)
            # 判断是否为原有供应商的新商品（供应商创建>24h且已有>100条商品）
            cursor.execute("""
                SELECT TIMESTAMPDIFF(HOUR, created_at, NOW()) > 24
                       AND (SELECT COUNT(*) FROM products WHERE supplier_id=%s AND is_available=1) > 100
                FROM suppliers WHERE id=%s
            """, (supplier_id, supplier_id))
            row_sup = cursor.fetchone()
            is_new_supplier = not (row_sup and row_sup[0])
            for p in all_products:
              try:
                # 优先按 SKU 查找，无 SKU 则按 name 查找
                if p.get("sku"):
                    cursor.execute(
                        "SELECT id, price, category, image_url FROM products WHERE supplier_id=%s AND sku=%s LIMIT 1",
                        (supplier_id, p["sku"])
                    )
                else:
                    cursor.execute(
                        "SELECT id, price, category, image_url FROM products WHERE supplier_id=%s AND name=%s LIMIT 1",
                        (supplier_id, p["name"])
                    )
                row = cursor.fetchone()
                if row:
                    prod_id, old_price, old_cat, old_img = row
                    # 优先保留已有细分层级分类
                    cat = old_cat if (old_cat and (not p.get("category") or len(old_cat) > len(p.get("category", "")))) else p.get("category", "")
                    img = p.get("image") or old_img or ""

                    if abs(float(old_price) - p["price"]) > 0.01:
                        cursor.execute(
                            "UPDATE products SET name=%s, price=%s, category=%s, image_url=%s, is_available=1, is_missing=0, updated_at=NOW() WHERE id=%s",
                            (p["name"], p["price"], cat, img, prod_id)
                        )
                        cursor.execute(
                            "INSERT INTO price_history (product_id, price, recorded_at) VALUES (%s, %s, NOW())",
                            (prod_id, p["price"])
                        )
                        updated += 1
                    else:
                        cursor.execute(
                            "UPDATE products SET name=%s, category=%s, image_url=%s, is_available=1, is_missing=0, updated_at=NOW() WHERE id=%s",
                            (p["name"], cat, img, prod_id)
                        )
                        skipped += 1
                else:
                    cursor.execute(
                        "INSERT INTO products (supplier_id, sku, name, price, category, image_url, is_available, is_new, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s,1,%s,NOW(),NOW())",
                        (supplier_id, p["sku"], p["name"], p["price"], p.get("category",""), p.get("image") or "", 0 if is_new_supplier else 1)
                    )
                    new_pid = cursor.lastrowid
                    if new_pid:
                        cursor.execute(
                            "INSERT INTO price_history (product_id, price, recorded_at) VALUES (%s, %s, NOW())",
                            (new_pid, p["price"])
                        )
                    inserted += 1
              except Exception as row_err:
                  errors += 1
                  logger.error(f"PDF入库失败 sku={p.get('sku')}: {row_err}")

        # ── 缺失标记：非最后一个导入日导入的商品全部标记为缺货商品 ──
        res_missing = db.mark_pdf_supplier_missing(supplier_id)
        marked_missing = res_missing["marked_missing"]
        logger.info(f"[PDF导入] 供应商{supplier_id}: 最后一个导入日={res_missing['latest_date']}，正常={res_missing['available_count']}条，标记缺货={marked_missing}条")

        return {"parsed": len(all_products), "inserted": inserted, "updated": updated, "skipped": skipped, "missing": marked_missing}

    finally:
        os.unlink(tmp_path)


@app.post("/api/suppliers/{supplier_id}/sync-pdf-missing")
async def sync_supplier_pdf_missing(supplier_id: int):
    """更新指定 PDF 导入店铺的缺货商品状态：非最后一个导入日导入的商品全部标记为缺货"""
    try:
        res = db.mark_pdf_supplier_missing(supplier_id)
        return {
            "success": True,
            "data": res,
            "message": f"供应商 {supplier_id} 已更新：最后导入日 {res['latest_date']}，正常 {res['available_count']} 条，缺货 {res['marked_missing']} 条"
        }
    except Exception as e:
        logger.error(f"同步供应商 {supplier_id} PDF 缺货状态失败: {e}")
        raise HTTPException(500, str(e))

@app.post("/api/suppliers/sync-pdf-missing")
async def sync_all_pdf_missing():
    """更新所有 PDF 导入店铺的缺货商品状态：非最后一个导入日导入的商品全部标记为缺货"""
    try:
        results = db.sync_all_pdf_suppliers_missing()
        return {
            "success": True,
            "data": results,
            "message": f"已完成所有 PDF 店铺缺货状态更新，共处理 {len(results)} 个店铺"
        }
    except Exception as e:
        logger.error(f"同步所有 PDF 店铺缺货状态失败: {e}")
        raise HTTPException(500, str(e))




# ── Excel 导入 ────────────────────────────────────────────────
@app.post("/api/suppliers/{supplier_id}/excel-preview")
async def excel_preview(supplier_id: int, file: UploadFile = File(...)):
    """上传Excel，返回前15行数据供用户选择表头行"""
    import openpyxl, io
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "请上传Excel文件（.xlsx / .xls）")
    content = await file.read()
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(400, "文件过大，最大支持100MB")
    try:
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=True)
    except Exception as e:
        raise HTTPException(400, f"Excel读取失败: {e}")
    ws = wb.worksheets[0]
    rows = []
    for row in ws.iter_rows(min_row=1, max_row=15, values_only=True):
        rows.append([str(c) if c is not None else "" for c in row])
    max_cols = max((len([c for c in r if c.strip()]) for r in rows), default=1)
    rows = [r[:max(max_cols, 1)] for r in rows]
    return {"rows": rows, "filename": file.filename}

@app.post("/api/suppliers/{supplier_id}/import-excel")
async def import_excel(supplier_id: int, file: UploadFile = File(...),
                       header_row: int = Form(1),
                       col_name: int = Form(-1),
                       col_sku: int = Form(-1),
                       col_price: int = Form(-1),
                       col_unit: int = Form(-1),
                       col_image: int = Form(-1),
                       col_category: int = Form(-1),
                       col_brand: int = Form(-1)):
    """导入Excel商品，列索引0-based，-1表示不导入
    跳过条件：名称为空/价格为空或非数字
    """
    import openpyxl, io, re

    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "请上传Excel文件（.xlsx / .xls）")

    suppliers_list = db.get_all_suppliers()
    if not any(s["id"] == supplier_id for s in suppliers_list):
        raise HTTPException(404, "供应商不存在")

    content = await file.read()
    try:
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=False)
    except Exception as e:
        raise HTTPException(400, f"Excel读取失败: {e}")

    ws = wb.worksheets[0]

    # 提取嵌入图片（按行号映射）
    image_map = {}
    if len(content) <= 30 * 1024 * 1024:
        try:
            import uuid
            from PIL import Image as PilImage
            for img in ws._images:
                try:
                    row_num = img.anchor._from.row + 1
                    img_data = img._data()
                    if not img_data or len(img_data) > 5 * 1024 * 1024:
                        continue
                    fname = f"{uuid.uuid4()}.jpg"
                    fpath = os.path.join(images_dir, "excel_import", fname)
                    os.makedirs(os.path.dirname(fpath), exist_ok=True)
                    pil = PilImage.open(io.BytesIO(img_data)).convert("RGB")
                    pil.thumbnail((800, 800))
                    pil.save(fpath, "JPEG", quality=85)
                    image_map[row_num] = f"/images/excel_import/{fname}"
                except Exception:
                    continue
        except Exception:
            pass
    logger.info(f"[Excel导入] 提取到{len(image_map)}张嵌入图片")

    def get_cell(row, ci):
        if ci < 0 or ci >= len(row):
            return None
        return row[ci]

    def to_float(v):
        if v is None:
            return None
        try:
            s = re.sub(r"[,$\s\u5143\uffe5,]", "", str(v).strip())
            return float(s) if s else None
        except:
            return None

    def to_str(v):
        return str(v).strip() if v is not None else ""

    inserted = updated = skipped = 0
    error_details = []
    data_start = header_row + 1  # 表头行之后开始

    with db.connection() as conn:
        cursor = conn.cursor(buffered=True)
        # 判断是否为原有供应商的新商品（供应商创建>24h且已有>100条商品）
        cursor.execute("""
            SELECT TIMESTAMPDIFF(HOUR, created_at, NOW()) > 24
                   AND (SELECT COUNT(*) FROM products WHERE supplier_id=%s AND is_available=1) > 100
            FROM suppliers WHERE id=%s
        """, (supplier_id, supplier_id))
        row_sup = cursor.fetchone()
        is_new_supplier = not (row_sup and row_sup[0])
        for row_idx, row in enumerate(ws.iter_rows(min_row=data_start, values_only=True), start=data_start):
            row = list(row) if row else []
            if not any(v for v in row if v is not None and str(v).strip()):
                continue

            name  = to_str(get_cell(row, col_name))
            sku   = to_str(get_cell(row, col_sku))
            price = to_float(get_cell(row, col_price))
            unit_raw = get_cell(row, col_unit)
            img_url   = to_str(get_cell(row, col_image))
            category  = to_str(get_cell(row, col_category))
            brand     = to_str(get_cell(row, col_brand))

            # 跳过条件
            if not name:
                skipped += 1
                error_details.append(f"第{row_idx}行: 名称为空，跳过")
                continue
            if price is None or price <= 0:
                skipped += 1
                error_details.append(f"第{row_idx}行 [{name}]: 价格无效，跳过")
                continue

            unit_str = ""
            if unit_raw is not None and str(unit_raw).strip():
                try:
                    unit_str = str(int(float(str(unit_raw)))) + "件/箱"
                except:
                    unit_str = to_str(unit_raw)

            # 嵌入图片优先，其次URL
            final_image = image_map.get(row_idx, "") or img_url

            # 查重
            existing = None
            if sku:
                cursor.execute(
                    "SELECT id, price FROM products WHERE supplier_id=%s AND sku=%s LIMIT 1",
                    (supplier_id, sku)
                )
                existing = cursor.fetchone()
            if not existing:
                cursor.execute(
                    "SELECT id, price FROM products WHERE supplier_id=%s AND name=%s LIMIT 1",
                    (supplier_id, name)
                )
                existing = cursor.fetchone()

            if existing:
                pid = existing[0] if isinstance(existing, tuple) else existing["id"]
                old_price = float(existing[1] if isinstance(existing, tuple) else existing["price"])
                cursor.execute(
                    """UPDATE products SET name=%s,sku=%s,price=%s,unit=%s,
                       category=%s,brand=%s,image_url=%s,is_available=1,is_missing=0,updated_at=NOW() WHERE id=%s""",
                    (name, sku, price, unit_str, category, brand, final_image, pid)
                )
                if abs(price - old_price) > 0.001:
                    cursor.execute(
                        "INSERT INTO price_history (product_id,price,recorded_at) VALUES (%s,%s,NOW())",
                        (pid, price)
                    )
                updated += 1
            else:
                cursor.execute(
                    """INSERT INTO products
                       (supplier_id,name,sku,price,unit,category,brand,image_url,is_available,is_new,created_at,updated_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1,%s,NOW(),NOW())""",
                    (supplier_id, name, sku, price, unit_str, category, brand, final_image, 0 if is_new_supplier else 1)
                )
                pid = cursor.lastrowid
                if pid:
                    cursor.execute(
                        "INSERT INTO price_history (product_id,price,recorded_at) VALUES (%s,%s,NOW())",
                        (pid, price)
                    )
                inserted += 1

    if error_details:
        logger.info(f"[Excel导入] 跳过{skipped}行: " + "; ".join(error_details[:5]))

    # ── 缺失标记：本次Excel未出现的已有商品标记为缺失 ──
    imported_keys = set()
    for row_idx2, row2 in enumerate(ws.iter_rows(min_row=data_start, values_only=True), start=data_start):
        row2 = list(row2) if row2 else []
        n = to_str(get_cell(row2, col_name))
        s = to_str(get_cell(row2, col_sku))
        if n:
            imported_keys.add((s, n))

    with db.connection() as conn2:
        cur2 = conn2.cursor(buffered=True)
        cur2.execute("SELECT id, sku, name FROM products WHERE supplier_id=%s", (supplier_id,))
        missing_ids = []
        for row in cur2.fetchall():
            pid, sku, name = row
            key = ((sku or '').strip(), (name or '').strip())
            if key not in imported_keys:
                missing_ids.append(pid)
        cur2.execute("UPDATE products SET is_missing=0 WHERE supplier_id=%s", (supplier_id,))
        if missing_ids:
            placeholders = ','.join(['%s'] * len(missing_ids))
            cur2.execute(f"UPDATE products SET is_missing=1 WHERE id IN ({placeholders})", missing_ids)
        conn2.commit()
    marked_missing = len(missing_ids)
    logger.info(f"[Excel导入] 供应商{supplier_id}: 标记缺失{marked_missing}条")

    return {
        "message": f"导入完成：新增{inserted}条，更新{updated}条，跳过{skipped}条，缺失{marked_missing}条",
        "inserted": inserted, "updated": updated, "skipped": skipped, "missing": marked_missing,
        "error_details": error_details[:50],
    }


# ── 收藏接口 ────────────────────────────────────────────────
@app.get("/api/favorites")
async def get_favorites():
    """获取所有收藏的 product_id 列表"""
    try:
        ids = db.get_favorite_ids()
        return {"ids": ids}
    except Exception as e:
        logger.error(f"获取收藏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/favorites/sync")
async def sync_favorites(data: dict):
    """批量同步收藏（用于 localStorage 迁移）"""
    try:
        product_ids = data.get("product_ids", [])
        if not product_ids:
            return {"synced": 0}
        count = db.sync_favorites(product_ids)
        return {"synced": count}
    except Exception as e:
        logger.error(f"同步收藏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/favorites/{product_id}")
async def add_favorite(product_id: int):
    """添加收藏"""
    try:
        added = db.add_favorite(product_id)
        return {"success": True, "added": added}
    except Exception as e:
        logger.error(f"添加收藏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/favorites/{product_id}")
async def remove_favorite(product_id: int):
    """取消收藏"""
    try:
        removed = db.remove_favorite(product_id)
        return {"success": True, "removed": removed}
    except Exception as e:
        logger.error(f"取消收藏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/favorites")
async def clear_favorites():
    """清空所有收藏"""
    try:
        cleared = db.clear_all_favorites()
        return {"success": True, "cleared": cleared}
    except Exception as e:
        logger.error(f"清空收藏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 购物车接口 ───────────────────────────────────────────────
@app.get("/api/cart")
async def get_cart():
    """获取购物车商品列表及统计汇总"""
    try:
        items = db.get_cart_items()
        stats = db.get_cart_stats()

        total_base = sum(round((item["price"] or 0) * (item["quantity"] or 1), 2) for item in items)
        total_adjusted = 0.0
        for item in items:
            p = float(item["price"] or 0)
            adj = float(item.get("price_adjustment") or 0)
            adj_p = round(p * (1 + adj / 100), 2)
            total_adjusted += round(adj_p * item["quantity"], 2)
            item["adjusted_price"] = adj_p
            item["base_subtotal"] = round(p * item["quantity"], 2)
            item["adj_subtotal"] = round(adj_p * item["quantity"], 2)

        return {
            "items": items,
            "distinct_count": stats["distinct_count"],
            "total_quantity": stats["total_quantity"],
            "total_base_price": round(total_base, 2),
            "total_adjusted_price": round(total_adjusted, 2),
        }
    except Exception as e:
        logger.error(f"获取购物车失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cart/count")
async def get_cart_count(include_missing: bool = False):
    """获取购物车数量小红点统计"""
    try:
        return db.get_cart_stats(include_missing=include_missing)
    except Exception as e:
        logger.error(f"获取购物车统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cart")
async def add_to_cart(data: CartItemAdd):
    """添加商品至购物车"""
    try:
        pid = data.product_id
        if not pid and data.sku:
            sku = data.sku.strip()
            clean_sku = sku.replace("-", "").replace(" ", "")
            with db.connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT id FROM products 
                    WHERE sku = %s OR REPLACE(REPLACE(sku, '-', ''), ' ', '') = %s OR sku LIKE %s
                    ORDER BY is_available DESC, id DESC LIMIT 1
                """, (sku, clean_sku, f"{sku}%"))
                row = cursor.fetchone()
                if row:
                    pid = row["id"]

        if not pid:
            raise HTTPException(status_code=400, detail="缺少有效的商品ID或SKU")

        res = db.add_to_cart(pid, data.quantity, data.mode)
        stats = db.get_cart_stats()
        return {"success": True, "item": res, "stats": stats}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"加入购物车失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/cart/{product_id}")
async def update_cart_item(product_id: int, data: CartItemUpdate):
    """更新购物车中商品数量"""
    try:
        res = db.update_cart_quantity(product_id, data.quantity)
        stats = db.get_cart_stats()
        return {"success": True, "result": res, "stats": stats}
    except Exception as e:
        logger.error(f"更新购物车失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cart/{product_id}")
async def remove_cart_item(product_id: int):
    """从购物车移除单个商品"""
    try:
        removed = db.remove_from_cart(product_id)
        stats = db.get_cart_stats()
        return {"success": True, "removed": removed, "stats": stats}
    except Exception as e:
        logger.error(f"移除购物车商品失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cart")
async def clear_cart():
    """清空购物车"""
    try:
        count = db.clear_cart()
        return {"success": True, "cleared": count}
    except Exception as e:
        logger.error(f"清空购物车失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cart/batch")
async def batch_add_cart(data: CartBatchAdd):
    """批量加入购物车（支持结构化列表或多行文本解析）"""
    try:
        items = list(data.items or [])
        if data.text:
            import re
            lines = [l.strip() for l in data.text.split("\n") if l.strip()]
            for line in lines:
                parts = re.split(r'[\s,\t]+', line)
                if len(parts) >= 2:
                    sku = parts[0].strip()
                    qty = 1
                    for p in parts[1:]:
                        if p.isdigit():
                            qty = int(p)
                            break
                    items.append({"sku": sku, "quantity": qty})
                elif len(parts) == 1 and parts[0]:
                    items.append({"sku": parts[0].strip(), "quantity": 1})

        if not items:
            return {"success_count": 0, "failed_count": 0, "message": "无有效条目"}

        res = db.batch_add_to_cart(items)
        stats = db.get_cart_stats()
        res["stats"] = stats
        return res
    except Exception as e:
        logger.error(f"批量加入购物车失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cart/sync/{supplier_id}")
async def sync_cart_to_supplier(supplier_id: int, req: Optional[CartSyncRequest] = None):
    """将购物车中指定供应商的商品自动同步添加进目标供应商的网站购物车"""
    try:
        from crawler.cart_sync import CartSyncManager
        mgr = CartSyncManager(db)
        auto_adjust = req.auto_adjust if req else True
        session_cookies = req.session_cookies if req else None
        filter_pids = set(req.product_ids) if (req and req.product_ids) else None

        all_items = db.get_cart_items()
        supplier_items = [
            it for it in all_items 
            if it.get("supplier_id") == supplier_id and (filter_pids is None or it.get("product_id") in filter_pids)
        ]

        if not supplier_items:
            raise HTTPException(status_code=400, detail="本地购物车中没有该供应商的商品")

        # 异步线程执行同步，避免阻塞主事件循环
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(
            None, mgr.sync_to_supplier, supplier_id, supplier_items, auto_adjust, session_cookies
        )
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"同步购物车至供应商失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cart/validate-quantities")
async def validate_cart_quantities(req: Optional[CartValidateRequest] = None):
    """校验购物车商品数量是否满足起订量(min_qty)与箱规/步进倍数(package_qty)，支持一键自动修复"""
    try:
        from crawler.cart_sync import calc_valid_quantity
        auto_fix = req.auto_fix if req else False
        supplier_id = req.supplier_id if req else None

        items = db.get_cart_items()
        if supplier_id:
            items = [it for it in items if it.get("supplier_id") == supplier_id]

        issues = []
        for it in items:
            cur_qty = int(it.get("quantity") or 1)
            min_q = int(it.get("min_qty") or 1)
            pkg_q = int(it.get("package_qty") or 1)

            valid_q = calc_valid_quantity(cur_qty, min_q, pkg_q)
            if valid_q != cur_qty:
                issue = {
                    "product_id": it.get("product_id"),
                    "name": it.get("name"),
                    "sku": it.get("sku"),
                    "supplier_id": it.get("supplier_id"),
                    "supplier_name": it.get("supplier_name"),
                    "current_quantity": cur_qty,
                    "valid_quantity": valid_q,
                    "min_qty": min_q,
                    "package_qty": pkg_q,
                }
                issues.append(issue)
                if auto_fix:
                    db.update_cart_quantity(it["product_id"], valid_q)

        return {
            "has_issues": len(issues) > 0,
            "issue_count": len(issues),
            "fixed_count": len(issues) if auto_fix else 0,
            "issues": issues,
        }
    except Exception as e:
        logger.exception(f"校验购物车数量异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/cart/export-xlsx")
async def export_cart_xlsx(mode: Optional[str] = "wholesale", mult: Optional[float] = 2.2, supplier_id: Optional[int] = None, supplier_name: Optional[str] = None, lang: Optional[str] = "es", include_missing: bool = False):
    """导出购物车为xlsx，含嵌入商品缩略图和价格汇总（支持 mode=wholesale 或 mode=retail，支持 lang=es 或 lang=zh）"""
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _do_export_cart_xlsx_sync, mode, mult, supplier_id, supplier_name, lang, include_missing)
    except Exception as e:
        logger.exception(f"导出购物车xlsx失败: {e}")
        raise HTTPException(500, f"导出失败: {str(e)}")


def _do_export_cart_xlsx_sync(mode="wholesale", mult=2.2, supplier_id=None, supplier_name=None, lang="es", include_missing=False):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.drawing.image import Image as XLImage
    from openpyxl.utils import get_column_letter
    from PIL import Image as PILImage
    import io as _io
    from urllib.parse import quote

    is_retail = (mode == "retail")
    is_es = (lang != "zh")
    if is_retail and (mult is None or mult == 0):
        try:
            mult_val = db.get_mobile_multiplier()
        except Exception:
            mult_val = 2.2
    else:
        mult_val = float(mult or 2.2)

    items = db.get_cart_items()
    if not include_missing:
        items = [it for it in items if it.get("is_missing") != 1]

    matched_sup_name = ""
    if supplier_id:
        items = [it for it in items if it.get("supplier_id") == supplier_id]
        if items:
            matched_sup_name = items[0].get("supplier_name") or ""
    elif supplier_name and supplier_name != "__all__":
        items = [it for it in items if (it.get("supplier_name") or "").strip() == supplier_name.strip()]
        if items:
            matched_sup_name = supplier_name.strip()

    wb = Workbook()
    ws = wb.active
    if is_es:
        default_title = "Presupuesto" if is_retail else "Pedido"
        ws.title = f"{matched_sup_name[:10]}_{default_title}" if matched_sup_name else default_title
    else:
        default_title = "商品订货清单" if is_retail else "采购进价清单"
        ws.title = f"{matched_sup_name[:10]}_订货清单" if matched_sup_name else default_title

    if is_retail:
        if is_es:
            headers = ["Foto", "Código / SKU", "Descripción / Producto", "Cantidad", "Precio Unitario (ARS)", "Subtotal (ARS)"]
        else:
            headers = ["图片", "SKU", "商品名称", "数量", "单价 (ARS)", "小计 (ARS)"]
        col_widths = [24, 18, 50, 12, 18, 20]
    else:
        if is_es:
            headers = ["Foto", "Código / SKU", "Descripción / Producto", "Proveedor", "Cantidad", "Precio Base (ARS)", "Precio Final (ARS)", "Subtotal (ARS)"]
        else:
            headers = ["图片", "SKU", "商品名称", "供应商", "数量", "原单价 (ARS)", "含税单价 (ARS)", "小计 (ARS)"]
        col_widths = [24, 18, 45, 18, 12, 16, 16, 18]

    header_fill = PatternFill("solid", start_color="1F2937")
    header_font = Font(bold=True, color="00D4AA", name="Arial", size=11)
    thin = Side(style="thin", color="30363D")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border

    ws.row_dimensions[1].height = 24
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    total_qty = 0
    total_amount = 0.0
    consultar_text = "A consultar" if is_es else "CONSULTAR"
    pending_text = "A consultar" if is_es else "待询价"

    IMG_DISPLAY_PX = 160  # 单元格内显示尺寸（像素）
    IMG_RENDER_PX = 450   # 内嵌图片分辨率（放大查看依然清晰）

    for idx, item in enumerate(items):
        row_idx = idx + 2
        ws.row_dimensions[row_idx].height = 126  # 约168px高，完整容纳160px大图

        qty = int(item.get("quantity") or 1)
        price = float(item.get("price") or 0)
        adj = float(item.get("price_adjustment") or 0)
        cost_price = round(price * (1 + adj / 100), 2)
        unit_price = round(cost_price * mult_val, 2) if is_retail else cost_price
        subtotal = round(unit_price * qty, 2)

        total_qty += qty
        total_amount += subtotal

        img_written = False
        img_rel = (item.get("image_local") or "").replace("\\", "/").lstrip("./").lstrip("/")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_path = os.path.join(base_dir, img_rel) if img_rel else ""
        if not (img_path and os.path.isfile(img_path)):
            img_url = (item.get("image_url") or "").replace("\\", "/")
            if img_url.startswith("/images/") or img_url.startswith("images/"):
                img_path = os.path.join(base_dir, img_url.lstrip("/"))

        if img_path and os.path.isfile(img_path):
            try:
                with PILImage.open(img_path) as im:
                    im_rgb = im.convert("RGB")
                    orig_w, orig_h = im_rgb.size
                    resample_filter = PILImage.Resampling.LANCZOS if hasattr(PILImage, "Resampling") else PILImage.LANCZOS
                    im_rgb.thumbnail((IMG_RENDER_PX, IMG_RENDER_PX), resample_filter)
                    buf = _io.BytesIO()
                    im_rgb.save(buf, format="JPEG", quality=92)
                    buf.seek(0)
                    xl_img = XLImage(buf)
                    if orig_w > 0 and orig_h > 0:
                        scale = min(IMG_DISPLAY_PX / orig_w, IMG_DISPLAY_PX / orig_h)
                        xl_img.width = max(1, int(round(orig_w * scale)))
                        xl_img.height = max(1, int(round(orig_h * scale)))
                    else:
                        xl_img.width = IMG_DISPLAY_PX
                        xl_img.height = IMG_DISPLAY_PX
                    ws.add_image(xl_img, f"A{row_idx}")
                    img_written = True
            except Exception:
                pass

        if not img_written:
            cell = ws.cell(row=row_idx, column=1, value="[Sin foto]" if is_es else "[无图]")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
            cell.font = Font(name="Arial", size=9, color="888888")
        else:
            ws.cell(row=row_idx, column=1).border = border

        is_missing = (item.get("is_missing") == 1)
        missing_tag = (" [AGOTADO]" if is_es else " [已缺货]") if is_missing else ""
        prod_name = (item.get("name") or "") + missing_tag

        if is_retail:
            row_data = [
                None,
                item.get("sku") or "",
                prod_name,
                qty,
                f"${unit_price:,.2f}" if price > 0 else consultar_text,
                f"${subtotal:,.2f}" if price > 0 else pending_text,
            ]
        else:
            sup_text = f"{item.get('supplier_name') or ''} ({'+' if adj>0 else ''}{adj}%)" if adj else (item.get("supplier_name") or "")
            row_data = [
                None,
                item.get("sku") or "",
                prod_name,
                sup_text,
                qty,
                f"${price:,.2f}" if price > 0 else consultar_text,
                f"${cost_price:,.2f}" if price > 0 else consultar_text,
                f"${subtotal:,.2f}" if price > 0 else pending_text,
            ]

        for col_idx, val in enumerate(row_data, 1):
            if col_idx == 1:
                continue
            c = ws.cell(row=row_idx, column=col_idx, value=val)
            c.border = border
            c.font = Font(name="Arial", size=10)
            if (is_retail and col_idx in (2, 4)) or (not is_retail and col_idx in (2, 5)):
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == len(headers) or (is_retail and col_idx == 5) or (not is_retail and col_idx in (6, 7)):
                c.alignment = Alignment(horizontal="right", vertical="center")
                if col_idx == len(headers):
                    c.font = Font(name="Arial", size=11, bold=True, color="00D4AA")
            else:
                c.alignment = Alignment(vertical="center", wrap_text=(col_idx == 3))

    last_row = len(items) + 2
    ws.row_dimensions[last_row].height = 26
    ws.cell(row=last_row, column=1, value="Total" if is_es else "合计").font = Font(name="Arial", size=11, bold=True)
    ws.cell(row=last_row, column=1).alignment = Alignment(horizontal="center", vertical="center")
    
    qty_col = 4 if is_retail else 5
    subtotal_col = 6 if is_retail else 8
    ws.cell(row=last_row, column=qty_col, value=total_qty).font = Font(name="Arial", size=11, bold=True)
    ws.cell(row=last_row, column=qty_col).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=last_row, column=subtotal_col, value=f"${total_amount:,.2f}").font = Font(name="Arial", size=12, bold=True, color="F59E0B")
    ws.cell(row=last_row, column=subtotal_col).alignment = Alignment(horizontal="right", vertical="center")
    for col_idx in range(1, len(headers) + 1):
        ws.cell(row=last_row, column=col_idx).border = border
        ws.cell(row=last_row, column=col_idx).fill = PatternFill("solid", start_color="21262D")

    ws.freeze_panes = "A2"

    import uuid
    export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
    os.makedirs(export_dir, exist_ok=True)
    if is_es:
        prefix = "Presupuesto" if is_retail else "Pedido"
    else:
        prefix = "商品订货清单" if is_retail else "采购进价清单"
    f_prefix = f"{matched_sup_name}_{prefix}" if matched_sup_name else prefix
    fname = f"{f_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    tmp_path = os.path.join(export_dir, f"_cart_{uuid.uuid4().hex}.xlsx")
    wb.save(tmp_path)

    return FileResponse(
        tmp_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=fname,
        headers={"Content-Disposition": f"attachment; filename*=utf-8''{quote(fname)}"}
    )


# ── 系统设置 (全局 / 手机端倍率) ───────────────────────────
class MultiplierUpdate(BaseModel):
    multiplier: float

@app.get("/api/settings/mobile-multiplier")
async def get_mobile_multiplier():
    """获取手机端售价倍率"""
    try:
        mult = db.get_mobile_multiplier()
        return {"multiplier": mult}
    except Exception as e:
        logger.error(f"获取手机端倍率失败: {e}")
        return {"multiplier": 2.2}

@app.post("/api/settings/mobile-multiplier")
@app.put("/api/settings/mobile-multiplier")
async def update_mobile_multiplier(data: MultiplierUpdate):
    """电脑端更新手机端售价倍率"""
    if data.multiplier <= 0 or data.multiplier > 100:
        raise HTTPException(400, "倍率必须大于 0 且小于等于 100")
    try:
        db.set_mobile_multiplier(data.multiplier)
        return {
            "success": True,
            "multiplier": round(float(data.multiplier), 4),
            "message": f"手机端零售倍率已更新为 {data.multiplier}x"
        }
    except Exception as e:
        logger.error(f"更新手机端倍率失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ── 云端同步 (Google Drive) ───────────────────────────────────
@app.post("/api/cloud/sync")
async def sync_to_google_drive(max_copy: int = 1500):
    """一键将数据库与新增图片同步到 Google Drive (G:\我的云端硬盘\Supplier_Crawler_Cloud)"""
    from scripts.cloud_sync import run_full_cloud_sync
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: run_full_cloud_sync(max_copy, db=db))
    return {"success": True, "data": result}

@app.post("/api/cloud/pull-cart")
async def pull_cart_from_google_drive():
    """从 Google Drive 的 cloud_state.json 拉取手机端修改的购物车与收藏夹到本地 MySQL"""
    from scripts.cloud_sync import CLOUD_DIR
    state_path = os.path.join(CLOUD_DIR, "cloud_state.json")
    if not os.path.exists(state_path):
        raise HTTPException(404, "云盘尚未生成 cloud_state.json")
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    cart_dict = state.get("cart") or {}
    fav_list = state.get("favorites") or []
    with db.connection() as conn:
        cur = conn.cursor()
        for pid_str, qty in cart_dict.items():
            if int(qty) > 0:
                cur.execute(
                    "INSERT INTO cart_items (product_id, quantity) VALUES (%s, %s) ON DUPLICATE KEY UPDATE quantity=%s",
                    (int(pid_str), int(qty), int(qty))
                )
        for pid in fav_list:
            cur.execute("INSERT IGNORE INTO favorites (product_id) VALUES (%s)", (int(pid),))
    return {"success": True, "cart_synced": len(cart_dict), "favorites_synced": len(fav_list)}


# ── 启动 / 关闭 ─────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global db, scheduler
    try:
        print("\n[STARTUP] 正在连接 MySQL...", flush=True)
        db = DatabaseManager(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "admin123"),
            database=os.getenv("DB_NAME", "supplier_crawler"),
        )
        print("[STARTUP] MySQL 连接成功", flush=True)
        print("[STARTUP] 图片目录:", images_dir, flush=True)
        scheduler = CrawlerScheduler(db)
        db.init_schema()
        print("[STARTUP] 数据库初始化完成", flush=True)
        scheduler.start()
        for s in db.get_all_suppliers():
            cron = s.get("cron_expr") or "0 2 * * *"
            scheduler.schedule_supplier(s["id"], cron)
        logger.info("系统启动完成 -> http://localhost:8100")
        print("\n启动成功！浏览器打开 http://localhost:8100\n", flush=True)
    except Exception as e:
        print(f"\n启动失败: {e}", flush=True)
        print("请检查：", flush=True)
        print("  1. MySQL 是否已启动", flush=True)
        print("  2. 密码是否正确（DB_PASSWORD）", flush=True)
        print("  3. 数据库 supplier_crawler 是否已创建", flush=True)
        raise

@app.on_event("shutdown")
async def shutdown():
    if scheduler:
        scheduler.stop()
    logger.info("系统已关闭")

# 托管前端
_frontend = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dashboard.html")
_mobile = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "mobile.html")
@app.get("/")
async def serve_ui(request: Request):
    if request.query_params.get("desktop") != "1":
        ua = (request.headers.get("user-agent") or "").lower()
        if any(k in ua for k in ("android", "iphone", "ipad", "ipod", "harmonyos", "mobile")):
            return RedirectResponse(url="/mobile", status_code=302)
    if os.path.exists(_frontend):
        return FileResponse(_frontend)
    return {"status": "running", "ui": "请打开 frontend/dashboard.html"}

@app.get("/mobile")
async def serve_mobile():
    if os.path.exists(_mobile):
        return FileResponse(_mobile)
    return {"error": "mobile.html not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8100, reload=False, log_level="info")
