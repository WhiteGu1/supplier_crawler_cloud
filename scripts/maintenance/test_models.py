import sys, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Administrator\Desktop\modelroute_api')
from modelroute_api import call_model

models = ['pool-deepseek-v4-flash', 'pool-kimi-k2.6', 'pool-glm-5.2', 'pool-minimax-m3']
for m in models:
    t0 = time.time()
    r = call_model(prompt='回复OK', model=m, max_tokens=100, timeout=60, base_url='http://127.0.0.1:52374/v1/chat/completions')
    elapsed = time.time() - t0
    err = r.get('error')
    content = r['content'][:50] if r.get('content') else ''
    print(f'{m}: {elapsed:.1f}s, err={err}, content=[{content}]')
