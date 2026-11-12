# -*- coding: utf-8 -*-
"""
supplier_crawler/crawler/whatsapp_monitor.py
WhatsApp Web 自动化监控与供应商 PDF 自动识别入库模块

功能特性：
1. 使用 Playwright 持久化浏览器目录 (.whatsapp_profile)，首次扫码登录后长期保持会话。
2. 按白名单监控指定供应商联系人或群组（支持关键词模糊匹配）。
3. 自动检测聊天中的 PDF 报价单/目录附件并下载到本地归档目录。
4. 三层智能识别（聊天对象映射 + 文件名特征 + PDF 内部版式/文本指纹）自动判断属于哪个供应商及对应解析器。
5. 直接复用项目 PDF 解析器与 MySQL 入库逻辑，自动更新商品价格、历史记录、缺货状态及爬取日志。
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import shutil
import sys
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.db_manager import DatabaseManager
from pdf_parsers import get_parser, list_parsers

logger = logging.getLogger("whatsapp_monitor")


def compute_file_sha256(file_path: str) -> str:
    """计算文件 SHA256，用于防止同一份 PDF 重复解析入库"""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def send_email_notification(
    config: dict,
    subject: str,
    body_text: str,
    recipient_override: str = "",
    attachments: Optional[List[str]] = None,
) -> bool:
    """通过 SMTP SSL 发送邮件通知（支持 QQ 邮箱 / 163 / Gmail 等，支持携带文件附件）"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
    from email.header import Header

    email_cfg = config.get("email_notify", {})
    smtp_host = os.getenv("SMTP_HOST") or email_cfg.get("smtp_host", "smtp.qq.com")
    smtp_port = int(os.getenv("SMTP_PORT") or email_cfg.get("smtp_port", 465))
    sender = os.getenv("SMTP_SENDER") or email_cfg.get("sender_email", "1813634420@qq.com")
    auth_code = os.getenv("SMTP_AUTH_CODE") or email_cfg.get("smtp_auth_code", "")
    recipient = recipient_override or email_cfg.get("recipient_email", "1813634420@qq.com")

    if not auth_code:
        logger.warning("未配置 SMTP 授权码 (email_notify.smtp_auth_code)，无法发送邮件。")
        return False

    valid_attachments = [p for p in (attachments or []) if p and os.path.exists(p)]
    if valid_attachments:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        for file_path in valid_attachments:
            fname = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=fname)
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=("utf-8", "", fname),
            )
            msg.attach(part)
    else:
        msg = MIMEText(body_text, "plain", "utf-8")

    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = str(Header(subject, "utf-8"))
    msg["X-Antigravity-Auto"] = "1"

    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=60)
    try:
        server.login(sender, auth_code)
        res = server.sendmail(sender, [recipient], msg.as_string())
        logger.info(f"[邮件通知] 已成功发送邮件至 {recipient}: {subject} (附件数={len(valid_attachments)}, SMTP返回: {res})")
    finally:
        try:
            server.quit()
        except Exception:
            pass

    return True


