"""调试 openclaw infer 输出"""
import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

OPENCLAW_BIN = r"C:\Program Files\QClaw\v0.2.31.600\resources\openclaw\config\bin\openclaw.cmd"
MODEL = "qclaw/pool-minimax-m3"

prompt = """为以下商品分配分类路径，输出JSON。

商品：
[{"id": 2, "name": "PERCHERO C/U"}, {"id": 4, "name": "NECESER C/U"}]

输出格式（只输出JSON）：
{"assignments":[{"id":2,"categories":["家居生活 > 衣帽架 > 挂衣架"]}],"new_categories":[]}"""

cmd = [OPENCLAW_BIN, "infer", "model", "run", "--gateway", "--model", MODEL, "--prompt", prompt, "--json"]
print(f"Running: {' '.join(cmd[:6])}...")
proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace")
print(f"Return code: {proc.returncode}")
print(f"STDOUT length: {len(proc.stdout)}")
print(f"STDERR length: {len(proc.stderr)}")
print(f"\n--- STDOUT (first 2000) ---")
print(proc.stdout[:2000])
print(f"\n--- STDERR (first 500) ---")
print(proc.stderr[:500])
