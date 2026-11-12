# -*- coding: utf-8 -*-
"""
supplier_crawler/email_agent_bridge.py
QQ 邮箱 <-> Antigravity AI Agent 远程双向对话与控制桥接器

核心功能：
1. --wait 模式（后台监听唤醒）：
   通过 IMAP SSL (imap.qq.com:993) 持续监听 1813634420@qq.com 收件箱。
   一旦收到用户发来（或直接回复）的新邮件（自动过滤带 X-Antigravity-Auto 头的系统通知邮件及外部垃圾邮件），
   立即解析邮件主题、正文指令与引用上下文，输出到标准输出并退出进程（Exit 0），从而自动唤醒 Antigravity AI Agent 执行任务！
2. --send-reply 模式（发送 Agent 回复邮件）：
   Agent 完成任务后调用此命令将执行结果通过 QQ 邮箱发回给用户，并重新启动 --wait 监听下一条指令。
3. --list-sessions / --read-session 模式（跨会话查看与对话）：
   读取本机所有 Antigravity 历史与活跃会话 (brain/<conversation-id>)，支持通过邮件查看或接续任意会话的工作。
4. --wa-cmd 模式（操控后台 WhatsApp 会话）：
   向正在运行的 whatsapp_monitor 投递指令（查看会话列表、读取某联系人聊天记录、代发 WhatsApp 消息、强制扫描 PDF）。
"""

import argparse
import email
from email.header import decode_header
from email.message import Message
from email.utils import parseaddr
import glob
import html
import imaplib
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from crawler.whatsapp_monitor import send_email_notification

CONFIG_PATH = os.path.join(ROOT_DIR, "whatsapp_config.json")
STATE_PATH = os.path.join(ROOT_DIR, "downloads", "whatsapp", "email_bridge_state.json")
WA_CMD_FILE = os.path.join(ROOT_DIR, "downloads", "whatsapp", "wa_command_queue.json")
WA_RES_FILE = os.path.join(ROOT_DIR, "downloads", "whatsapp", "wa_command_result.json")
BRAIN_DIR = os.path.expanduser(r"~\.gemini\antigravity\brain")


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_bridge_state() -> dict:
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_uid": 0}