class ProcessedState:
    """管理已处理的消息 ID 和文件 Hash 状态，支持持久化到 JSON"""

    def __init__(self, state_file: str):
        self.state_file = state_file
        self.message_ids: Dict[str, dict] = {}
        self.file_hashes: Dict[str, dict] = {}
        self.load()

    def load(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.message_ids = data.get("message_ids", {})
                self.file_hashes = data.get("file_hashes", {})
            except Exception as e:
                logger.warning(f"读取状态文件失败 ({self.state_file}): {e}")

    def save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.state_file)), exist_ok=True)
        data = {
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message_ids": self.message_ids,
            "file_hashes": self.file_hashes,
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def is_message_processed(self, msg_id: str) -> bool:
        return bool(msg_id and msg_id in self.message_ids)

    def is_file_processed(self, sha256: str) -> bool:
        return bool(sha256 and sha256 in self.file_hashes)

    def mark_processed(self, msg_id: str, sha256: str, info: dict):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {**info, "processed_at": now_str}
        if msg_id:
            self.message_ids[msg_id] = record
        if sha256:
            self.file_hashes[sha256] = record
        self.save()


class PDFSupplierDetector:
    """
    三层 PDF 供应商与解析器识别器：
    1. PDF 内容结构/文本指纹识别（最准确，即使文件名是通用 Catalogo.pdf 也能识别）
    2. PDF 文件名关键词识别
    3. WhatsApp 聊天窗口名称（联系人/群名）映射识别
    """

    # 默认供应商与解析器映射字典（与数据库 suppliers 表对齐）
    DEFAULT_SUPPLIER_MAP = {
        "dsaza":     {"supplier_id": 6,  "supplier_name": "Dsaza",     "parser_id": "dsaza"},
        "kandel":    {"supplier_id": 9,  "supplier_name": "by kandel", "parser_id": "kandel"},
        "kk":        {"supplier_id": 10, "supplier_name": "KK",        "parser_id": "kk"},
        "panda":     {"supplier_id": 11, "supplier_name": "Panda哥",   "parser_id": "panda"},
        "durax":     {"supplier_id": 12, "supplier_name": "Durax",     "parser_id": "lp"},
        "rigolleau": {"supplier_id": 13, "supplier_name": "Rigolleau", "parser_id": "lp"},
        "najal":     {"supplier_id": 14, "supplier_name": "najal",     "parser_id": "najal"},
        "gaston":    {"supplier_id": 16, "supplier_name": "Gaston",    "parser_id": "gaston"},
    }

    def __init__(self, config: dict, db: Optional[DatabaseManager] = None):
        self.config = config
        self.db = db
        self._sync_supplier_ids_from_db()

    def _sync_supplier_ids_from_db(self):
        """从数据库动态校准供应商名称对应的真实 ID，防止硬编码 ID 偏差"""
        if not self.db:
            return
        try:
            suppliers = self.db.get_all_suppliers()
            name_to_id = {s["name"].strip().lower(): s["id"] for s in suppliers}
            for key, item in self.DEFAULT_SUPPLIER_MAP.items():
                sname_lower = item["supplier_name"].lower()
                if sname_lower in name_to_id:
                    item["supplier_id"] = name_to_id[sname_lower]
        except Exception as e:
            logger.debug(f"校准数据库供应商ID跳过: {e}")

    def identify(
        self,
        pdf_path: str,
        filename: str = "",
        chat_name: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        综合判断 PDF 属于哪个供应商，返回:
        {
            "supplier_id": int,
            "supplier_name": str,
            "parser_id": str,
            "match_source": str,  # "pdf_content" | "filename" | "chat_name"
            "reason": str
        }
        """
        fname = filename or os.path.basename(pdf_path)

        # 1. 优先尝试从 PDF 内容指纹识别（防止群聊转发或通用文件名误判）
        if self.config.get("auto_detect_from_pdf_content", True) and os.path.exists(pdf_path):
            content_match = self.detect_from_pdf_content(pdf_path)
            if content_match:
                return content_match

        # 2. 从文件名关键词识别
        fname_match = self.detect_from_filename(fname)
        if fname_match:
            return fname_match

        # 3. 从 WhatsApp 聊天名称映射识别
        if chat_name:
            chat_match = self.detect_from_chat_name(chat_name)
            if chat_match:
                return chat_match

        return None

    def detect_from_pdf_content(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """提取 PDF 前几页的文本与页面尺寸特征，匹配对应的解析器与供应商"""
        pages_text = []
        page_sizes = []

        # 优先使用 PyMuPDF (fitz) 快速提取前 6 页文本
        try:
            import fitz
            doc = fitz.open(pdf_path)
            max_p = min(6, len(doc))
            for i in range(max_p):
                page = doc[i]
                page_sizes.append((page.rect.width, page.rect.height))
                pages_text.append(page.get_text("text") or "")
            doc.close()
        except Exception:
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    max_p = min(6, len(pdf.pages))
                    for i in range(max_p):
                        page = pdf.pages[i]
                        page_sizes.append((float(page.width), float(page.height)))
                        pages_text.append(page.extract_text() or "")
            except Exception as e:
                logger.warning(f"无法读取 PDF 内容进行指纹识别 ({pdf_path}): {e}")
                return None

        full_text = "\n".join(pages_text)
        upper_text = full_text.upper()

        # ── 特征 1: Najal ──
        if (
            "NAJAL@HOTMAIL.COM.AR" in upper_text
            or "AV.CORRIENTES 2294" in upper_text
            or len(re.findall(r"\bART\s+\d{3,6}\b", full_text)) >= 3
        ):
            return {
                **self.DEFAULT_SUPPLIER_MAP["najal"],
                "match_source": "pdf_content",
                "reason": "PDF内容包含 najal 页脚或 ART+SKU 格式特征",
            }

        # ── 特征 2: Dsaza ──
        if (
            ("BULTOS:" in upper_text and "::" in full_text)
            or ("CODIGO" in upper_text and "PRECIO" in upper_text and "BULTO" in upper_text and "FOTO" in upper_text)
            or "D'SAZA" in upper_text
            or "DSAZA" in upper_text
        ):
            return {
                **self.DEFAULT_SUPPLIER_MAP["dsaza"],
                "match_source": "pdf_content",
                "reason": "PDF内容包含 d'sazá 特征 (Bultos/双冒号分类或 Codigo Foto Precio Bulto 表头)",
            }

        # ── 特征 3: Gaston ──
        if (
            "DON ABRAHAM" in upper_text
            or "EMPAQUE: CAJA X" in upper_text
            or ("EMPAQUE:" in upper_text and "SKU:" in upper_text)
            or ("BULTO:" in upper_text and "MINIMO:" in upper_text and "CÓDIGO" in upper_text)
        ):
            return {
                **self.DEFAULT_SUPPLIER_MAP["gaston"],
                "match_source": "pdf_content",
                "reason": "PDF内容包含 Gaston 特征 (DON ABRAHAM / Empaque: Caja x / SKU+Bulto+Minimo)",
            }

        # ── 特征 4: LP (Durax / Rigolleau) ──
        if "PRECIO:" in upper_text and ";CA" in upper_text and "ARTICULO" in upper_text:
            rigo_count = len(re.findall(r"RIGOLLEAU|ENVASES RIGO", upper_text))
            durax_count = len(re.findall(r"DURAX", upper_text))
            if rigo_count > durax_count:
                return {
                    **self.DEFAULT_SUPPLIER_MAP["rigolleau"],
                    "match_source": "pdf_content",
                    "reason": f"PDF内容符合 LP 4列标准格式，且品牌 RIGOLLEAU 出现 {rigo_count} 次",
                }
            return {
                **self.DEFAULT_SUPPLIER_MAP["durax"],
                "match_source": "pdf_content",
                "reason": f"PDF内容符合 LP 4列标准格式 (DURAX={durax_count}, RIGOLLEAU={rigo_count})",
            }

        # ── 特征 5: KK (K&K) ──
        if (
            ("PACK:" in upper_text and "INT:" in upper_text)
            and len(re.findall(r"\bC\d{3,6}\b", full_text)) >= 2
        ):
            return {
                **self.DEFAULT_SUPPLIER_MAP["kk"],
                "match_source": "pdf_content",
                "reason": "PDF内容包含 K&K 特征 (Pack/Int 包装信息 + C开头价格)",
            }

        # ── 特征 6: Kandel ──
        is_landscape_792 = any(w > 740 and h < 660 for w, h in page_sizes)
        has_bm_pack = len(re.findall(r"\bB:\s*\d+\s+M:\s*\d+\b", full_text)) >= 2
        if has_bm_pack or (is_landscape_792 and ("COLLECTION" in upper_text or len(re.findall(r"\b\d{5,7}\b", full_text)) >= 4)):
            return {
                **self.DEFAULT_SUPPLIER_MAP["kandel"],
                "match_source": "pdf_content",
                "reason": "PDF内容包含 Kandel 特征 (792x612横向布局 / B:M:包装标记 / COLLECTION页眉)",
            }

        # ── 特征 7: Panda哥 ──
        panda_skus = re.findall(r"\b\d{1,3}/2[0-5]\d{3,4}[A-Za-z]{0,4}\b", full_text)
        has_opp_bag = ("OPP" in upper_text and "BAG" in upper_text) or "PCS" in upper_text
        std_panda_skus = re.findall(r"\b2[0-5]\d{3,4}[A-Za-z]{0,3}\b", full_text)
        if len(panda_skus) >= 2 or (has_opp_bag and len(std_panda_skus) >= 3):
            return {
                **self.DEFAULT_SUPPLIER_MAP["panda"],
                "match_source": "pdf_content",
                "reason": "PDF内容包含 Panda 玩具目录特征 (序号/24xxx SKU + OPP BAG/PCS)",
            }

        return None

    def detect_from_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """根据文件名中的关键词判断供应商"""
        fn = filename.lower()
        rules = [
            (["dsaza", "d'saza", "d_saza", "nuevos_ingresos"], "dsaza"),
            (["gaston", "catalogo_sp", "generales da", "don abraham", "rotacion"], "gaston"),
            (["kandel"], "kandel"),
            (["k&k", "catalogo_kk", "kk_"], "kk"),
            (["durax"], "durax"),
            (["rigolleau", "rigo"], "rigolleau"),
            (["najal"], "najal"),
            (["panda"], "panda"),
        ]
        for keywords, sup_key in rules:
            for kw in keywords:
                if kw in fn:
                    return {
                        **self.DEFAULT_SUPPLIER_MAP[sup_key],
                        "match_source": "filename",
                        "reason": f"文件名 '{filename}' 命中关键词 '{kw}'",
                    }
        return None

    def detect_from_chat_name(self, chat_name: str) -> Optional[Dict[str, Any]]:
        """根据 WhatsApp 联系人/群名称匹配配置或默认供应商"""
        cname = chat_name.strip().lower()
        if not cname:
            return None

        # 1. 先查 whatsapp_config.json 中的 monitored_chats
        for item in self.config.get("monitored_chats", []):
            if not item.get("enabled", True):
                continue
            target_name = (item.get("chat_name") or "").strip().lower()
            keywords = [k.strip().lower() for k in item.get("keywords", []) if k.strip()]
            if (target_name and target_name in cname) or any(kw in cname for kw in keywords):
                if item.get("supplier_id") and item.get("parser_id"):
                    return {
                        "supplier_id": int(item["supplier_id"]),
                        "supplier_name": item.get("supplier_name") or item.get("chat_name"),
                        "parser_id": item["parser_id"],
                        "match_source": "chat_name",
                        "reason": f"聊天窗口 '{chat_name}' 匹配监控配置 '{item.get('chat_name')}'",
                    }

        # 2. 兜底匹配默认供应商名
        for key, sup in self.DEFAULT_SUPPLIER_MAP.items():
            if key in cname or sup["supplier_name"].lower() in cname:
                return {
                    **sup,
                    "match_source": "chat_name",
                    "reason": f"聊天窗口 '{chat_name}' 匹配供应商 '{sup['supplier_name']}'",
                }
        return None


def import_pdf_to_supplier(
    db: DatabaseManager,
    pdf_path: str,
    supplier_id: int,
    parser_id: str,
    images_dir: str,
    source_label: str = "WhatsApp自动导入",
) -> Dict[str, Any]:
    """
    调用指定的 PDF 解析器解析 PDF 并导入到对应的供应商数据库（与 api/main.py 逻辑完全一致），
    同时在 crawl_logs 表中记录一条导入日志，方便在后台仪表盘查看。
    """
    parser = get_parser(parser_id)
    if parser is None:
        raise ValueError(f"未找到 PDF 解析器: {parser_id}")

    filename = os.path.basename(pdf_path)
    log_id = db.create_crawl_log(supplier_id)
    logger.info(f"[{source_label}] 开始解析 PDF: {filename} -> supplier_id={supplier_id}, parser={parser_id}")

    try:
        all_products = parser.parse(pdf_path, images_dir, supplier_id)
        if not all_products:
            msg = f"[{source_label}] {filename}: 解析出 0 条商品，请检查 PDF 格式是否匹配解析器 {parser_id}"
            logger.warning(msg)
            db.finish_crawl_log(log_id, "failed", 0, 0, 1, msg)
            return {
                "success": False,
                "parsed": 0,
                "inserted": 0,
                "updated": 0,
                "skipped": 0,
                "missing": 0,
                "message": msg,
            }

        inserted = updated = skipped = errors = 0
        with db.connection() as conn:
            cursor = conn.cursor(buffered=True)
            cursor.execute(
                """
                SELECT TIMESTAMPDIFF(HOUR, created_at, NOW()) > 24
                       AND (SELECT COUNT(*) FROM products WHERE supplier_id=%s AND is_available=1) > 100
                FROM suppliers WHERE id=%s
                """,
                (supplier_id, supplier_id),
            )
            row_sup = cursor.fetchone()
            is_new_supplier = not (row_sup and row_sup[0])

            for p in all_products:
                try:
                    if p.get("sku"):
                        cursor.execute(
                            "SELECT id, price, category, image_url FROM products WHERE supplier_id=%s AND sku=%s LIMIT 1",
                            (supplier_id, p["sku"]),
                        )
                    else:
                        cursor.execute(
                            "SELECT id, price, category, image_url FROM products WHERE supplier_id=%s AND name=%s LIMIT 1",
                            (supplier_id, p["name"]),
                        )
                    row = cursor.fetchone()
                    if row:
                        prod_id, old_price, old_cat, old_img = row
                        cat = (
                            old_cat
                            if (old_cat and (not p.get("category") or len(old_cat) > len(p.get("category", ""))))
                            else p.get("category", "")
                        )
                        img = p.get("image") or old_img or ""

                        if abs(float(old_price) - float(p["price"])) > 0.01:
                            cursor.execute(
                                "UPDATE products SET name=%s, price=%s, category=%s, image_url=%s, is_available=1, is_missing=0, updated_at=NOW() WHERE id=%s",
                                (p["name"], p["price"], cat, img, prod_id),
                            )
                            cursor.execute(
                                "INSERT INTO price_history (product_id, price, recorded_at) VALUES (%s, %s, NOW())",
                                (prod_id, p["price"]),
                            )
                            updated += 1
                        else:
                            cursor.execute(
                                "UPDATE products SET name=%s, category=%s, image_url=%s, is_available=1, is_missing=0, updated_at=NOW() WHERE id=%s",
                                (p["name"], cat, img, prod_id),
                            )
                            skipped += 1
                    else:
                        cursor.execute(
                            "INSERT INTO products (supplier_id, sku, name, price, category, image_url, is_available, is_new, created_at, updated_at) "
                            "VALUES (%s,%s,%s,%s,%s,%s,1,%s,NOW(),NOW())",
                            (
                                supplier_id,
                                p.get("sku", ""),
                                p["name"],
                                p["price"],
                                p.get("category", ""),
                                p.get("image") or "",
                                0 if is_new_supplier else 1,
                            ),
                        )
                        new_pid = cursor.lastrowid
                        if new_pid:
                            cursor.execute(
                                "INSERT INTO price_history (product_id, price, recorded_at) VALUES (%s, %s, NOW())",
                                (new_pid, p["price"]),
                            )
                        inserted += 1
                except Exception as row_err:
                    errors += 1
                    logger.error(f"PDF入库单行失败 sku={p.get('sku')}: {row_err}")

        # 同步该 PDF 供应商的缺货商品状态（仅当本次导入商品数达到原有在售商品数的阈值比例时执行，避免新品增补册或子目录误标主目录缺货）
        marked_missing = 0
        with db.connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT missing_threshold FROM suppliers WHERE id=%s", (supplier_id,))
            r_th = cur.fetchone()
            threshold_pct = (r_th[0] if r_th and r_th[0] else 80) / 100.0
            cur.execute(
                "SELECT COUNT(*) FROM products WHERE supplier_id=%s AND is_available=1 AND is_missing=0",
                (supplier_id,),
            )
            active_cnt = cur.fetchone()[0] or 0

        if active_cnt == 0 or len(all_products) >= active_cnt * threshold_pct:
            res_missing = db.mark_pdf_supplier_missing(supplier_id)
            marked_missing = res_missing.get("marked_missing", 0)
        else:
            logger.info(
                f"[{source_label}] 本次导入 {len(all_products)} 条 < 在售 {active_cnt} 条的 {threshold_pct:.0%}（增补/分册目录），跳过整店缺货覆盖标记"
            )

        summary_msg = (
            f"[{source_label}] {filename} -> 解析 {len(all_products)} 条 | "
            f"新增 {inserted} | 调价 {updated} | 未变 {skipped} | 缺货标记 {marked_missing}"
        )
        logger.info(summary_msg)
        db.finish_crawl_log(log_id, "success", 1, len(all_products), errors, summary_msg)

        return {
            "success": True,
            "parsed": len(all_products),
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "errors": errors,
            "missing": marked_missing,
            "message": summary_msg,
        }
    except Exception as e:
        err_msg = f"[{source_label}] {filename} 解析入库异常: {e}"
        logger.exception(err_msg)
        db.finish_crawl_log(log_id, "failed", 0, 0, 1, err_msg)
        raise


class WhatsAppMonitor:
    """
    基于 Playwright 持久化上下文的 WhatsApp Web PDF 自动监控器
    """

    def __init__(self, config_path: str, db: DatabaseManager, images_dir: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.db = db
        self.images_dir = images_dir

        self.profile_dir = os.path.abspath(
            os.path.join(ROOT_DIR, self.config.get("profile_dir", ".whatsapp_profile"))
        )
        self.downloads_dir = os.path.abspath(
            os.path.join(ROOT_DIR, self.config.get("downloads_dir", "downloads/whatsapp"))
        )
        state_file = os.path.abspath(
            os.path.join(ROOT_DIR, self.config.get("state_file", "downloads/whatsapp/processed_state.json"))
        )
        os.makedirs(self.downloads_dir, exist_ok=True)
        self.state = ProcessedState(state_file)
        self.detector = PDFSupplierDetector(self.config, self.db)
        self._active_chat_name: str = ""
        self._current_clicking_msg_id: str = ""
        self._download_lock = asyncio.Lock()
        self._last_download_outcome: Optional[Dict[str, Any]] = None
        # 记录每个会话的最新消息快照: {contact_name: {"preview": str, "unread": int}}
        self._chat_snapshots: Dict[str, Dict[str, Any]] = {}
        self._snapshots_initialized: bool = False
        # 记录每个联系人上次发送邮件提醒的时间戳 (秒)，用于实现“同一个联系人一分钟只触发一次”
        self._contact_last_email_ts: Dict[str, float] = {}
        # 记录已扫描过最新 PDF 预览的会话签名，避免无新 PDF 时反复点击会话清除未读状态
        self._checked_pdf_previews: set = set()

    def _load_config(self) -> dict:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def reload_config(self):
        """每次轮询前热重载配置文件，修改 whatsapp_config.json 无需重启脚本"""
        try:
            self.config = self._load_config()
            self.detector.config = self.config
        except Exception as e:
            logger.warning(f"重载配置失败: {e}")

    def _match_monitored_chat(self, title: str) -> Optional[dict]:
        """检查左侧会话列表中的聊天标题是否在白名单内"""
        if not title:
            return None
        t_low = title.strip().lower()
        for item in self.config.get("monitored_chats", []):
            if not item.get("enabled", True):
                continue
            cname = (item.get("chat_name") or "").strip().lower()
            keywords = [k.strip().lower() for k in item.get("keywords", []) if k.strip()]
            if cname == "*" or (cname and cname in t_low) or any(kw in t_low for kw in keywords):
                return item
        return None

    @staticmethod
    def _is_pdf_preview(text: str) -> bool:
        """判断列表预览或消息文本是否包含 PDF 文件特征"""
        if not text:
            return False
        t = text.strip()
        if ".pdf" in t.lower():
            return True
        if re.search(r"\bpdf\b", t, re.I):
            return True
        if re.search(r"•\s*\d+\s*(?:页|p[aá]g|page)", t, re.I):
            return True
        return False

    @staticmethod
    def _is_trivial_catalog_caption(text: str) -> bool:
        """
        判断跟随 PDF 一起发出的短文本是否仅为空白或常规目录问候语（如 'Hola', 'Buen día', 'Catálogo actualizado'），
        若包含实质性对话、提问或订单沟通则返回 False（归为需要通知用户的其他内容）。
        """
        if not text:
            return True
        clean = text.strip()
        if not clean:
            return True
        if "?" in clean or "？" in clean or len(clean) > 70:
            return False
        pattern = re.compile(
            r"^[\s,!¡.…:;\-—]*"
            r"(?:hola|buen\s*d[ií]a|buenos\s*d[ií]as|buenas(?:\s*tardes|\s*noches)?|"
            r"te\s*paso(?:\s*el|\s*la)?|adjunto|env[ií]o|"
            r"cat[aá]logo(?:\s*nuevo|\s*actualizado|\s*general|\s*octubre|\s*noviembre|\s*diciembre)?|"
            r"lista(?:\s*de\s*precios)?(?:\s*nueva|\s*actualizada)?|nuevos\s*ingresos)"
            r"(?:[\s,!¡.…:;\-—]+(?:hola|buen\s*d[ií]a|buenos\s*d[ií]as|buenas(?:\s*tardes|\s*noches)?|"
            r"te\s*paso(?:\s*el|\s*la)?|adjunto|env[ií]o|"
            r"cat[aá]logo(?:\s*nuevo|\s*actualizado|\s*general)?|"
            r"lista(?:\s*de\s*precios)?(?:\s*nueva|\s*actualizada)?|nuevos\s*ingresos|gracias|saludos))*[\s,!¡.…:;\-—]*$",
            re.I,
        )
        return bool(pattern.match(clean))

    async def _handle_browser_download(self, download):
        """
        全局下载事件处理器：
        无论是脚本自动点击下载的 PDF，还是用户在浏览器里手动点击下载的 PDF，
        都会自动触发识别并导入到对应的供应商，并将判定结果记录到 self._last_download_outcome。
        """
        async with self._download_lock:
            self._last_download_outcome = None
            try:
                suggested_name = download.suggested_filename or f"whatsapp_{int(datetime.now().timestamp())}.pdf"
                ext = os.path.splitext(suggested_name)[1].lower()

                date_dir = os.path.join(self.downloads_dir, datetime.now().strftime("%Y%m%d"))
                os.makedirs(date_dir, exist_ok=True)
                save_path = os.path.join(date_dir, suggested_name)

                # 若同名文件已存在，加时间戳后缀避免覆盖
                if os.path.exists(save_path):
                    base, extension = os.path.splitext(suggested_name)
                    save_path = os.path.join(date_dir, f"{base}_{datetime.now().strftime('%H%M%S')}{extension}")

                logger.info(f"[下载捕获] 正在接收文件: {suggested_name} (来自会话: {self._active_chat_name or '未知'})")
                await download.save_as(save_path)
                logger.info(f"[下载完成] 已保存至: {save_path}")

                if ext != ".pdf":
                    logger.info(f"[跳过解析] 非 PDF 文件 ({suggested_name})，仅归档保存。")
                    self._last_download_outcome = {
                        "is_catalogo": False,
                        "filename": suggested_name,
                        "save_path": save_path,
                        "reason": "非PDF文件",
                    }
                    return

                sha256 = compute_file_sha256(save_path)
                msg_id = self._current_clicking_msg_id

                if self.state.is_file_processed(sha256):
                    prev = self.state.file_hashes.get(sha256, {})
                    imp = prev.get("import_result", {})
                    is_cat = bool(imp.get("success") and imp.get("parsed", 0) > 0)
                    logger.info(
                        f"[去重跳过] 文件 {suggested_name} (SHA256={sha256[:10]}...) "
                        f"已于 {prev.get('processed_at')} 导入过 ({prev.get('supplier_name')})"
                    )
                    if msg_id:
                        self.state.mark_processed(msg_id, sha256, prev)
                    self._last_download_outcome = {
                        "is_catalogo": is_cat,
                        "already_processed": True,
                        "filename": suggested_name,
                        "save_path": save_path,
                        "supplier_name": prev.get("supplier_name", ""),
                        "import_result": imp,
                        "reason": (
                            f"Catalogo已导入过 ({prev.get('supplier_name')}, 共{imp.get('parsed', 0)}条商品)"
                            if is_cat
                            else "文件已处理过但非有效商品目录(Catalogo)"
                        ),
                    }
                    return

                # 识别该 PDF 属于哪个供应商
                match = self.detector.identify(
                    pdf_path=save_path,
                    filename=suggested_name,
                    chat_name=self._active_chat_name,
                )
                if not match:
                    logger.warning(
                        f"[未能识别为Catalogo] 文件={suggested_name}, 会话={self._active_chat_name}。"
                        f"非已知供应商商品目录或需人工查看。"
                    )
                    self._last_download_outcome = {
                        "is_catalogo": False,
                        "filename": suggested_name,
                        "save_path": save_path,
                        "reason": f"文件 '{suggested_name}' 未能识别为已知供应商的商品目录(Catalogo)",
                    }
                    return

                supplier_id = match["supplier_id"]
                supplier_name = match["supplier_name"]
                parser_id = match["parser_id"]
                logger.info(
                    f"[识别成功] 文件 '{suggested_name}' -> 供应商: {supplier_name} (ID={supplier_id}), "
                    f"解析器: {parser_id} | 依据: [{match['match_source']}] {match['reason']}"
                )

                # 在后台线程中执行耗时的 PDF 解析与数据库入库，避免阻塞 Playwright 事件循环
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None,
                    import_pdf_to_supplier,
                    self.db,
                    save_path,
                    supplier_id,
                    parser_id,
                    self.images_dir,
                    f"WhatsApp:{self._active_chat_name or supplier_name}",
                )

                # 将归档文件重命名加上供应商前缀，方便人工查阅
                sup_dir = os.path.join(self.downloads_dir, supplier_name)
                os.makedirs(sup_dir, exist_ok=True)
                archived_path = os.path.join(
                    sup_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{suggested_name}"
                )
                try:
                    shutil.copy2(save_path, archived_path)
                except Exception:
                    archived_path = save_path

                self.state.mark_processed(
                    msg_id=msg_id,
                    sha256=sha256,
                    info={
                        "filename": suggested_name,
                        "archived_path": archived_path,
                        "chat_name": self._active_chat_name,
                        "supplier_id": supplier_id,
                        "supplier_name": supplier_name,
                        "parser_id": parser_id,
                        "match_reason": match["reason"],
                        "import_result": result,
                    },
                )
                is_cat = bool(result.get("success") and result.get("parsed", 0) > 0)
                self._last_download_outcome = {
                    "is_catalogo": is_cat,
                    "filename": suggested_name,
                    "save_path": archived_path,
                    "supplier_name": supplier_name,
                    "import_result": result,
                    "reason": result.get("message", ""),
                }
            except Exception as e:
                logger.exception(f"[下载处理失败] {e}")
                self._last_download_outcome = {
                    "is_catalogo": False,
                    "filename": "未知文件.pdf",
                    "reason": f"下载或解析异常: {e}",
                }

    async def _get_active_chat_title(self, page) -> str:
        """获取右侧当前打开的聊天窗口标题"""
        try:
            el = await page.query_selector("#main header span[title]")
            if el:
                title = await el.get_attribute("title")
                if title:
                    return title.strip()
        except Exception:
            pass
        return self._active_chat_name

    async def _dismiss_modals(self, page):
        """自动关闭 WhatsApp Web 登录后的新手引导/通知提示遮罩层"""
        for _ in range(3):
            try:
                dialog = await page.query_selector('div[role="dialog"][aria-modal="true"]')
                if not dialog:
                    break
                btn = await dialog.query_selector("button")
                if btn:
                    await btn.click(force=True)
                else:
                    await page.keyboard.press("Escape")
                await asyncio.sleep(0.8)
            except Exception:
                break

    async def _close_pdf_viewer(self, page):
        """关闭 WhatsApp Web 的全屏 PDF 预览遮罩层，恢复到会话界面"""
        try:
            close_btn = await page.query_selector(
                'button[aria-label="关闭"], button[aria-label="Close"], button[aria-label="Cerrar"]'
            )
            if close_btn:
                await close_btn.click(force=True)
                await asyncio.sleep(0.8)
            else:
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.8)
        except Exception:
            pass

    async def _scan_current_chat_for_pdfs(self, page, chat_title: str) -> List[Dict[str, Any]]:
        """
        扫描当前打开的聊天窗口中的最近消息（从最新往上找），寻找 PDF 附件并触发下载与入库，
        返回每个找到的 PDF 的判定与导入结果列表。
        """
        self._active_chat_name = chat_title
        limit = int(self.config.get("scan_recent_messages_limit", 5))
        max_pdfs_per_chat = int(self.config.get("max_pdfs_per_chat", 1))
        outcomes: List[Dict[str, Any]] = []

        try:
            msg_elements = await page.query_selector_all("#main div[data-id]")
            if not msg_elements:
                return outcomes

            # 从最新一条消息往前扫描，优先抓取最新的一份报价单
            recent_msgs = list(reversed(msg_elements[-limit:]))
            downloaded_in_chat = 0

            for msg_el in recent_msgs:
                if downloaded_in_chat >= max_pdfs_per_chat:
                    break

                msg_id = await msg_el.get_attribute("data-id") or ""
                text_content = (await msg_el.inner_text() or "").strip()
                has_pdf_name = ".pdf" in text_content.lower()
                has_pdf_badge = bool(re.search(r"\bPDF\b", text_content))

                if not (has_pdf_name or has_pdf_badge):
                    continue

                if self.state.is_message_processed(msg_id):
                    rec = self.state.message_ids.get(msg_id, {})
                    imp = rec.get("import_result", {})
                    is_cat = bool(imp.get("success") and imp.get("parsed", 0) > 0)
                    outcomes.append(
                        {
                            "is_catalogo": is_cat,
                            "already_processed": True,
                            "filename": rec.get("filename", "已处理文件.pdf"),
                            "supplier_name": rec.get("supplier_name", ""),
                            "import_result": imp,
                            "reason": imp.get("message") or f"已导入 ({rec.get('supplier_name')})",
                        }
                    )
                    downloaded_in_chat += 1
                    continue

                # 第一步：点击气泡内的 PDF 卡片（打开 WhatsApp Web 内部 PDF 预览层）
                target_click = await msg_el.query_selector(
                    'div[role="button"][title*=".pdf"], div[role="button"][title*=".PDF"], '
                    'span[data-icon="document-PDF-icon"]'
                )
                if not target_click:
                    continue

                btn_title = (await target_click.get_attribute("title") or "").strip()
                logger.info(
                    f"[{chat_title}] 发现未处理最新 PDF 消息 ({btn_title or msg_id[:20]})，正在打开预览并下载..."
                )
                self._current_clicking_msg_id = msg_id
                self._last_download_outcome = None
                try:
                    await target_click.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await target_click.click(force=True)

                    # 第二步：等待顶部预览栏出现“下载”按钮并点击触发浏览器下载
                    dl_selector = 'button[aria-label="下载"], button[aria-label="Download"], button[aria-label="Descargar"]'
                    dl_btn = await page.wait_for_selector(dl_selector, timeout=15000)
                    if dl_btn:
                        async with page.expect_download(timeout=90000):
                            await dl_btn.click(force=True)
                        downloaded_in_chat += 1

                    # 等待后台下载保存与数据库入库完成
                    await asyncio.sleep(2.0)
                    async with self._download_lock:
                        await asyncio.sleep(0.5)

                    if self._last_download_outcome:
                        outcomes.append(self._last_download_outcome)
                    else:
                        outcomes.append(
                            {
                                "is_catalogo": False,
                                "filename": btn_title or "未知.pdf",
                                "reason": "下载未返回解析结果",
                            }
                        )
                except Exception as dl_err:
                    logger.warning(f"[{chat_title}] 下载 PDF ({btn_title}) 异常: {dl_err}")
                    outcomes.append(
                        {
                            "is_catalogo": False,
                            "filename": btn_title or "未知.pdf",
                            "reason": f"下载失败: {dl_err}",
                        }
                    )
                finally:
                    self._current_clicking_msg_id = ""
                    # 第三步：务必关闭全屏 PDF 预览层，否则会挡住后续切换左侧联系人的点击
                    await self._close_pdf_viewer(page)
        except Exception as e:
            logger.warning(f"扫描会话 [{chat_title}] PDF 消息异常: {e}")

        return outcomes

    async def _inspect_chat_messages_and_pdfs(
        self, page, chat_title: str, unread_count: int
    ) -> Dict[str, Any]:
        """
        当收到包含 PDF 的消息满 150 秒无新消息时，点进会话检查内部消息内容与 PDF 文件：
        - 判断 PDF 是否为可导入的商品目录（Catalogo），若确定是则已在下载回调中直接入库；
        - 同时检查该批次未读消息中是否夹杂了其他非 Catalogo 的文字/媒体消息。
        """
        chat_spans = await page.query_selector_all("#pane-side span[title]")
        target_sp = None
        for sp in chat_spans:
            raw_t = (await sp.get_attribute("title") or "").strip()
            clean_t = re.sub(r"[\u202a-\u202e]", "", raw_t).strip()
            if clean_t == chat_title:
                target_sp = sp
                break

        if not target_sp:
            return {
                "is_pure_catalogo": False,
                "pdf_outcomes": [],
                "other_messages": ["[无法在列表中定位该联系人窗口]"],
                "all_messages": [],
                "summary": "无法定位会话窗口",
            }

        other_non_catalog_msgs: List[str] = []
        all_bubble_summaries: List[str] = []
        pdf_outcomes: List[Dict[str, Any]] = []

        try:
            self._active_chat_name = chat_title
            await self._dismiss_modals(page)
            await target_sp.click(force=True)
            await asyncio.sleep(3.0)

            # 提取会话内对方发来的最近未读消息气泡 (data-id 以 false_ 开头代表对方发来)
            incoming_els = await page.query_selector_all('#main div[data-id^="false_"]')
            if not incoming_els:
                incoming_els = await page.query_selector_all("#main div[data-id]")

            inspect_cnt = max(1, min(int(unread_count or 1), 10))
            recent_incoming = incoming_els[-inspect_cnt:] if incoming_els else []

            for el in recent_incoming:
                raw_txt = (await el.inner_text() or "").strip()
                lines = [
                    re.sub(r"[\u202a-\u202e]", "", ln).strip()
                    for ln in raw_txt.splitlines()
                    if ln.strip()
                ]
                # 去掉末尾的纯时间行 (例如 "10:05" 或 "上午10:05")
                while lines and re.match(r"^(?:[上下]午\s*)?\d{1,2}:\d{2}(?:\s*[AP]M)?$", lines[-1], re.I):
                    lines.pop()

                pdf_btn = await el.query_selector(
                    'div[role="button"][title*=".pdf"], div[role="button"][title*=".PDF"], '
                    'span[data-icon="document-PDF-icon"]'
                )
                is_pdf_bubble = bool(
                    pdf_btn
                    or ".pdf" in raw_txt.lower()
                    or re.search(r"\bPDF\b", raw_txt)
                )
                if is_pdf_bubble:
                    pdf_title = ""
                    if pdf_btn:
                        pdf_title = (await pdf_btn.get_attribute("title") or "").strip()
                    if not pdf_title and lines:
                        pdf_title = lines[0]
                    all_bubble_summaries.append(f"[PDF文件] {pdf_title or '文档.pdf'}")
                    # 检查同一个 PDF 气泡下是否附带了除文件名和页数/大小元数据之外的长文字说明
                    extra_lines = [
                        ln
                        for ln in lines
                        if ln != pdf_title
                        and ".pdf" not in ln.lower()
                        and not re.match(
                            r"^(?:\d+\s*(?:页|p[aá]g\w*|pages?)|PDF|\d+(?:[.,]\d+)?\s*(?:KB|MB|GB|B)|•)+$",
                            ln,
                            re.I,
                        )
                    ]
                    extra_txt = " ".join(extra_lines).strip()
                    if extra_txt and not self._is_trivial_catalog_caption(extra_txt):
                        other_non_catalog_msgs.append(extra_txt)
                        all_bubble_summaries.append(f"[附言] {extra_txt}")
                else:
                    msg_txt = " ".join(lines).strip() or "[图片/语音/其他媒体消息]"
                    all_bubble_summaries.append(msg_txt)
                    if not self._is_trivial_catalog_caption(msg_txt):
                        other_non_catalog_msgs.append(msg_txt)

            # 下载并尝试按 Catalogo 解析入库
            pdf_outcomes = await self._scan_current_chat_for_pdfs(page, chat_title)

            # 检查完毕后退出右侧聊天面板，避免后续来消息不显示未读红点
            await page.keyboard.press("Escape")
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"[150秒PDF检查] 检查会话 [{chat_title}] 异常: {e}")

        is_pure_catalogo = (
            bool(pdf_outcomes)
            and all(o.get("is_catalogo", False) for o in pdf_outcomes)
            and len(other_non_catalog_msgs) == 0
        )
        summary = "; ".join(o.get("reason") or o.get("filename", "") for o in pdf_outcomes)
        return {
            "is_pure_catalogo": is_pure_catalogo,
            "pdf_outcomes": pdf_outcomes,
            "other_messages": other_non_catalog_msgs,
            "all_messages": all_bubble_summaries,
            "summary": summary,
        }

    async def _extract_pane_chats(self, page) -> List[Dict[str, Any]]:
        """从左侧 #pane-side 会话列表中提取当前可见会话的联系人、消息预览、未读红点状态及未读数"""
        raw_rows = await page.eval_on_selector_all(
            '#pane-side div[role="row"], #pane-side div[role="listitem"]',
            """els => els.map((el, idx) => {
                const titles = Array.from(el.querySelectorAll('span[title]')).map(s => s.getAttribute('title') || '');
                const ariaBadges = Array.from(el.querySelectorAll('span[aria-label]')).map(s => s.getAttribute('aria-label') || '');
                const isOutgoing = Boolean(
                    el.querySelector('span[data-icon^="status-"], span[data-icon*="msg-check"], span[data-icon*="msg-dblcheck"]')
                );
                const lines = (el.innerText || '').split('\\n').map(s => s.trim()).filter(Boolean);
                return {idx, titles, ariaBadges, isOutgoing, lines};
            })""",
        )
        chats = []
        seen_names = set()
        for r in raw_rows:
            titles = [re.sub(r"[\u202a-\u202e]", "", t).strip() for t in r.get("titles", []) if t]
            if not titles:
                continue
            contact_name = titles[0]
            if not contact_name or contact_name in seen_names:
                continue
            seen_names.add(contact_name)

            preview_text = titles[1] if len(titles) > 1 else ""
            lines = [re.sub(r"[\u202a-\u202e]", "", ln).strip() for ln in r.get("lines", []) if ln]
            time_str = ""
            if len(lines) >= 2:
                for ln in lines[1:3]:
                    if ln != contact_name and ln != preview_text:
                        time_str = ln
                        break
            if not preview_text and len(lines) >= 3:
                preview_text = lines[-1]

            unread_count = 0
            has_red_dot = False
            for badge in r.get("ariaBadges", []):
                b_clean = badge.strip()
                m = re.search(r"(\d+)\s*(?:条?未读|unread|mensaje|no le[ií]d)", b_clean, re.I)
                if m:
                    unread_count = max(unread_count, int(m.group(1)))
                    has_red_dot = True
                elif re.search(r"(?:未读消息|^未读$|unread message|no le[ií]do)", b_clean, re.I):
                    unread_count = max(unread_count, 1)
                    has_red_dot = True

            chats.append(
                {
                    "idx": r.get("idx", 999),
                    "contact_name": contact_name,
                    "preview_text": preview_text,
                    "time_str": time_str,
                    "unread_count": unread_count,
                    "has_red_dot": has_red_dot,
                    "is_outgoing": bool(r.get("isOutgoing", False)),
                }
            )
        return chats

    async def _check_new_messages_and_notify(self, page) -> List[Dict[str, Any]]:
        """
        未读红点与 150 秒 PDF 智能检测逻辑：
        1. 计数结束前如果红点消失（用户在对话中已读），立即取消计时，不发送提醒。
        2. 如果期间红点消失后又重新出现新的红点，以最后一个红点出现时间重新计数；收到新消息时刷新最后消息时间。
        3. 【150秒 PDF 规则】：如果收到消息 150 秒后没有新消息，并且发现包含 PDF，就点进会话查看消息内容：
           - 如果确定是 Catalogo（商品目录且无其他需人工处理的对话内容），不发邮件，直接导入数据库；
           - 如果是其他内容（非 Catalogo 的 PDF，或同时发了其他聊天内容），向 QQ 邮箱发送提醒。
        4. 【180秒普通未读规则】：如果不包含 PDF，红点持续满 180 秒未消失，向 QQ 邮箱发送未读提醒。
        """
        import time

        chats = await self._extract_pane_chats(page)
        if not chats:
            return []

        now_ts = time.time()
        msg_notify_cfg = self.config.get("message_notify", {})
        notify_enabled = bool(msg_notify_cfg.get("enabled", True)) and bool(
            self.config.get("email_notify", {}).get("enabled", True)
        )
        unread_delay_sec = float(
            msg_notify_cfg.get("unread_delay_sec", msg_notify_cfg.get("cooldown_sec", 180))
        )
        pdf_inspect_delay_sec = float(msg_notify_cfg.get("pdf_inspect_delay_sec", 150))
        only_monitored = bool(msg_notify_cfg.get("only_monitored_chats", False))

        # 首次启动：记录基线快照（启动前已存在的历史陈旧红点标记为已处理，除非后续收到新消息内容）
        if not self._snapshots_initialized:
            for c in chats:
                p_txt = c["preview_text"]
                self._chat_snapshots[c["contact_name"]] = {
                    "has_red_dot": c["has_red_dot"],
                    "dot_appeared_ts": now_ts if c["has_red_dot"] else 0.0,
                    "last_msg_ts": now_ts if c["has_red_dot"] else 0.0,
                    "has_pdf": self._is_pdf_preview(p_txt) if c["has_red_dot"] else False,
                    "pdf_inspected": True if c["has_red_dot"] else False,
                    "notified": True if c["has_red_dot"] else False,
                    "preview": p_txt,
                    "messages": [p_txt] if p_txt else [],
                    "unread": c["unread_count"],
                    "time_str": c["time_str"],
                }
                self._checked_pdf_previews.add(f"{c['contact_name']}::{p_txt}::{c['time_str']}")
            self._snapshots_initialized = True
            logger.info(
                f"[静默监控已就绪] 已建立 {len(self._chat_snapshots)} 个会话的初始状态 | "
                f"PDF无新消息 {int(pdf_inspect_delay_sec)} 秒进会话检查(Catalogo直导不发邮件/其他内容通知) | "
                f"普通未读红点满 {int(unread_delay_sec)} 秒发邮件提醒..."
            )
            return chats

        for c in chats:
            cname = c["contact_name"]
            has_dot = c["has_red_dot"]
            preview = c["preview_text"]
            unread = c["unread_count"]
            time_str = c["time_str"]

            if only_monitored and not self._match_monitored_chat(cname):
                continue

            tracker = self._chat_snapshots.get(cname)

            # 情况 A：当前没有红点（未读已消除）
            if not has_dot:
                if tracker and tracker.get("has_red_dot"):
                    if not tracker.get("notified"):
                        elapsed = int(now_ts - tracker.get("dot_appeared_ts", now_ts))
                        logger.info(
                            f"[红点已消失] 联系人 [{cname}] 在倒计时结束前已读 (持续 {elapsed}s)，不发送提醒。"
                        )
                self._chat_snapshots[cname] = {
                    "has_red_dot": False,
                    "dot_appeared_ts": 0.0,
                    "last_msg_ts": 0.0,
                    "has_pdf": False,
                    "pdf_inspected": False,
                    "notified": False,
                    "preview": preview,
                    "messages": [],
                    "unread": 0,
                    "time_str": time_str,
                }
                continue

            # 情况 B：当前存在未读红点 (has_dot == True)，且红点是新出现的（或消失后重新出现的）
            if not tracker or not tracker.get("has_red_dot"):
                is_pdf = self._is_pdf_preview(preview)
                self._chat_snapshots[cname] = {
                    "has_red_dot": True,
                    "dot_appeared_ts": now_ts,
                    "last_msg_ts": now_ts,
                    "has_pdf": is_pdf,
                    "pdf_inspected": False,
                    "notified": False,
                    "preview": preview,
                    "messages": [preview] if preview else [],
                    "unread": unread,
                    "time_str": time_str,
                }
                target_wait = int(pdf_inspect_delay_sec) if is_pdf else int(unread_delay_sec)
                logger.info(
                    f"[红点开始计数] 联系人 [{cname}] 出现未读红点 (内容: '{preview}', PDF={is_pdf})，"
                    f"开始 {target_wait} 秒检测倒计时..."
                )
                continue

            # 情况 C：红点一直存在，检测是否有新消息到达
            has_new_msg = (preview != tracker.get("preview")) or (unread > tracker.get("unread", 0))
            if has_new_msg:
                is_pdf = self._is_pdf_preview(preview)
                tracker["last_msg_ts"] = now_ts
                if tracker.get("notified"):
                    # 此前已处理过，但又收到了新消息 -> 重新开启新一轮计数
                    tracker["dot_appeared_ts"] = now_ts
                    tracker["notified"] = False
                    tracker["pdf_inspected"] = False
                    tracker["has_pdf"] = is_pdf
                    tracker["messages"] = [preview] if preview else []
                    logger.info(
                        f"[新内容重置计数] 联系人 [{cname}] 收到新内容 ('{preview}', PDF={is_pdf})，重新开始计时..."
                    )
                else:
                    if is_pdf:
                        tracker["has_pdf"] = True
                    if preview:
                        msgs_list = tracker.setdefault("messages", [])
                        if not msgs_list or msgs_list[-1] != preview:
                            msgs_list.append(preview)
                    logger.info(
                        f"[收到新消息-刷新计时] 联系人 [{cname}] 收到新内容 ('{preview}', PDF={tracker.get('has_pdf')})，"
                        f"无新消息计时已重置为 0s..."
                    )
                tracker["preview"] = preview
                tracker["unread"] = unread
                tracker["time_str"] = time_str
                continue

            tracker["preview"] = preview
            tracker["unread"] = unread
            tracker["time_str"] = time_str

            if tracker.get("notified"):
                continue

            quiet_elapsed = now_ts - tracker.get("last_msg_ts", tracker.get("dot_appeared_ts", now_ts))
            dot_elapsed = now_ts - tracker.get("dot_appeared_ts", now_ts)

            # 分支 1：包含 PDF，且收到消息已满 150 秒无新消息 -> 进入会话检查内容
            if tracker.get("has_pdf") and not tracker.get("pdf_inspected"):
                if quiet_elapsed >= pdf_inspect_delay_sec:
                    tracker["pdf_inspected"] = True
                    tracker["notified"] = True
                    logger.info(
                        f"[150秒PDF无新消息-进入检查] 联系人 [{cname}] 收到 PDF 后已满 {int(quiet_elapsed)} 秒无新消息，"
                        f"正在点进会话检查内容是否为 Catalogo..."
                    )
                    inspect_res = await self._inspect_chat_messages_and_pdfs(page, cname, unread)
                    self._checked_pdf_previews.add(f"{cname}::{preview}::{time_str}")

                    if inspect_res["is_pure_catalogo"]:
                        logger.info(
                            f"[确认Catalogo-直接导入不发邮件] 联系人 [{cname}] 发送的 PDF 确认为 Catalogo "
                            f"({inspect_res['summary']})，已直接导入数据库，不发送邮件提醒。"
                        )
                    elif notify_enabled:
                        all_msgs = inspect_res.get("all_messages") or tracker.get("messages") or [preview]
                        msgs_formatted = "\n".join(f"  - {m}" for m in all_msgs)
                        pdf_notes = "\n".join(
                            f"  - {o.get('filename')}: {o.get('reason')}"
                            for o in inspect_res.get("pdf_outcomes", [])
                        )
                        subject = f"【WhatsApp消息提醒】{cname}（包含非Catalogo或其他消息内容）"
                        body = (
                            f"WhatsApp 消息提醒（收到 PDF 满 {int(quiet_elapsed)} 秒无新消息，经进入会话检查包含其他内容）：\n\n"
                            f"联系人/群组：{cname}\n"
                            f"消息时间  ：{time_str or '刚刚'}\n"
                            f"未读条数  ：{unread}\n"
                            f"会话内消息内容：\n{msgs_formatted}\n"
                        )
                        if pdf_notes:
                            body += f"\nPDF 检查结果：\n{pdf_notes}\n"
                        logger.info(
                            f"[150秒PDF检查-触发通知] 联系人 [{cname}] 会话内包含非 Catalogo 或其他消息内容，正在发送 QQ 邮箱提醒..."
                        )
                        loop = asyncio.get_running_loop()
                        loop.run_in_executor(None, send_email_notification, self.config, subject, body, "")
                continue

            # 分支 2：普通非 PDF 消息，红点持续满 180 秒未消失 -> 发送邮件提醒
            if not tracker.get("has_pdf") and notify_enabled:
                if dot_elapsed >= unread_delay_sec:
                    tracker["notified"] = True
                    msgs_list = tracker.get("messages") or ([preview] if preview else ["[图片/媒体/文件]"])
                    msgs_formatted = "\n".join(f"  - {m}" for m in msgs_list)
                    subject = f"【WhatsApp未读提醒】{cname}（已超过{int(unread_delay_sec // 60)}分钟未读）"
                    body = (
                        f"WhatsApp 消息未读提醒（红点已持续 {int(dot_elapsed)} 秒未消失）：\n\n"
                        f"联系人/群组：{cname}\n"
                        f"消息时间  ：{time_str or '刚刚'}\n"
                        f"未读条数  ：{unread}\n"
                        f"捕获到的消息内容：\n{msgs_formatted}\n"
                    )
                    logger.info(
                        f"[倒计时结束-触发提醒] 联系人 [{cname}] 红点已持续 {int(dot_elapsed)} 秒未消失，正在发送 QQ 邮箱提醒..."
                    )
                    loop = asyncio.get_running_loop()
                    loop.run_in_executor(None, send_email_notification, self.config, subject, body, "")

        return chats

    async def _poll_once(self, page):
        """单次轮询：1) 静默检测 150 秒 PDF 自动核验入库与 180 秒红点提醒；2) 用户已读的白名单供应商新 PDF 兜底入库"""
        self.reload_config()
        await self._dismiss_modals(page)

        # 1. 检测所有会话的未读红点状态与 150 秒 PDF 自动进会话检查
        chats = await self._check_new_messages_and_notify(page)

        # 2. 兜底检查：如果某个白名单供应商发了 PDF，且用户在 150 秒内自己点开读过了（红点已消失），
        #    但该 PDF 预览还未入库过，则静默补扫入库（不发邮件）
        for c in chats:
            title = c["contact_name"]
            preview = c["preview_text"]
            time_str = c["time_str"]
            matched_cfg = self._match_monitored_chat(title)
            if not matched_cfg:
                continue

            # 有未读红点时统一交由上面 _check_new_messages_and_notify 的 150 秒规则处理，绝不提前点开消掉红点
            if c.get("has_red_dot"):
                continue

            if not self._is_pdf_preview(preview):
                continue

            sig = f"{title}::{preview}::{time_str}"
            if sig in self._checked_pdf_previews:
                continue

            chat_spans = await page.query_selector_all("#pane-side span[title]")
            target_sp = None
            for sp in chat_spans:
                raw_t = (await sp.get_attribute("title") or "").strip()
                clean_t = re.sub(r"[\u202a-\u202e]", "", raw_t).strip()
                if clean_t == title:
                    target_sp = sp
                    break

            if not target_sp:
                continue

            try:
                logger.info(f"[已读PDF兜底入库] 打开白名单供应商会话检查已读新 PDF: {title} (预览: {preview})")
                self._active_chat_name = title
                await self._dismiss_modals(page)
                await target_sp.click(force=True)
                await asyncio.sleep(3.0)
                await self._scan_current_chat_for_pdfs(page, title)
                self._checked_pdf_previews.add(sig)
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.warning(f"切换会话 [{title}] 异常: {e}")

        # 3. 执行 AI Agent 远程投递的 WhatsApp 操作指令队列 (wa_command_queue.json)
        await self._execute_wa_remote_commands(page, chats)

    async def _execute_wa_remote_commands(self, page, chats: List[Dict[str, Any]]):
        """处理由 AI Agent 投递到 downloads/whatsapp/wa_command_queue.json 的远程 WhatsApp 控制指令"""
        cmd_file = os.path.join(self.downloads_dir, "wa_command_queue.json")
        res_file = os.path.join(self.downloads_dir, "wa_command_result.json")
        if not os.path.exists(cmd_file):
            return

        try:
            with open(cmd_file, "r", encoding="utf-8") as f:
                cmd = json.load(f)
            os.remove(cmd_file)
        except Exception as e:
            logger.warning(f"读取远程指令文件失败: {e}")
            return

        action = (cmd.get("action") or "").strip().lower()
        contact_kw = (cmd.get("contact") or "").strip()
        text_to_send = (cmd.get("text") or "").strip()
        limit = int(cmd.get("limit", 15))
        cmd_id = cmd.get("cmd_id", "")

        logger.info(f"[远程指令执行] 收到 Agent 指令: action={action}, contact={contact_kw}")
        result: Dict[str, Any] = {
            "cmd_id": cmd_id,
            "action": action,
            "contact": contact_kw,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": False,
        }

        try:
            if action == "list_chats":
                result["success"] = True
                result["chats"] = chats
            else:
                chat_spans = await page.query_selector_all("#pane-side span[title]")
                target_sp = None
                matched_title = ""
                kw_lower = contact_kw.lower()
                for sp in chat_spans:
                    raw_t = (await sp.get_attribute("title") or "").strip()
                    clean_t = re.sub(r"[\u202a-\u202e]", "", raw_t).strip()
                    if clean_t and (clean_t.lower() == kw_lower or kw_lower in clean_t.lower()):
                        target_sp = sp
                        matched_title = clean_t
                        break

                if not target_sp:
                    result["error"] = f"未在左侧会话列表中找到匹配 '{contact_kw}' 的联系人"
                else:
                    self._active_chat_name = matched_title
                    await self._dismiss_modals(page)
                    await target_sp.click(force=True)
                    await asyncio.sleep(2.5)

                    if action == "read_chat":
                        msg_els = await page.query_selector_all("#main div[data-id]")
                        recent_els = msg_els[-limit:] if msg_els else []
                        messages = []
                        for el in recent_els:
                            mid = await el.get_attribute("data-id") or ""
                            sender_role = "我" if mid.startswith("true_") else matched_title
                            raw_txt = (await el.inner_text() or "").strip()
                            lines = [
                                re.sub(r"[\u202a-\u202e]", "", ln).strip()
                                for ln in raw_txt.splitlines()
                                if ln.strip()
                            ]
                            messages.append({"sender": sender_role, "text": " | ".join(lines)})
                        result["success"] = True
                        result["matched_contact"] = matched_title
                        result["messages"] = messages

                    elif action == "send_message":
                        input_box = await page.query_selector('#main footer div[contenteditable="true"]')
                        if not input_box:
                            result["error"] = "未找到聊天输入框"
                        else:
                            await input_box.click()
                            await asyncio.sleep(0.3)
                            await input_box.fill(text_to_send)
                            await asyncio.sleep(0.3)
                            await page.keyboard.press("Enter")
                            await asyncio.sleep(1.5)
                            result["success"] = True
                            result["matched_contact"] = matched_title
                            result["sent_text"] = text_to_send

                    elif action == "scan_pdf":
                        outcomes = await self._scan_current_chat_for_pdfs(page, matched_title)
                        result["success"] = True
                        result["matched_contact"] = matched_title
                        result["pdf_outcomes"] = outcomes

                    await page.keyboard.press("Escape")
                    await asyncio.sleep(0.5)
        except Exception as e:
            result["error"] = str(e)
            logger.warning(f"[远程指令异常] {e}")

        try:
            with open(res_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"写入远程指令结果失败: {e}")

    def _build_browser_args(self, headless: bool) -> List[str]:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-gpu",
        ]
        return args

    async def run_forever(self):
        """启动持久化浏览器并静默持续监控 WhatsApp Web（150秒PDF检查直导 + 3分钟未读红点邮件提醒）"""
        from playwright.async_api import async_playwright

        headless = bool(self.config.get("headless", True))
        poll_interval = int(self.config.get("poll_interval_sec", 5))
        unread_delay = int(self.config.get("message_notify", {}).get("unread_delay_sec", 180))
        pdf_delay = int(self.config.get("message_notify", {}).get("pdf_inspect_delay_sec", 150))

        logger.info("=" * 65)
        logger.info("WhatsApp 静默实时监控启动 (150秒PDF智能直导 + 3分钟未读红点提醒)")
        logger.info(f"静默无头模式    : {'开启 (--headless=new)' if headless else '关闭 (显示窗口)'}")
        logger.info(f"轮询检测间隔    : {poll_interval} 秒")
        logger.info(f"PDF 150秒智能检测: 收到PDF满 {pdf_delay} 秒无新消息进会话检查 -> Catalogo直导不发邮件 / 其他内容发邮件")
        logger.info(f"普通未读延迟提醒: {unread_delay} 秒 (红点不消失才发邮件，消失重出则按最后一次重新计时)")
        monitored_names = [
            c.get("chat_name") for c in self.config.get("monitored_chats", []) if c.get("enabled", True)
        ]
        logger.info(f"PDF入库白名单   : {monitored_names}")
        logger.info("=" * 65)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                channel="chrome",
                headless=headless,
                accept_downloads=True,
                viewport={"width": 1280, "height": 860},
                args=self._build_browser_args(headless),
            )
            page = context.pages[0] if context.pages else await context.new_page()
            page.on("download", lambda d: asyncio.create_task(self._handle_browser_download(d)))

            logger.info("正在后台静默加载 https://web.whatsapp.com ...")
            if not headless:
                await page.bring_to_front()
            await page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)

            await self._wait_for_login_with_qr_capture(page, timeout_sec=300)
            logger.info("WhatsApp Web 已成功登录！开始静默监控所有新消息与供应商 PDF...")

            while True:
                try:
                    await self._poll_once(page)
                except Exception as loop_err:
                    logger.error(f"轮询周期异常: {loop_err}")
                await asyncio.sleep(poll_interval)

    async def _wait_for_login_with_qr_capture(self, page, timeout_sec: int = 180) -> bool:
        """等待 WhatsApp 登录成功；若处于二维码页面，自动截取最新二维码保存到本地方便扫码"""
        login_selector = '#pane-side, div[aria-label*="Chat list"], div[aria-label*="聊天列表"], div[aria-label*="Lista de chats"], div[role="grid"]'
        qr_path = os.path.join(self.downloads_dir, "whatsapp_qr.png")
        elapsed = 0
        interval = 3

        logger.info(f"等待 WhatsApp Web 会话加载（若需扫码，二维码将同步保存至 {qr_path}）...")
        while elapsed < timeout_sec:
            logged_in = await page.query_selector(login_selector)
            if logged_in:
                return True

            qr_canvas = await page.query_selector("canvas")
            if qr_canvas:
                try:
                    await page.screenshot(path=qr_path)
                    extra_qr = os.environ.get("WHATSAPP_QR_COPY_PATH")
                    if extra_qr:
                        shutil.copy2(qr_path, extra_qr)
                except Exception:
                    pass

            await asyncio.sleep(interval)
            elapsed += interval

        return False

    async def run_once(self) -> List[Dict[str, Any]]:
        """执行单次 WhatsApp Web 静默检查（供 Agent 定时任务调用），检查完毕后自动关闭浏览器并返回本次处理结果"""
        from playwright.async_api import async_playwright

        headless = bool(self.config.get("headless", True))
        before_hashes = set(self.state.file_hashes.keys())

        logger.info("启动单次 WhatsApp 供应商 PDF 静默检测...")
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                channel="chrome",
                headless=headless,
                accept_downloads=True,
                viewport={"width": 1280, "height": 860},
                args=self._build_browser_args(headless),
            )
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                page.on("download", lambda d: asyncio.create_task(self._handle_browser_download(d)))

                if not headless:
                    await page.bring_to_front()
                await page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)
                ok = await self._wait_for_login_with_qr_capture(page, timeout_sec=180)
                if not ok:
                    logger.warning("等待 WhatsApp Web 登录超时（3分钟内未完成扫码登录），本次检测退出。")
                    return []
                logger.info("WhatsApp Web 登录成功！正在静默扫描监控会话...")
                await asyncio.sleep(3.0)

                await self._poll_once(page)
                # 等待可能正在进行的下载与入库任务完成
                async with self._download_lock:
                    await asyncio.sleep(1.0)
            finally:
                await context.close()

        after_hashes = set(self.state.file_hashes.keys())
        new_hashes = after_hashes - before_hashes
        return [self.state.file_hashes[h] for h in new_hashes]

