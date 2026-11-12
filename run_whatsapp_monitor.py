# -*- coding: utf-8 -*-
"""
run_whatsapp_monitor.py
WhatsApp 供应商 PDF 自动化抓取与智能入库启动脚本

用法示例：
1. 启动持久化浏览器并持续监控 WhatsApp Web：
   python run_whatsapp_monitor.py

2. 仅测试本地某个 PDF 文件会被识别为哪个供应商与解析器（不入库）：
   python run_whatsapp_monitor.py --identify pdf_parsers/samples/CATALOGO_2026_panda.pdf

3. 自动识别本地某个 PDF 文件并直接导入对应供应商数据库：
   python run_whatsapp_monitor.py --import-pdf pdf_parsers/samples/CATALOGO_2026_panda.pdf
"""

import argparse
import asyncio
import json
import logging
import os
import sys

from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

load_dotenv(os.path.join(ROOT_DIR, ".env"))

from database.db_manager import DatabaseManager
from crawler.whatsapp_monitor import (
    WhatsAppMonitor,
    PDFSupplierDetector,
    import_pdf_to_supplier,
    send_email_notification,
)


def setup_logging():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(ROOT_DIR, "crawler.log"), encoding="utf-8"),
        ],
    )
    for noisy in ("pdfminer", "pdfplumber", "PIL", "urllib3", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def init_db() -> DatabaseManager:
    return DatabaseManager(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "admin123"),
        database=os.getenv("DB_NAME", "supplier_crawler"),
    )


def main():
    parser = argparse.ArgumentParser(description="WhatsApp 供应商 PDF 自动抓取与入库工具")
    parser.add_argument(
        "--config",
        default=os.path.join(ROOT_DIR, "whatsapp_config.json"),
        help="配置文件路径 (默认: whatsapp_config.json)",
    )
    parser.add_argument(
        "--identify",
        metavar="PDF_PATH",
        help="仅测试识别指定 PDF 属于哪个供应商及解析器（不执行入库）",
    )
    parser.add_argument(
        "--import-pdf",
        metavar="PDF_PATH",
        help="自动识别指定 PDF 所属供应商并直接解析入库",
    )
    parser.add_argument(
        "--chat",
        default="",
        help="配合 --identify 或 --import-pdf 模拟来自某个 WhatsApp 聊天窗口名称",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="执行单次 WhatsApp 检测后退出（适用于 Agent 定时自动化任务）",
    )
    parser.add_argument(
        "--test-email",
        action="store_true",
        help="发送一封测试邮件到 whatsapp_config.json 配置的收件箱",
    )
    args = parser.parse_args()

    setup_logging()
    db = init_db()
    images_dir = os.path.join(ROOT_DIR, "images")
    os.makedirs(images_dir, exist_ok=True)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    if args.test_email:
        ok = send_email_notification(
            config=config,
            subject="【供应商爬虫系统】WhatsApp 监控邮件通知测试",
            body_text=(
                "你好！\n\n"
                "这是一封来自供应商爬虫管理系统（WhatsApp 供应商 PDF 自动监控模块）的测试邮件。\n"
                "每日 10:00 自动检测到新的供应商 PDF 并完成入库后，系统会将入库汇总结果发送至此邮箱。\n"
            ),
        )
        sys.exit(0 if ok else 1)

    detector = PDFSupplierDetector(config, db)

    if args.identify:
        pdf_path = os.path.abspath(args.identify)
        if not os.path.exists(pdf_path):
            print(f"[错误] 文件不存在: {pdf_path}")
            sys.exit(1)
        match = detector.identify(pdf_path=pdf_path, chat_name=args.chat)
        print("\n=== PDF 供应商自动识别结果 ===")
        print(json.dumps(match, ensure_ascii=False, indent=2))
        return

    if args.import_pdf:
        pdf_path = os.path.abspath(args.import_pdf)
        if not os.path.exists(pdf_path):
            print(f"[错误] 文件不存在: {pdf_path}")
            sys.exit(1)
        match = detector.identify(pdf_path=pdf_path, chat_name=args.chat)
        if not match:
            print(f"[失败] 无法自动识别该 PDF 所属供应商: {pdf_path}")
            sys.exit(1)
        print(
            f"[识别成功] 供应商: {match['supplier_name']} (ID={match['supplier_id']}), "
            f"解析器: {match['parser_id']} | 依据: {match['reason']}"
        )
        res = import_pdf_to_supplier(
            db=db,
            pdf_path=pdf_path,
            supplier_id=match["supplier_id"],
            parser_id=match["parser_id"],
            images_dir=images_dir,
            source_label="命令行测试导入",
        )
        print("\n=== 导入结果 ===")
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    monitor = WhatsAppMonitor(config_path=args.config, db=db, images_dir=images_dir)
    if args.once:
        results = asyncio.run(monitor.run_once())
        print("\n=== 单次 WhatsApp 检测结果 ===")
        print(json.dumps({"new_imported_count": len(results), "items": results}, ensure_ascii=False, indent=2))
        if results and config.get("email_notify", {}).get("enabled") and config.get("email_notify", {}).get("smtp_auth_code"):
            lines = [f"本次 WhatsApp 自动检测共处理 {len(results)} 份新 PDF：\n"]
            for idx, item in enumerate(results, 1):
                ir = item.get("import_result", {})
                lines.append(
                    f"{idx}. 供应商: {item.get('supplier_name')} | 文件: {item.get('filename')}\n"
                    f"   解析结果: {ir.get('message', '')}\n"
                )
            send_email_notification(
                config=config,
                subject=f"【供应商爬虫】WhatsApp 新增 {len(results)} 份供应商 PDF 报价单汇报",
                body_text="\n".join(lines),
            )
        return

    # 默认启动持续监控
    try:
        asyncio.run(monitor.run_forever())
    except KeyboardInterrupt:
        print("\n[退出] 已停止 WhatsApp 监控。")


if __name__ == "__main__":
    main()
