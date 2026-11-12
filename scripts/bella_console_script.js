(async () => {
  // Bella Central 一键清空并加购脚本 (自动适配规格变体)
  // 共计 110 件在售商品
  const items = [{"id": 75042, "qty": 2, "name": "DEDO DE PRACTICA CON UÑA CD:DH70539", "spec": "x6 unidad"}, {"id": 111479, "qty": 2, "name": "Strass Gemas Autoadhesivas SURTIDOS", "spec": "pack 12u"}, {"id": 173995, "qty": 5, "name": "Parches Para LABIOS Mascarilla TEI ", "spec": "pack-10u"}, {"id": 105697, "qty": 2, "name": "LIMPIADOR FACIAL SILICONA CD:HT-230", "spec": "pack x12u"}, {"id": 173991, "qty": 5, "name": "Parches Para Ojos Mascarilla TEI K3", "spec": "pack-10u"}, {"id": 71269, "qty": 4, "name": "MASCARA KERATINA 270G FIDELITE 6119", "spec": "simple"}, {"id": 71276, "qty": 4, "name": "MASCARA ALMENDRAS 270G FIDELITE 612", "spec": "simple"}, {"id": 153660, "qty": 2, "name": "Set de Belleza 5 en 1 &#8211; Kit C", "spec": "3-unidad"}, {"id": 204287, "qty": 2, "name": "KIT DE PERFUME + CREMA CORPORAL CD:", "spec": "simple"}, {"id": 196226, "qty": 1, "name": "CEPILLO LIMPIADOR Y EXFOLIANTE FACI", "spec": "6-unidad"}, {"id": 156192, "qty": 8, "name": "MASCARA CAPILAR SKALA", "spec": "simple"}, {"id": 102669, "qty": 1, "name": "SEMI 10ML CITY GIRL #74", "spec": "caja 6u"}, {"id": 7101, "qty": 6, "name": "SEMI 10ML CITY GIRL #11", "spec": "simple"}, {"id": 102686, "qty": 1, "name": "SEMI 10ML CITY GIRL #71", "spec": "caja 6u"}, {"id": 7078, "qty": 6, "name": "SEMI 10ML CITY GIRL #59", "spec": "simple"}, {"id": 126237, "qty": 2, "name": "RUBOR EN BARRA RIMERA QUINCE RQ15 A", "spec": "caja 24u"}, {"id": 177004, "qty": 3, "name": "Labial en Barra Matte Miss Betty DD", "spec": "caja-24u"}, {"id": 119021, "qty": 2, "name": "SERIE 12PCS ESMALTE SEMI OJO DE GAT", "spec": "caja 12colores"}, {"id": 199067, "qty": 4, "name": "POLVO TRASLUCIDO MINERAL– CITY GIRL", "spec": "caja-12u"}, {"id": 156152, "qty": 4, "name": "LFME REMOVEDOR PARA ESMALTE UÑA 100", "spec": "3 unidad"}, {"id": 177071, "qty": 1, "name": "Delineador Líquido para Ojos Makeup", "spec": "caja-24u"}, {"id": 189499, "qty": 2, "name": "Depilador De Cristal Removedor De P", "spec": "3-unidad"}, {"id": 130351, "qty": 2, "name": "PACK DE LIMA MINI cml-060c", "spec": "6 unidad"}, {"id": 120343, "qty": 3, "name": "MASCARA DE PESTAÑAS 4ANGELS AR1152", "spec": "caja 24u"}, {"id": 95747, "qty": 2, "name": "CAJA*12 DELINEADOR CON SELLO 89109", "spec": "simple"}, {"id": 199044, "qty": 1, "name": "AGUA MICELAR – CITY GIRL F6658/F665", "spec": "caja-8-unida"}, {"id": 204905, "qty": 2, "name": "Agua Micelar TEI con Aloe Vera54344", "spec": "x3 unidad"}, {"id": 117757, "qty": 4, "name": "DELINEADOR LAPIZ LABIO KARITE 2690-", "spec": "12 unidad"}, {"id": 156212, "qty": 2, "name": "TOALLITA DESMAQUILLANTES CON AGUA M", "spec": "pack 12u"}, {"id": 101517, "qty": 2, "name": "TOALLITA DESMAQUILLANTES CON AGUA M", "spec": "pack 12u"}, {"id": 159775, "qty": 3, "name": "LAS VARANO REMOVEDOR 120ML R120", "spec": "10-unidad"}, {"id": 189724, "qty": 2, "name": "Máscara De Pestañas Volum&#8217; Ex", "spec": "caja-24u"}, {"id": 118524, "qty": 2, "name": "REMOVEDOR DE CUTICULAS CHERIMOYA CH", "spec": "x3 unidad"}, {"id": 169300, "qty": 2, "name": "Paleta De Sombras Angel Stitch Summ", "spec": "3-unidad"}, {"id": 168291, "qty": 1, "name": "MASCARA DE PESTAÑAS TEI TEI8291", "spec": "caja 24u"}, {"id": 169264, "qty": 4, "name": "Paleta De Sombras Angel Stitch Rosa", "spec": "3-unidad"}, {"id": 195038, "qty": 1, "name": "MASCARA DE PESTAÑAS WATERPROOF NOLM", "spec": "caja-24u"}, {"id": 189712, "qty": 1, "name": "Máscara De Pestañas Sky High Volume", "spec": "caja-24u"}, {"id": 192177, "qty": 6, "name": "Pack 12pcs Esponja de Maquillaje Bl", "spec": "simple"}, {"id": 155067, "qty": 1, "name": "PACK*10 ACEITE CUTICULA  CML-598CX", "spec": "simple"}, {"id": 126636, "qty": 2, "name": "PACK*12 DE REPUESTO DE ARQUEADOR CM", "spec": "simple"}, {"id": 7898, "qty": 2, "name": "PACK X25 LIMAS CITY GIRL 150/150 40", "spec": "simple"}, {"id": 199844, "qty": 8, "name": "TOALLITAS HUMEDAS MINI 8 PACK X 8 U", "spec": "simple"}, {"id": 167281, "qty": 1, "name": "Pack Cepillos de Pestañas NAEZ BC28", "spec": "6-unidad"}, {"id": 180169, "qty": 1, "name": "PALETA DE SOMBRAS CITY GIRL RL-1227", "spec": "caja-21unida"}, {"id": 169360, "qty": 6, "name": "Paleta De Sombras Stitch Aloha Con ", "spec": "simple"}, {"id": 169343, "qty": 24, "name": "Paleta De Sombras Nude Eyeshadow Co", "spec": "simple"}, {"id": 169331, "qty": 6, "name": "Paleta De Sombras Hello Kitty Sanri", "spec": "simple"}, {"id": 169259, "qty": 6, "name": "Paleta De Sombras Stitch Con Espejo", "spec": "simple"}, {"id": 170453, "qty": 2, "name": "Uñas Press On Con Diseños Surtidos ", "spec": "pack-12u"}, {"id": 175575, "qty": 3, "name": "Uñas Press On Con Diseños Surtidos ", "spec": "pack-12u"}, {"id": 160025, "qty": 3, "name": "UÑAS PRESS ON COFFIN NAEZ BC1764/17", "spec": "pack-12u"}, {"id": 187552, "qty": 3, "name": "Uñas Press On Con Diseños Surtidos ", "spec": "pack-12u"}, {"id": 188731, "qty": 6, "name": "Pegamento para Uñas con Pincel DD29", "spec": "pack-12u"}, {"id": 203364, "qty": 6, "name": "PEGAMENTO PARA UÑAS RÁPIDO Y FIRME ", "spec": "pack-12u"}, {"id": 100752, "qty": 12, "name": "*3 UNIDAD ESMALTE SEMI MELY COLOR 8", "spec": "unidad"}, {"id": 159062, "qty": 4, "name": "Ultrabond 15 ML CHERIMOYA  CH045", "spec": "caja-6u"}, {"id": 93394, "qty": 1, "name": "#49 ESMALTE SEMI CITY GIRL", "spec": "caja 6u"}, {"id": 93346, "qty": 2, "name": "#33 ESMALTE SEMI CITY GIRL", "spec": "caja 6u"}, {"id": 109687, "qty": 1, "name": "#136 ESMALTE SEMI CITY GIRL", "spec": "caja x6u"}, {"id": 109262, "qty": 1, "name": "SERIE A+B 24UNIDAD ESMALTE SEMI ROJ", "spec": "simple"}, {"id": 109742, "qty": 1, "name": "#156 ESMALTE SEMI CITY GIRL", "spec": "caja x6u"}, {"id": 184416, "qty": 1, "name": "ESMALTE SEMI BLANCO NEGRO VIA LACTE", "spec": "caja-12u"}, {"id": 152092, "qty": 2, "name": "PRESS GEL CAPPING ELOISE 10 ML 1014", "spec": "caja-12u"}, {"id": 84062, "qty": 2, "name": "ULTRABOND PRIMER 10ML CITY GIRL PX2", "spec": "caja 6u"}, {"id": 173217, "qty": 1, "name": "Set De Polvos Aurora Sólido X6 Tono", "spec": "pack-12u"}, {"id": 109642, "qty": 1, "name": "#149 ESMALTE SEMI CITY GIRL", "spec": "caja x6u"}, {"id": 197121, "qty": 3, "name": "Colección de 8 Colores Efecto Auror", "spec": "caja-8u-1-8"}, {"id": 135826, "qty": 1, "name": "BASE DE MAQUILLAJE PINK21 CS3403/56", "spec": "caja 24u"}, {"id": 105345, "qty": 2, "name": "LABIAL EN BARRA EFECTO BRILLOSO 4AN", "spec": "caja x24u"}, {"id": 129679, "qty": 1, "name": "LABIAL EN BARRA MISS BETTY DH-K5927", "spec": "caja 24u"}, {"id": 125522, "qty": 1, "name": "LABIAL EN BARRA MISS BETTY DH-K5930", "spec": "caja 24u"}, {"id": 126787, "qty": 2, "name": "PALETA DE CORRECTOR DH-ME6014E/1911", "spec": "caja 12u"}, {"id": 172860, "qty": 1, "name": "CORRECTOR EN BARRA MINI TANGO DH-L2", "spec": "caja 24u"}, {"id": 126651, "qty": 1, "name": "CHERIMOYA PRIMER CON ACIDO CH046", "spec": "x16 unidad"}, {"id": 107250, "qty": 1, "name": "LAS VARANO PRIMER SIN ACIDO PSA11", "spec": "x10 unidad"}, {"id": 14565, "qty": 24, "name": "LABIAL LIP GLOSS BARBY DH75043/2337", "spec": "unidad"}, {"id": 21234, "qty": 36, "name": "GLOSS DE ALOE VERA QOIDEN ROSE 6010", "spec": "unidad"}, {"id": 48066, "qty": 2, "name": "LIP GLOSS DOULEEC 81035/22513", "spec": "caja 12u"}, {"id": 77924, "qty": 3, "name": "SET PERFILADORES CITY 15048/MD-003", "spec": "caja 20u"}, {"id": 120079, "qty": 2, "name": "VINCHAS PARA MAQUILLAJES NAEZ BC112", "spec": "pack 12u"}, {"id": 140941, "qty": 2, "name": "SET Blister de hebillas y colitas d", "spec": "pack 12u"}, {"id": 120007, "qty": 1, "name": "VINCHAS+MUÑEQUERA NAEZ BC1115", "spec": "pack 12u"}, {"id": 85549, "qty": 1, "name": "CEPILLO PARA DUCHA MELY 63819", "spec": "pack 12u"}, {"id": 120132, "qty": 1, "name": "VINCHAS+MUÑEQUERA NAEZ BC2191", "spec": "pack 12u"}, {"id": 120029, "qty": 2, "name": "VINCHAS PARA MAQUILLAJES NAEZ BC112", "spec": "pack 12u"}, {"id": 174001, "qty": 6, "name": "MASCARILLA FACIAL TEI SURTIDO", "spec": "pack-10u"}, {"id": 158819, "qty": 3, "name": "Mascarilla Facial De Miel De Manuka", "spec": "20 unidad surtidos"}, {"id": 158842, "qty": 1, "name": "Mascarilla Facial Antioxidante De F", "spec": "20 unidad surtidos"}, {"id": 164436, "qty": 36, "name": "MASCARA DE PESTAÑAS 2 EN 1  4ANGEL ", "spec": "unidad"}, {"id": 133759, "qty": 6, "name": "MASCARILLA FACIAL PERSONAJES 36 MOD", "spec": "pack 10u"}, {"id": 133764, "qty": 1, "name": "MASCARA DE PESTAÑAS ARABE DH509-232", "spec": "caja 24u"}, {"id": 165874, "qty": 2, "name": "Rubor liquido PINK TOUCH  PINK 21 C", "spec": "caja-24u"}, {"id": 196876, "qty": 2, "name": "RUBOR  MAGICO DH80102/81290", "spec": "caja-12u"}, {"id": 202261, "qty": 2, "name": "MASCARA DE PESTAÑAS VOLUMINIZADORA ", "spec": "caja-12u"}, {"id": 81822, "qty": 2, "name": "RUBOR LABIAL 2IN1 GEGEBEAR GX1236", "spec": "6 unidad"}, {"id": 202177, "qty": 1, "name": "LABIAL LIQUIDO MATTE LARGA DURACION", "spec": "caja-24u"}, {"id": 144544, "qty": 1, "name": "MASCARA DE PESTAÑAS MINII TANGO DH-", "spec": "caja 36u"}, {"id": 99009, "qty": 1, "name": "ACEITE DE CUTICULAS 15ML NAVI 91518", "spec": "x6 unidad"}, {"id": 55340, "qty": 28, "name": "LABIAL LIP STICK COLOR 2IN1 MISS BE", "spec": "unidad"}, {"id": 176563, "qty": 4, "name": "CUARTETO DE SOMBRAS  TYL1407", "spec": "10-unidad"}, {"id": 189755, "qty": 4, "name": "Paleta De Sombras 9 Tonos Smoked Ey", "spec": "6-unidad"}, {"id": 189750, "qty": 4, "name": "Paleta De Sombras 9 Tonos Chocolate", "spec": "6-unidad"}, {"id": 194276, "qty": 2, "name": "PALETA DE SOMBRAS 48 COLORES TEI TE", "spec": "caja-6-unidad"}, {"id": 204402, "qty": 1, "name": "SOMBRAS LÍQUIDAS PARA OJOS TEI TEI8", "spec": "caja-24u"}, {"id": 192179, "qty": 6, "name": "Pack 12pcs Esponjas de Maquillaje B", "spec": "simple"}, {"id": 133925, "qty": 1, "name": "RUBOR EN POLVO MISS LARA MS-503/318", "spec": "caja 12u"}, {"id": 42110, "qty": 24, "name": "ILUMINADOR EN CREMA 80145/12963", "spec": "unidad"}, {"id": 59884, "qty": 24, "name": "ILUMINADOR LIQUIDO MISS LARA 03510/", "spec": "unidad"}, {"id": 188726, "qty": 1, "name": "Pack 15pcs Aceite Revitalizante par", "spec": "simple"}];

  console.log(`🚀 开始处理 Bella Central 购物车 (目标商品数: ${items.length})...`);

  // 1. 获取 Nonce 并自动清空购物车中的旧商品
  let nonce = '';
  try {
    const cr = await fetch('/wp-json/wc/store/v1/cart', { credentials: 'include' });
    nonce = cr.headers.get('Nonce') || '';
    if (cr.ok) {
      const cData = await cr.json();
      const existing = cData.items || [];
      if (existing.length > 0) {
        console.log(`🧹 检测到网站购物车已有 ${existing.length} 件商品，正在先彻底清空...`);
        for (const ex of existing) {
          const rmRes = await fetch('/wp-json/wc/store/v1/cart/remove-item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Nonce': nonce },
            credentials: 'include',
            body: JSON.stringify({ key: ex.key })
          });
          const n = rmRes.headers.get('Nonce');
          if (n) nonce = n;
        }
        console.log('✨ 旧购物车已彻底清空！准备开始导入新商品...');
      } else {
        console.log('🛒 网站购物车当前为空，直接开始导入...');
      }
    }
  } catch(e) {
    console.warn('清空购物车检查异常，继续执行加购:', e);
  }

  let added = 0;
  let failed = 0;

  // 2. 依次加入新商品
  for (let i = 0; i < items.length; i++) {
    const it = items[i];
    try {
      const res = await fetch('/wp-json/wc/store/v1/cart/add-item', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Nonce': nonce
        },
        credentials: 'include',
        body: JSON.stringify({
          id: it.id,
          quantity: it.qty
        })
      });

      const nextNonce = res.headers.get('Nonce');
      if (nextNonce) nonce = nextNonce;

      if (res.ok) {
        added++;
        console.log(`[${i + 1}/${items.length}] ✅ 加购成功: ${it.name} (${it.spec} x ${it.qty})`);
      } else {
        const errJson = await res.json().catch(() => ({}));
        console.warn(`[${i + 1}/${items.length}] ⚠️ 加购受阻: ${it.name} (ID: ${it.id})`, errJson.message || res.statusText);
        failed++;
      }
    } catch(err) {
      console.error(`[${i + 1}/${items.length}] ❌ 异常: ${it.name}`, err);
      failed++;
    }
    await new Promise(r => setTimeout(r, 60));
  }

  console.log(`🎉 导入执行完毕！成功导入: ${added}, 失败: ${failed}`);
  alert(`🎉 成功将 ${added} / ${items.length} 件商品加入 Bella Central 购物车！点击确定跳转查看。`);
  location.href = '/carro/';
})();