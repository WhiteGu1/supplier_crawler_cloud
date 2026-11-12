import json

with open('scripts/resolved_bella_cart.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

resolved = data['resolved']

payload = []
for r in resolved:
    payload.append({
        'id': r['id'],
        'qty': r['qty'],
        'name': r['name'][:35].replace('"', "'"),
        'spec': r.get('var_label', 'simple')
    })

items_json = json.dumps(payload, ensure_ascii=False)

script = f"""(async () => {{
  // Bella Central 一键清空并加购脚本 (自动适配规格变体)
  // 共计 {len(payload)} 件在售商品
  const items = {items_json};

  console.log(`🚀 开始处理 Bella Central 购物车 (目标商品数: ${{items.length}})...`);

  // 1. 获取 Nonce 并自动清空购物车中的旧商品
  let nonce = '';
  try {{
    const cr = await fetch('/wp-json/wc/store/v1/cart', {{ credentials: 'include' }});
    nonce = cr.headers.get('Nonce') || '';
    if (cr.ok) {{
      const cData = await cr.json();
      const existing = cData.items || [];
      if (existing.length > 0) {{
        console.log(`🧹 检测到网站购物车已有 ${{existing.length}} 件商品，正在先彻底清空...`);
        for (const ex of existing) {{
          const rmRes = await fetch('/wp-json/wc/store/v1/cart/remove-item', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json', 'Nonce': nonce }},
            credentials: 'include',
            body: JSON.stringify({{ key: ex.key }})
          }});
          const n = rmRes.headers.get('Nonce');
          if (n) nonce = n;
        }}
        console.log('✨ 旧购物车已彻底清空！准备开始导入新商品...');
      }} else {{
        console.log('🛒 网站购物车当前为空，直接开始导入...');
      }}
    }}
  }} catch(e) {{
    console.warn('清空购物车检查异常，继续执行加购:', e);
  }}

  let added = 0;
  let failed = 0;

  // 2. 依次加入新商品
  for (let i = 0; i < items.length; i++) {{
    const it = items[i];
    try {{
      const res = await fetch('/wp-json/wc/store/v1/cart/add-item', {{
        method: 'POST',
        headers: {{
          'Content-Type': 'application/json',
          'Nonce': nonce
        }},
        credentials: 'include',
        body: JSON.stringify({{
          id: it.id,
          quantity: it.qty
        }})
      }});

      const nextNonce = res.headers.get('Nonce');
      if (nextNonce) nonce = nextNonce;

      if (res.ok) {{
        added++;
        console.log(`[${{i + 1}}/${{items.length}}] ✅ 加购成功: ${{it.name}} (${{it.spec}} x ${{it.qty}})`);
      }} else {{
        const errJson = await res.json().catch(() => ({{}}));
        console.warn(`[${{i + 1}}/${{items.length}}] ⚠️ 加购受阻: ${{it.name}} (ID: ${{it.id}})`, errJson.message || res.statusText);
        failed++;
      }}
    }} catch(err) {{
      console.error(`[${{i + 1}}/${{items.length}}] ❌ 异常: ${{it.name}}`, err);
      failed++;
    }}
    await new Promise(r => setTimeout(r, 60));
  }}

  console.log(`🎉 导入执行完毕！成功导入: ${{added}}, 失败: ${{failed}}`);
  alert(`🎉 成功将 ${{added}} / ${{items.length}} 件商品加入 Bella Central 购物车！点击确定跳转查看。`);
  location.href = '/carro/';
}})();"""

with open('scripts/bella_console_script.js', 'w', encoding='utf-8') as f:
    f.write(script)

print("Generated scripts/bella_console_script.js with clear-cart feature successfully!")
