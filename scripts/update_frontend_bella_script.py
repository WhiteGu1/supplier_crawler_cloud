with open('frontend/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('window.copyBellaConsoleScript')
start_target = text.find('  var scriptItems = [];', idx)
end_target = text.find('  function fallbackCopy', idx)

new_code_gen = r'''  var scriptItems = [];
  list.forEach(function(it) {
    var wcId = String(it.sku || '').trim();
    if (/^\d+$/.test(wcId)) {
      scriptItems.push({
        id: parseInt(wcId, 10),
        qty: parseInt(it.quantity || 1, 10),
        name: (it.name || '').trim().slice(0, 40),
        pkg: parseInt(it.package_qty || 1, 10),
        sub: parseInt(it.sub_pack_qty || 1, 10)
      });
    }
  });

  if (!scriptItems.length) {
    showToast('未能提取到 Bella Central 商品的网站数字 ID', 'error');
    return;
  }

  var jsonStr = JSON.stringify(scriptItems);
  var code = '(async () => {\n'
    + '  const items = ' + jsonStr + ';\n\n'
    + '  console.log(\'🚀 开始向 Bella Central 购物车导入 \' + items.length + \' 件商品 (先清空后导入)...\');\n'
    + '  let nonce = \'\';\n'
    + '  try {\n'
    + '    const cr = await fetch(\'/wp-json/wc/store/v1/cart\', { credentials: \'include\' });\n'
    + '    nonce = cr.headers.get(\'Nonce\') || \'\';\n'
    + '    if (cr.ok) {\n'
    + '      const cData = await cr.json();\n'
    + '      const existing = cData.items || [];\n'
    + '      if (existing.length > 0) {\n'
    + '        console.log(`🧹 检测到购物车已有 ${existing.length} 件商品，正在先清空旧商品...`);\n'
    + '        for (const ex of existing) {\n'
    + '          const rmRes = await fetch(\'/wp-json/wc/store/v1/cart/remove-item\', {\n'
    + '            method: \'POST\',\n'
    + '            headers: { \'Content-Type\': \'application/json\', \'Nonce\': nonce },\n'
    + '            credentials: \'include\',\n'
    + '            body: JSON.stringify({ key: ex.key })\n'
    + '          });\n'
    + '          const n = rmRes.headers.get(\'Nonce\');\n'
    + '          if (n) nonce = n;\n'
    + '        }\n'
    + '        console.log(\'✨ 旧购物车已彻底清空！准备开始导入新商品...\');\n'
    + '      }\n'
    + '    }\n'
    + '  } catch(e) {}\n\n'
    + '  let added = 0;\n'
    + '  let skipped = 0;\n'
    + '  let failed = 0;\n\n'
    + '  for (let i = 0; i < items.length; i++) {\n'
    + '    const it = items[i];\n'
    + '    try {\n'
    + '      let targetId = it.id;\n'
    + '      let targetQty = it.qty;\n'
    + '      let note = \'单品\';\n\n'
    + '      try {\n'
    + '        const pr = await fetch(`/wp-json/wc/store/v1/products/${it.id}`);\n'
    + '        if (pr.ok) {\n'
    + '          const prod = await pr.json();\n'
    + '          if (prod.is_in_stock === false) {\n'
    + '            console.warn(`[${i + 1}/${items.length}] ❌ 售罄断货已跳过: ${it.name}`);\n'
    + '            skipped++;\n'
    + '            continue;\n'
    + '          }\n'
    + '          if (prod.type === \'variable\' && prod.variations && prod.variations.length > 0) {\n'
    + '            const vars = prod.variations.map(v => {\n'
    + '              const val = (v.attributes && v.attributes[0] ? v.attributes[0].value : \'\').toLowerCase();\n'
    + '              const m = val.match(/\\d+/);\n'
    + '              return { id: v.id, val: val, count: m ? parseInt(m[0], 10) : 1 };\n'
    + '            });\n'
    + '            let chosen = vars.find(v => v.count === it.pkg && it.qty % it.pkg === 0);\n'
    + '            if (!chosen && it.sub > 1) chosen = vars.find(v => v.count === it.sub && it.qty % it.sub === 0);\n'
    + '            if (!chosen) chosen = vars.find(v => v.count > 1 && it.qty % v.count === 0);\n'
    + '            if (!chosen) chosen = vars.find(v => v.count === 1) || vars[0];\n'
    + '            if (chosen) {\n'
    + '              targetId = chosen.id;\n'
    + '              targetQty = (chosen.count > 1 && it.qty >= chosen.count && it.qty % chosen.count === 0) ? (it.qty / chosen.count) : it.qty;\n'
    + '              note = `${chosen.val || chosen.id} x ${targetQty}`;\n'
    + '            }\n'
    + '          }\n'
    + '        }\n'
    + '      } catch(e) {}\n\n'
    + '      const res = await fetch(\'/wp-json/wc/store/v1/cart/add-item\', {\n'
    + '        method: \'POST\',\n'
    + '        headers: { \'Content-Type\': \'application/json\', \'Nonce\': nonce },\n'
    + '        credentials: \'include\',\n'
    + '        body: JSON.stringify({ id: targetId, quantity: targetQty })\n'
    + '      });\n'
    + '      const nextNonce = res.headers.get(\'Nonce\');\n'
    + '      if (nextNonce) nonce = nextNonce;\n\n'
    + '      if (res.ok) {\n'
    + '        added++;\n'
    + '        console.log(`[${i + 1}/${items.length}] ✅ 加购成功 (${note}): ${it.name}`);\n'
    + '      } else {\n'
    + '        const err = await res.json().catch(() => ({}));\n'
    + '        console.warn(`[${i + 1}/${items.length}] ⚠️ 加购受阻: ${it.name}`, err.message || res.statusText);\n'
    + '        failed++;\n'
    + '      }\n'
    + '    } catch(err) {\n'
    + '      console.error(`[${i + 1}/${items.length}] ❌ 异常: ${it.name}`, err);\n'
    + '      failed++;\n'
    + '    }\n'
    + '    await new Promise(r => setTimeout(r, 60));\n'
    + '  }\n\n'
    + '  console.log(`🎉 导入执行完毕！成功: ${added}, 缺货跳过: ${skipped}, 失败: ${failed}`);\n'
    + '  alert(`🎉 成功将 ${added} / ${items.length} 件商品加入 Bella Central 购物车！(缺货 ${skipped} 件)\\n点击确定跳转查看。`);\n'
    + '  location.href = \'/carro/\';\n'
    + '})();';\n\n'''

text = text[:start_target] + new_code_gen + text[end_target:]
with open('frontend/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated frontend/dashboard.html successfully!")

# Update mobile.html
with open('frontend/mobile.html', 'r', encoding='utf-8') as f:
    m_text = f.read()

m_idx = m_text.find('window.copyMobileBellaConsoleScript')
m_start = m_text.find('  var scriptItems = [];', m_idx)
m_end = m_text.find('  if (navigator.clipboard', m_idx)

m_text = m_text[:m_start] + new_code_gen + m_text[m_end:]
with open('frontend/mobile.html', 'w', encoding='utf-8') as f:
    f.write(m_text)
print("Updated frontend/mobile.html successfully!")