def save_bridge_state(state: dict):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    state["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def decode_mime_str(val: Optional[str]) -> str:
    if not val:
        return ""
    parts = decode_header(val)
    out = []
    for content, charset in parts:
        if isinstance(content, bytes):
            enc = charset or "utf-8"
            try:
                out.append(content.decode(enc, errors="replace"))
            except LookupError:
                out.append(content.decode("utf-8", errors="replace"))
        else:
            out.append(str(content))
    return "".join(out).strip()


def html_to_plain(html_str: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html_str)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", text)
    text = re.sub(r"(?s)<.*?>", "", text)
    text = html.unescape(text)
    lines = [ln.strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def extract_email_body(msg: Message) -> str:
    plain_parts = []
    html_parts = []

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition") or "")
            if "attachment" in disp.lower():
                continue
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            charset = part.get_content_charset() or "utf-8"
            try:
                decoded = payload.decode(charset, errors="replace")
            except LookupError:
                decoded = payload.decode("utf-8", errors="replace")
            if ctype == "text/plain":
                plain_parts.append(decoded)
            elif ctype == "text/html":
                html_parts.append(decoded)
    else:
        payload = msg.get_payload(decode=True)
        if payload is not None:
            charset = msg.get_content_charset() or "utf-8"
            try:
                decoded = payload.decode(charset, errors="replace")
            except LookupError:
                decoded = payload.decode("utf-8", errors="replace")
            if msg.get_content_type() == "text/html":
                html_parts.append(decoded)
            else:
                plain_parts.append(decoded)

    if plain_parts:
        return "\n".join(plain_parts).strip()
    if html_parts:
        return html_to_plain("\n".join(html_parts)).strip()
    return ""


def split_reply_and_quote(full_body: str) -> Tuple[str, str]:
    """将用户回复的正文与邮件底部的引用历史拆分开"""
    markers = [
        r"^-{3,}\s*原始邮件\s*-{3,}",
        r"^-{3,}\s*Original\s*Message\s*-{3,}",
        r"^在\s*\d{4}年.*写道[:：]",
        r"^On\s+.*wrote:$",
        r"^发件人[:：]\s*",
        r"^From:\s*",
    ]
    lines = full_body.splitlines()
    for idx, ln in enumerate(lines):
        s = ln.strip()
        if any(re.match(pat, s, re.I) for pat in markers):
            user_text = "\n".join(lines[:idx]).strip()
            quoted_text = "\n".join(lines[idx:]).strip()
            return user_text, quoted_text
    return full_body.strip(), ""


def get_max_uid(imap: imaplib.IMAP4_SSL) -> int:
    typ, data = imap.uid("search", None, "ALL")
    if typ != "OK" or not data or not data[0]:
        return 0
    uids = [int(x) for x in data[0].split() if x.isdigit()]
    return max(uids) if uids else 0


def wait_for_incoming_email(poll_interval: int = 6):
    """阻塞监听 QQ 邮箱收件箱，一旦收到用户发来的新指令邮件则输出详情并退出 (唤醒 Agent)"""
    cfg = load_config()
    email_cfg = cfg.get("email_notify", {})
    imap_host = email_cfg.get("imap_host", "imap.qq.com")
    imap_port = int(email_cfg.get("imap_port", 993))
    user_email = (email_cfg.get("sender_email") or "1813634420@qq.com").strip().lower()
    auth_code = email_cfg.get("smtp_auth_code", "")

    state = load_bridge_state()
    last_uid = int(state.get("last_uid", 0))

    # 首次运行时同步当前最大 UID 为基线
    if last_uid <= 0:
        imap = imaplib.IMAP4_SSL(imap_host, imap_port)
        imap.login(user_email, auth_code)
        imap.select("INBOX")
        last_uid = get_max_uid(imap)
        imap.logout()
        save_bridge_state({"last_uid": last_uid})
        print(f"[EmailBridge] 已初始化收件箱基线 UID={last_uid}，正在静默等待来自 {user_email} 的远程指令邮件...", flush=True)
    else:
        print(f"[EmailBridge] 继续监听 {user_email} 新邮件 (当前基线 UID={last_uid})...", flush=True)

    while True:
        try:
            imap = imaplib.IMAP4_SSL(imap_host, imap_port)
            imap.login(user_email, auth_code)
            imap.select("INBOX")

            search_criterion = f"UID {last_uid + 1}:*"
            typ, data = imap.uid("search", None, search_criterion)
            if typ == "OK" and data and data[0]:
                new_uids = sorted(int(u) for u in data[0].split() if int(u) > last_uid)
                for uid in new_uids:
                    ftyp, fdata = imap.uid("fetch", str(uid), "(RFC822)")
                    last_uid = max(last_uid, uid)
                    save_bridge_state({"last_uid": last_uid})

                    if ftyp != "OK" or not fdata or not fdata[0]:
                        continue
                    raw_email = fdata[0][1]
                    if not isinstance(raw_email, bytes):
                        continue

                    msg = email.message_from_bytes(raw_email)

                    # 1. 过滤由系统/Agent 自动发出的邮件（所有系统发出的邮件均带有 X-Antigravity-Auto: 1 头）
                    if msg.get("X-Antigravity-Auto"):
                        continue

                    subject = decode_mime_str(msg.get("Subject"))
                    from_hdr = decode_mime_str(msg.get("From"))
                    _, from_addr = parseaddr(from_hdr)
                    from_addr_low = (from_addr or from_hdr).strip().lower()

                    # 2. 安全校验：仅允许用户本人邮箱发来的邮件控制 Agent
                    if user_email not in from_addr_low:
                        continue

                    full_body = extract_email_body(msg)
                    user_instruction, quoted_context = split_reply_and_quote(full_body)

                    imap.logout()

                    payload = {
                        "event": "USER_EMAIL_COMMAND",
                        "uid": uid,
                        "received_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "from": from_addr_low,
                        "subject": subject,
                        "instruction": user_instruction or subject,
                        "quoted_context": quoted_context[:1500] if quoted_context else "",
                    }
                    print("\n=== [收到用户远程邮件指令] ===", flush=True)
                    print(json.dumps(payload, ensure_ascii=False, indent=2), flush=True)
                    return

            imap.logout()
        except Exception as e:
            print(f"[EmailBridge] IMAP 轮询重试中: {e}", flush=True)

        time.sleep(poll_interval)


def list_antigravity_sessions(limit: int = 15) -> List[Dict[str, Any]]:
    """列出本机最近的 Antigravity 会话（包含会话ID、活跃时间、首条与最新用户消息）"""
    if not os.path.exists(BRAIN_DIR):
        return []

    sessions = []
    for cid in os.listdir(BRAIN_DIR):
        t_path = os.path.join(BRAIN_DIR, cid, ".system_generated", "logs", "transcript.jsonl")
        if not os.path.exists(t_path):
            continue
        try:
            mtime = os.path.getmtime(t_path)
            user_inputs = []
            with open(t_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if '"USER_INPUT"' not in line:
                        continue
                    try:
                        obj = json.loads(line)
                        if obj.get("type") == "USER_INPUT" and obj.get("content"):
                            raw_c = obj["content"]
                            raw_c = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", raw_c, flags=re.S)
                            raw_c = re.sub(r"<[^>]+>", "", raw_c).strip()
                            if raw_c:
                                user_inputs.append(raw_c[:120])
                    except Exception:
                        pass
            if not user_inputs:
                continue
            sessions.append(
                {
                    "conversation_id": cid,
                    "updated_at": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "mtime": mtime,
                    "first_prompt": user_inputs[0],
                    "latest_prompt": user_inputs[-1],
                    "turns": len(user_inputs),
                }
            )
        except Exception:
            pass

    sessions.sort(key=lambda x: x["mtime"], reverse=True)
    return sessions[:limit]


def read_antigravity_session(target: str, max_steps: int = 10) -> Dict[str, Any]:
    """根据会话 ID 前缀或关键词读取某个 Antigravity 会话的最近对话内容"""
    sessions = list_antigravity_sessions(limit=100)
    matched = None
    t_low = target.strip().lower()
    for s in sessions:
        if (
            s["conversation_id"].lower().startswith(t_low)
            or t_low in s["first_prompt"].lower()
            or t_low in s["latest_prompt"].lower()
        ):
            matched = s
            break

    if not matched:
        return {"success": False, "error": f"未找到匹配 '{target}' 的会话"}

    cid = matched["conversation_id"]
    t_path = os.path.join(BRAIN_DIR, cid, ".system_generated", "logs", "transcript.jsonl")
    messages = []
    try:
        with open(t_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    stype = obj.get("type")
                    content = (obj.get("content") or "").strip()
                    if stype == "USER_INPUT" and content:
                        clean_c = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", content, flags=re.S)
                        clean_c = re.sub(r"</?USER_REQUEST>", "", clean_c).strip()
                        if clean_c:
                            messages.append({"role": "User", "content": clean_c[:800]})
                    elif stype == "PLANNER_RESPONSE" and content:
                        messages.append({"role": "Agent", "content": content[:800]})
                except Exception:
                    pass
    except Exception as e:
        return {"success": False, "error": str(e)}

    return {
        "success": True,
        "session": matched,
        "recent_messages": messages[-max_steps:],
    }


def dispatch_wa_command(action: str, contact: str = "", text: str = "", limit: int = 15, timeout: int = 20) -> dict:
    """向正在运行的 whatsapp_monitor 守护进程投递指令并等待执行结果"""
    cmd_id = f"cmd_{int(time.time() * 1000)}"
    if os.path.exists(WA_RES_FILE):
        try:
            os.remove(WA_RES_FILE)
        except Exception:
            pass

    cmd_data = {
        "cmd_id": cmd_id,
        "action": action,
        "contact": contact,
        "text": text,
        "limit": limit,
    }
    os.makedirs(os.path.dirname(WA_CMD_FILE), exist_ok=True)
    with open(WA_CMD_FILE, "w", encoding="utf-8") as f:
        json.dump(cmd_data, f, ensure_ascii=False, indent=2)

    waited = 0.0
    while waited < timeout:
        if os.path.exists(WA_RES_FILE):
            try:
                with open(WA_RES_FILE, "r", encoding="utf-8") as f:
                    res = json.load(f)
                if res.get("cmd_id") == cmd_id:
                    return res
            except Exception:
                pass
        time.sleep(0.5)
        waited += 0.5

    return {"success": False, "error": "等待 whatsapp_monitor 执行指令超时，请确认守护进程正在运行"}


def main():
    parser = argparse.ArgumentParser(description="QQ Email <-> Antigravity AI Agent Bridge")
    parser.add_argument("--wait", action="store_true", help="阻塞监听新指令邮件并在收到时唤醒 Agent")
    parser.add_argument("--send-reply", action="store_true", help="向用户 QQ 邮箱发送 Agent 回复")
    parser.add_argument("--subject", type=str, default="【AI助手回复】远程指令执行结果", help="回复邮件标题")
    parser.add_argument("--body", type=str, default="", help="回复邮件正文")
    parser.add_argument("--body-file", type=str, default="", help="从文件读取回复邮件正文")
    parser.add_argument("--attach", type=str, nargs="*", default=[], help="要作为附件发送的文件路径列表")
    parser.add_argument("--list-sessions", action="store_true", help="列出本机最近的 Antigravity 会话")
    parser.add_argument("--read-session", type=str, default="", help="读取指定 ID 或关键词的 Antigravity 会话")
    parser.add_argument("--wa-cmd", type=str, default="", help="执行 WhatsApp 远程动作: list_chats|read_chat|send_message|scan_pdf")
    parser.add_argument("--contact", type=str, default="", help="WhatsApp 联系人名称或关键词")
    parser.add_argument("--text", type=str, default="", help="要发送的 WhatsApp 消息内容")
    args = parser.parse_args()

    if args.wait:
        wait_for_incoming_email()
    elif args.send_reply:
        cfg = load_config()
        body_content = args.body
        if args.body_file and os.path.exists(args.body_file):
            with open(args.body_file, "r", encoding="utf-8") as f:
                body_content = f.read()
        subj = args.subject
        if not subj.startswith("【AI助手"):
            subj = f"【AI助手回复】{subj}"
        send_email_notification(cfg, subj, body_content, attachments=args.attach)
    elif args.list_sessions:
        print(json.dumps(list_antigravity_sessions(limit=20), ensure_ascii=False, indent=2))
    elif args.read_session:
        print(json.dumps(read_antigravity_session(args.read_session), ensure_ascii=False, indent=2))
    elif args.wa_cmd:
        res = dispatch_wa_command(args.wa_cmd, args.contact, args.text)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
