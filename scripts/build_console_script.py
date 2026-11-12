# -*- coding: utf-8 -*-
import sys
import json
import os

sys.path.insert(0, '.')
from database.db_manager import DatabaseManager

db = DatabaseManager('localhost', 3306, 'root', 'admin123', 'supplier_crawler')
items = db.get_cart_items()
bella = [it for it in items if 'bella' in (it.get('supplier_name') or '').lower() or it.get('supplier_id') == 18]

# 按照加入顺序或者 SKU 排序
bella_list = []
for it in bella:
    sku = int(str(it.get('sku')).strip())
    qty = int(it.get('quantity') or 1)
    name = (it.get('name') or '').strip()[:40]
    bella_list.append({"id": sku, "qty": qty, "name": name})

json_str = json.dumps(bella_list, ensure_ascii=False)

script = f"""(async () => {{
  const items = {json_str};

  console.log('🚀 开始向 Bella Central 购物车导入 ' + items.length + ' 件商品...');
  let added = 0;
  let failed = 0;

  for (let i = 0; i < items.length; i++) {{
    const it = items[i];
    try {{
      const fd = new FormData();
      fd.append('product_id', it.id);
      fd.append('quantity', it.qty);
      const res = await fetch('/?wc-ajax=add_to_cart', {{
        method: 'POST',
        body: fd
      }});
      if (res.ok) {{
        added++;
        console.log(`[${{i + 1}}/${{items.length}}] ✅ 已加购 (${{it.qty}}件): ${{it.name}} (ID: ${{it.id}})`);
      }} else {{
        // 备用加购方式 (GET 参数)
        await fetch(`/?add-to-cart=${{it.id}}&quantity=${{it.qty}}`);
        added++;
        console.log(`[${{i + 1}}/${{items.length}}] ✅ (GET方式)已加购 (${{it.qty}}件): ${{it.name}}`);
      }}
    }} catch(e) {{
      failed++;
      console.error(`[${{i + 1}}/${{items.length}}] ❌ 加购失败: ${{it.name}}`, e);
    }}
    // 稍微延迟 80ms 避免请求过频
    await new Promise(r => setTimeout(r, 80));
  }}

  console.log(`🎉 全部完成！成功: ${{added}}, 失败: ${{failed}}`);
  alert(`🎉 成功将 ${{added}} / ${{items.length}} 件商品加入 Bella Central 购物车！点击确定跳转查看购物车。`);
  location.href = '/carro/';
}})();"""

output_path = os.path.join(os.path.dirname(__file__), 'bella_console_import.js')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(script)

print(f"Generated {len(bella_list)} items import script successfully at: {output_path}")
