"""测试 Gateway OpenAI 兼容端点"""
import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# 从 openclaw.json 读取 token
with open(r"C:\Users\Administrator\.qclaw\openclaw.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)
token = cfg["gateway"]["auth"]["token"]

r = requests.post(
    "http://127.0.0.1:61233/v1/chat/completions",
    json={
        "model": "openclaw/main",
        "messages": [
            {"role": "system", "content": "You are a JSON API. Only output JSON, no other text."},
            {"role": "user", "content": 'Output this exact JSON: {"msg":"hello"}'}
        ],
        "max_tokens": 50
    },
    headers={
        "Authorization": f"Bearer {token}",
        "x-openclaw-model": "qclaw/pool-minimax-m3"
    },
    timeout=120
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")
