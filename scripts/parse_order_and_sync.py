import re
import pymysql

order_text = """
[DEDO DE PRACTICA CON UÑA CD:DH70539/ZJJSZ - X6 UNIDAD](https://bellacentral.com.ar/producto/dedo-de-practica-con-una-cddh70539-zjjsz/?attribute_cantidad=X6+UNIDAD) × 2
$ 4.800,00
[Strass Gemas Autoadhesivas SURTIDOS COLORES NAEZ BC2051/20517 - PACK 12U](https://bellacentral.com.ar/producto/strass-gemas-autoadhesivas-surtidos-colores-naez-bc2051/?attribute_cantidad=PACK+12U) × 2
$ 9.600,00
[Parches Para LABIOS Mascarilla TEI k3040/k3039/k3038/k3037 - PACK 10U](https://bellacentral.com.ar/producto/parches-para-labios-mascarilla-tei-k3040-k3039-k3038-k3037/?attribute_pa_unidad-12unidad-caja-24u=pack-10u) × 5
$ 15.000,00
[LIMPIADOR FACIAL SILICONA CD:HT-2301 - PACK X12U](https://bellacentral.com.ar/producto/limpiador-facial-silicona-cdht-1119-56181/?attribute_cantidad=PACK+X12U) × 2
$ 45.600,00
[Parches Para Ojos Mascarilla TEI K3031 - PACK 10U](https://bellacentral.com.ar/producto/parches-para-ojos-mascarilla-tei-k3031/?attribute_pa_unidad-12unidad-caja-24u=pack-10u) × 5
$ 15.000,00
[MASCARA KERATINA 270G FIDELITE 61190 ART/403](https://bellacentral.com.ar/producto/mascara-keratina-270g-fidelite-61190-art-403/) × 4
$ 17.600,00
[MASCARA ALMENDRAS 270G FIDELITE 61213 ART/405](https://bellacentral.com.ar/producto/mascara-almendras-270g-fidelite-61213-art-405/) × 4
$ 17.400,00
[Set de Belleza 5 en 1 - Kit Completo de Limpieza Facial y Maquillaje NAEZ BC2306/23065 - 3 UNIDAD](https://bellacentral.com.ar/producto/set-de-belleza-5-en-1-kit-completo-de-limpieza-facial-y-maquillaje-naez-bc2306-23065/?attribute_pa_unidad-12unidad-caja-24u=3-unidad) × 2
$ 31.800,00
[KIT DE PERFUME + CREMA CORPORAL CD:YT2574/10494](https://bellacentral.com.ar/producto/kit-de-perfume-crema-corporal-cdyt2574-10494/) × 2
$ 20.000,00
[CEPILLO LIMPIADOR Y EXFOLIANTE FACIAL DOBLE FAZ DE SILICONA NAEZ BC2587/325878 - 6 UNIDAD](https://bellacentral.com.ar/producto/cepillo-limpiador-y-exfoliante-facial-doble-faz-de-silicona-naez-bc2587-325878/?attribute_pa_unidad-12unidad-caja-24u=6-unidad) × 1
$ 10.800,00
[MASCARA CAPILAR SKALA](https://bellacentral.com.ar/producto/mascara-capilar-skala/) × 8
$ 36.800,00
[SEMI 10ML CITY GIRL #74 - CAJA 6U](https://bellacentral.com.ar/producto/semi-10ml-city-girl-74/?attribute_cantidad=CAJA+6U) × 1
$ 10.800,00
[SEMI 10ML CITY GIRL #11](https://bellacentral.com.ar/producto/semi-10ml-city-girl-11/) × 6
$ 10.800,00
[SEMI 10ML CITY GIRL #71 - CAJA 6U](https://bellacentral.com.ar/producto/semi-10ml-city-girl-71/?attribute_cantidad=CAJA+6U) × 1
$ 10.800,00
[SEMI 10ML CITY GIRL #59](https://bellacentral.com.ar/producto/semi-10ml-city-girl-59/) × 6
$ 10.800,00
[RUBOR EN BARRA RIMERA QUINCE RQ15 APROBADO POR ANMAT - CAJA 24U](https://bellacentral.com.ar/producto/rubor-en-barra-rimera-quince-rq15-aprobado-por-anmat/?attribute_cantidad=CAJA+24U) × 2
$ 105.600,00
[Labial en Barra Matte Miss Betty DD-MIB-K6120/561209 - CAJA 24U](https://bellacentral.com.ar/producto/brillo-labial-humectante-infantil-magic-love-miss-betty-dd-mib-l6297-562978/?attribute_pa_unidad-12unidad-caja-24u=caja-24u) × 3
$ 90.000,00
[SERIE 12PCS ESMALTE SEMI OJO DE GATO CHARM LIMIT 08855 - CAJA 12COLORES](https://bellacentral.com.ar/producto/serie-12pcs-esmalte-semi-ojo-de-gato-charm-limit-08855/?attribute_cantidad=CAJA+12COLORES) × 2
$ 45.600,00
[POLVO TRASLUCIDO MINERAL– CITY GIRL F6608 - CAJA 12U](https://bellacentral.com.ar/producto/polvo-traslucido-mineral-city-girl-f6608/?attribute_pa_unidad-12unidad-caja-24u=caja-12u) × 4
$ 144.000,00
[LFME REMOVEDOR PARA ESMALTE UÑA 100ml RA100 - 3 UNIDAD](https://bellacentral.com.ar/producto/lfme-removedor-para-esmalte-una-100ml-ra100/?attribute_cantidad=3+UNIDAD) × 4
$ 31.200,00
[Delineador Líquido para Ojos Makeup New Eyeliner Miss Betty DD-MIB-E1381/513819 - CAJA 24U](https://bellacentral.com.ar/producto/delineador-liquido-para-ojos-makeup-new-eyeliner-miss-betty-dd-mib-e1381-513819/?attribute_pa_unidad-12unidad-caja-24u=caja-24u) × 1
$ 36.000,00
[Depilador De Cristal Removedor De Pelo Y Exfoliante Corporal NAEZ BC2236/32365 - 3 UNIDAD](https://bellacentral.com.ar/producto/depilador-de-cristal-removedor-de-pelo-y-exfoliante-corporal-naez-bc2236-32365/?attribute_pa_unidad-12unidad-caja-24u=3-unidad) × 2
$ 14.400,00
[PACK DE LIMA MINI cml-060c - 6 UNIDAD](https://bellacentral.com.ar/producto/pack-de-lima-mini-cml-060c/?attribute_cantidad=6+UNIDAD) × 2
$ 9.600,00
[MASCARA DE PESTAÑAS 4ANGELS AR1152 - CAJA 24U](https://bellacentral.com.ar/producto/mascara-de-pestanas-4angels-ar1152/?attribute_cantidad=CAJA+24U) × 3
$ 104.400,00
[CAJA*12 DELINEADOR CON SELLO 89109](https://bellacentral.com.ar/producto/caja12-delineador-con-sello-89109/) × 2
$ 17.000,00
[AGUA MICELAR – CITY GIRL F6658/F6659 - CAJA 8 UNIDA](https://bellacentral.com.ar/producto/agua-micelar-city-girl-f6658-f6659/?attribute_pa_unidad-12unidad-caja-24u=caja-8-unida) × 1
$ 28.000,00
[Agua Micelar TEI con Aloe Vera54344 - X3 UNIDAD](https://bellacentral.com.ar/producto/agua-micelar-tei-con-aloe-vera54344/?attribute_cantidad=X3+UNIDAD) × 2
$ 16.800,00
[DELINEADOR LAPIZ LABIO KARITE 2690-47 54501 - 12 UNIDAD](https://bellacentral.com.ar/producto/lapiz-labio-karite-2690-47/?attribute_cantidad=12+UNIDAD) × 4
$ 28.800,00
[TOALLITA DESMAQUILLANTES CON AGUA MICELAR MY891005/10059 - PACK 12U](https://bellacentral.com.ar/producto/toallita-desmaquillantes-con-agua-micelar-my891005-10059/?attribute_cantidad=PACK+12U) × 2
$ 40.800,00
[TOALLITA DESMAQUILLANTES CON AGUA MICELAR MELY891020/10202 - PACK 12U](https://bellacentral.com.ar/producto/toallita-desmaquillantes-con-agua-micelar-my891020-10202/?attribute_cantidad=PACK+12U) × 2
$ 38.400,00
[LAS VARANO REMOVEDOR 120ML R120 - 10 UNIDAD](https://bellacentral.com.ar/producto/las-varano-removedor-120-ml/?attribute_pa_unidad-12unidad-caja-24u=10-unidad) × 3
$ 103.500,00
[Máscara De Pestañas Volum' Express The Colossal Cat Eyes Negro MISS BETTY DH-M6610/05331 - CAJA 24U](https://bellacentral.com.ar/producto/mascara-de-pestanas-volum-express-the-colossal-cat-eyes-negro-miss-betty-dh-m6610-05331/?attribute_pa_unidad-12unidad-caja-24u=caja-24u) × 2
$ 67.200,00
[REMOVEDOR DE CUTICULAS CHERIMOYA CH014 - X3 UNIDAD](https://bellacentral.com.ar/producto/removedor-de-cuticulas-cherimoya/?attribute_cantidad=X3+UNIDAD) × 2
$ 11.400,00
[Paleta De Sombras Angel Stitch Summer Con Espejo X18 Tonos DH-JZD-EYE-18025/80259 - 3 UNIDAD](https://bellacentral.com.ar/producto/paleta-de-sombras-angel-stitch-summer-con-espejo-x18-tonos-dh-jzd-eye-18025-80259/?attribute_pa_unidad-12unidad-caja-24u=3-unidad) × 2
$ 23.400,00
[MASCARA DE PESTAÑAS TEI TEI8291 - CAJA 24U](https://bellacentral.com.ar/producto/mascara-de-pestanas-tei-tei8291/?attribute_cantidad=CAJA+24U) × 1
$ 37.200,00
[Paleta De Sombras Angel Stitch Rosa Con Espejo X9 Tonos DH-JZD-EYE-0927/09274 - 3 UNIDAD](https://bellacentral.com.ar/producto/paleta-de-sombras-angel-stitch-rosa-con-espejo-x9-tonos-dh-jzd-eye-0927-09274/?attribute_pa_unidad-12unidad-caja-24u=3-unidad) × 4
$ 34.800,00
[MASCARA DE PESTAÑAS WATERPROOF NOLM DD-YDM-953/579530 - CAJA 24U](https://bellacentral.com.ar/producto/mascara-de-pestanas-waterproof-nolm-dd-ydm-953-579530/?attribute_pa_unidad-12unidad-caja-24u=caja-24u) × 1
$ 36.000,00
[Máscara De Pestañas Sky High Volume Up Waterproof Negro MISS BETTY DD-M3840/83840 - CAJA 24U](https://bellacentral.com.ar/producto/mascara-de-pestanas-sky-high-volume-up-waterproof-negro-miss-betty-dd-m3840-83840/?attribute_pa_unidad-12unidad-caja-24u=caja-24u) × 1
$ 33.600,00
[Pack 12pcs Esponja de Maquillaje Blender Difuminadora Gota y Reloj de Arena NAEZ DD3079/30797](https://bellacentral.com.ar/producto/pack-12pcs-esponja-de-maquillaje-blender-difuminadora-gota-y-reloj-de-arena-naez-dd3079-30797/) × 6
$ 39.600,00
[PACK*10 ACEITE CUTICULA CML-598CX](https://bellacentral.com.ar/producto/pack10-aceite-cuticula-naez-ht-826/) × 1
$ 8.500,00
[PACK*12 DE REPUESTO DE ARQUEADOR CML-802D/88025](https://bellacentral.com.ar/producto/pack12-de-repuesto-de-arqueador-cdcml-802d/) × 2
$ 14.400,00
[PACK X25 LIMAS CITY GIRL 150/150 40148](https://bellacentral.com.ar/producto/pack-x25-limas-city-girl-150-150-40148/) × 2
$ 22.500,00
[TOALLITAS HUMEDAS MINI 8 PACK X 8 UNIDADES DD-RH-HSXM001/LZ-1540/LZ-1541/LZ-1834/LZ-896/LZ-9603-1/LZ-9603-2/LZ-9611/QH-0344/QH-0368](https://bellacentral.com.ar/producto/toallitas-humedas-mini-8-pack-x-8-unidades-dd-rh-hsxm001-lz-1540-lz-1541-lz-1834-lz-896-lz-9603-1-lz-9603-2-lz-9611-qh-0344-qh-0368/) × 8
$ 44.000,00
[Pack Cepillos de Pestañas NAEZ BC2822/28220 - 6 UNIDAD](https://bellacentral.com.ar/producto/pack-cepillos-de-pestanas-naez-bc2822-28220/?attribute_pa_unidad-12unidad-caja-24u=6-unidad) × 1
$ 9.000,00
[PALETA DE SOMBRAS CITY GIRL RL-12270 - CAJA 21UNIDA](https://bellacentral.com.ar/producto/paleta-de-sombras-city-girl-rl-12270/?attribute_pa_unidad-12unidad-caja-24u=caja-21unida) × 1
$ 94.500,00
[Paleta De Sombras Stitch Aloha Con Espejo X42 Tonos DH-JZD-EYE-4218/42186](https://bellacentral.com.ar/producto/paleta-de-sombras-stitch-aloha-con-espejo-x42-tonos-dh-jzd-eye-4218-42186/) × 6
$ 51.000,00
[Paleta De Sombras Nude Eyeshadow Con Espejo X40 Tonos DH-JZD-IG3275/02754](https://bellacentral.com.ar/producto/paleta-de-sombras-nude-eyeshadow-con-espejo-x40-tonos-dh-jzd-ig3275-02754/) × 24
$ 216.000,00
[Paleta De Sombras Hello Kitty Sanrio Libro Gigante DH-JZD-EYE-5438/54387](https://bellacentral.com.ar/producto/paleta-de-sombras-hello-kitty-sanrio-libro-gigante-dh-jzd-eye-5438-54387/) × 6
$ 54.000,00
[Paleta De Sombras Stitch Con Espejo DH-JZD-EYE-4220/42209](https://bellacentral.com.ar/producto/paleta-de-sombras-stitch-con-espejo-dh-jzd-eye-4220-42209/) × 6
$ 51.000,00
[Uñas Press On Con Diseños Surtidos Naez BC1795/17958 - PACK 12U](https://bellacentral.com.ar/producto/unas-press-on-con-disenos-surtidos-naez-bc1795-17958/?attribute_pa_unidad-12unidad-caja-24u=pack-12u) × 2
$ 45.600,00
[Uñas Press On Con Diseños Surtidos Naez 1820/18207 - PACK 12U](https://bellacentral.com.ar/producto/unas-press-on-con-disenos-surtidos-naez-1820-18207/?attribute_pa_unidad-12unidad-caja-24u=pack-12u) × 3
$ 72.000,00
[UÑAS PRESS ON COFFIN NAEZ BC1764/17606 - PACK 12U](https://bellacentral.com.ar/producto/unas-press-on-coffin-naez-bc1764-17606/?attribute_pa_unidad-12unidad-caja-24u=pack-12u) × 3
$ 64.800,00
[Uñas Press On Con Diseños Surtidos Naez BC1824/18245 - PACK 12U](https://bellacentral.com.ar/producto/unas-press-on-con-disenos-surtidos-naez-bc1824-18245/?attribute_pa_unidad-12unidad-caja-24u=pack-12u) × 3
$ 68.400,00
[Pegamento para Uñas con Pincel DD2913/29135 Naez - PACK 12U](https://bellacentral.com.ar/producto/pegamento-para-unas-con-pincel-dd2913-29135-naez/?attribute_pa_unidad-12unidad-caja-24u=pack-12u) × 6
$ 75.600,00
[PEGAMENTO PARA UÑAS RÁPIDO Y FIRME X 5 UNIDADES NAEZ DD2977/329777 - PACK 12U](https://bellacentral.com.ar/producto/pegamento-para-unas-rapido-y-firme-x-5-unidades-naez-dd2977-329777/?attribute_pa_unidad-12unidad-caja-24u=pack-12u) × 6
$ 115.200,00
[*3 UNIDAD ESMALTE SEMI MELY COLOR 860000 - UNIDAD](https://bellacentral.com.ar/producto/esmalte-semi-mely-color/?attribute_pa_esmalte-mely=unidad) × 12
$ 30.000,00
[Ultrabond 15 ML CHERIMOYA CH045 - CAJA 6U](https://bellacentral.com.ar/producto/ultrabond-15-ml-cherimoya-ch045/?attribute_pa_unidad-12unidad-caja-24u=caja-6u) × 4
$ 144.000,00
[#49 ESMALTE SEMI CITY GIRL - CAJA 6U](https://bellacentral.com.ar/producto/49-esmalte-semi-city-girl/?attribute_cantidad=CAJA+6U) × 1
$ 10.800,00
[#33 ESMALTE SEMI CITY GIRL - CAJA 6U](https://bellacentral.com.ar/producto/33-esmalte-semi-city-girl/?attribute_cantidad=CAJA+6U) × 2
$ 21.600,00
[#136 ESMALTE SEMI CITY GIRL - CAJA X6U](https://bellacentral.com.ar/producto/136-esmalte-semi-city-girl/?attribute_cantidad=CAJA+X6U) × 1
$ 10.800,00
[SERIE A+B 24UNIDAD ESMALTE SEMI ROJO CHARM LIMIT DH89013](https://bellacentral.com.ar/producto/serie-ab-24unidad-esmalte-semi-rojo-charm-limit-dh89013/) × 1
$ 40.800,00
[#156 ESMALTE SEMI CITY GIRL - CAJA X6U](https://bellacentral.com.ar/producto/156-esmalte-semi-city-girl/?attribute_cantidad=CAJA+X6U) × 1
$ 10.800,00
[ESMALTE SEMI BLANCO NEGRO VIA LACTEA SAR-103 00781 - CAJA 12U](https://bellacentral.com.ar/producto/esmalte-semi-blanco-charm-limit-dh86042-03034/?attribute_pa_unidad-12unidad-caja-24u=caja-12u) × 1
$ 18.000,00
[PRESS GEL CAPPING ELOISE 10 ML 10144 - CAJA 12U](https://bellacentral.com.ar/producto/press-gel-capping-eloise-10-ml-10144/?attribute_pa_unidad-12unidad-caja-24u=caja-12u) × 2
$ 60.000,00
[ULTRABOND PRIMER 10ML CITY GIRL PX2438/13092 - CAJA 6U](https://bellacentral.com.ar/producto/ultrabond-primer-10ml-city-girl-px2438-13092/?attribute_cantidad=CAJA+6U) × 2
$ 33.600,00
[Set De Polvos Aurora Sólido X6 Tonos Cromo Nail SP6245/016245 - PACK 12U](https://bellacentral.com.ar/producto/set-de-polvos-aurora-solido-x6-tonos-cromo-nail-sp6245-016245/?attribute_pa_unidad-12unidad-caja-24u=pack-12u) × 1
$ 26.400,00
[#149 ESMALTE SEMI CITY GIRL - CAJA X6U](https://bellacentral.com.ar/producto/149-esmalte-semi-city-girl/?attribute_cantidad=CAJA+X6U) × 1
$ 10.800,00
[Colección de 8 Colores Efecto Aurora / Unicornio RIMERA 15 ES01-08-09 - CAJA 8U 1-8](https://bellacentral.com.ar/producto/coleccion-de-8-colores-efecto-aurora-unicornio-rimera-15-es01-08-09/?attribute_pa_unidad-12unidad-caja-24u=caja-8u-1-8) × 3
$ 67.200,00
[BASE DE MAQUILLAJE PINK21 CS3403/56029 - CAJA 24U](https://bellacentral.com.ar/producto/base-de-maquillaje-pink21-cs3403-56029/?attribute_cantidad=CAJA+24U) × 1
$ 55.200,00
[LABIAL EN BARRA EFECTO BRILLOSO 4ANGELS CD:AR1085/85197 - CAJA X24U](https://bellacentral.com.ar/producto/labial-en-barra-efecto-brilloso-4angels-cdar1085-85197/?attribute_cantidad=CAJA+X24U) × 2
$ 57.600,00
[LABIAL EN BARRA MISS BETTY DH-K5927/59275 - CAJA 24U](https://bellacentral.com.ar/producto/labial-en-barra-miss-betty-dh-k5927-59275/?attribute_cantidad=CAJA+24U) × 1
$ 26.400,00
[LABIAL EN BARRA MISS BETTY DH-K5930/59305 - CAJA 24U](https://bellacentral.com.ar/producto/labial-en-barra-miss-betty-dh-k5930-59305/?attribute_cantidad=CAJA+24U) × 1
$ 26.400,00
[PALETA DE CORRECTOR DH-ME6014E/19115 - CAJA 12U](https://bellacentral.com.ar/producto/paleta-de-corrector-dh-me6014e-19115/?attribute_cantidad=CAJA+12U) × 2
$ 74.400,00
[CORRECTOR EN BARRA MINI TANGO DH-L272/20724 - CAJA 24U](https://bellacentral.com.ar/producto/corrector-en-barra-mini-tango-dh-l272-20724-2/?attribute_cantidad=CAJA+24U) × 1
$ 33.600,00
[CHERIMOYA PRIMER CON ACIDO CH046 - X16 UNIDAD](https://bellacentral.com.ar/producto/cherimoya-primer-con-acido/?attribute_cantidad=X16+UNIDAD) × 1
$ 52.800,00
[LAS VARANO PRIMER SIN ACIDO PSA11 - X10 UNIDAD](https://bellacentral.com.ar/producto/las-varano-primer-sin-acido/?attribute_cantidad=X10+UNIDAD) × 1
$ 24.000,00
[LIP GLOSS DOULEEC 81035/22513 - CAJA 12U](https://bellacentral.com.ar/producto/lip-gloss-douleec-81035/?attribute_cantidad=CAJA+12U) × 2
$ 12.000,00
[SET PERFILADORES CITY 15048/MD-003 - CAJA 20U](https://bellacentral.com.ar/producto/set-x3-perfiladores-city-15048-md-003/?attribute_cantidad=CAJA+20U) × 3
$ 48.000,00
[VINCHAS PARA MAQUILLAJES NAEZ BC1121 - PACK 12U](https://bellacentral.com.ar/producto/vinchas-para-maquillajes-naez-bc1121/?attribute_cantidad=PACK+12U) × 2
$ 40.800,00
[SET Blister de hebillas y colitas de pelo NAEZ BC2263/22631 - PACK 12U](https://bellacentral.com.ar/producto/set-blister-de-hebillas-y-colitas-de-pelo-naez-bc2263-22631/?attribute_cantidad=PACK+12U) × 2
$ 33.600,00
[VINCHAS+MUÑEQUERA NAEZ BC1115 - PACK 12U](https://bellacentral.com.ar/producto/vinchasmunequera-naez-bc1115/?attribute_cantidad=PACK+12U) × 1
$ 38.400,00
[CEPILLO PARA DUCHA MELY 63819 - PACK 12U](https://bellacentral.com.ar/producto/cepillo-para-ducha-mely-63819/?attribute_cantidad=PACK+12U) × 1
$ 36.000,00
[VINCHAS+MUÑEQUERA NAEZ BC2191 - PACK 12U](https://bellacentral.com.ar/producto/vinchasmunequera-naez-bc2191/?attribute_cantidad=PACK+12U) × 1
$ 32.400,00
[VINCHAS PARA MAQUILLAJES NAEZ BC1122 - PACK 12U](https://bellacentral.com.ar/producto/vinchas-para-maquillajes-naez-bc1122/?attribute_cantidad=PACK+12U) × 2
$ 40.800,00
[MASCARILLA FACIAL TEI SURTIDO - PACK 10U](https://bellacentral.com.ar/producto/mascarilla-facial-tei-surtido/?attribute_pa_unidad-12unidad-caja-24u=pack-10u) × 6
$ 33.000,00
[Mascarilla Facial De Miel De Manuka Y Vitamina E BQY15921/715921 BIOAQUA - 20 UNIDAD SURTIDOS](https://bellacentral.com.ar/producto/kit-limpieza-de-nariz-3-pasos-bioaqua-bqy00911-800911-bioaqua-2/?attribute_cantidad=20+UNIDAD+SURTIDOS) × 3
$ 36.000,00
[Mascarilla Facial Antioxidante De Flor De Loto De Nieve DH-BQY48035/748035 BIOAQUA - 20 UNIDAD SURTIDOS](https://bellacentral.com.ar/producto/mascarilla-facial-antioxidante-de-flor-de-loto-de-nieve-dh-bqy48035-748035-bioaqua/?attribute_cantidad=20+UNIDAD+SURTIDOS) × 1
$ 12.000,00
[MASCARILLA FACIAL PERSONAJES 36 MODELO DH509-222/223/224/KTMM - PACK 10U](https://bellacentral.com.ar/producto/mascarilla-facial-personajes-36-modelo-dh509-222-223-224-ktmm/?attribute_cantidad=PACK+10U) × 6
$ 30.000,00
[MASCARA DE PESTAÑAS ARABE DH509-232/22053 - CAJA 24U](https://bellacentral.com.ar/producto/mascara-de-pestanas-arabe-dh509-232-22053/?attribute_cantidad=CAJA+24U) × 1
$ 31.200,00
[Rubor liquido PINK TOUCH PINK 21 CS5580/484626 - CAJA 24U](https://bellacentral.com.ar/producto/rubor-liquido-pink-touch-pink-21-cs5580-484626/?attribute_pa_unidad-12unidad-caja-24u=caja-24u) × 2
$ 57.600,00
[RUBOR MAGICO DH80102/81290 - CAJA 12U](https://bellacentral.com.ar/producto/rubor-magico-dh80102-81290/?attribute_pa_unidad-12unidad-caja-24u=caja-12u) × 2
$ 16.800,00
[MASCARA DE PESTAÑAS VOLUMINIZADORA PINK SHOCK PINK 21 CS6754/01613 - CAJA 12U](https://bellacentral.com.ar/producto/mascara-de-pestanas-voluminizadora-pink-shock-pink-21-cs6754-01613/?attribute_pa_unidad-12unidad-caja-24u=caja-12u) × 2
$ 45.600,00
[RUBOR LABIAL 2IN1 GEGEBEAR GX1236 - 6 UNIDAD](https://bellacentral.com.ar/producto/rubor-labial-2in1-gegebear-gx1236/?attribute_cantidad=6+UNIDAD) × 2
$ 19.200,00
[LABIAL LIQUIDO MATTE LARGA DURACION BEAUTY PINK 21 CS6696/01767 - CAJA 24U](https://bellacentral.com.ar/producto/labial-liquido-matte-larga-duracion-beauty-pink-21-cs6696-01767/?attribute_pa_unidad-12unidad-caja-24u=caja-24u) × 1
$ 45.600,00
[MASCARA DE PESTAÑAS MINII TANGO DH-MT-M342/13429 - CAJA 36U](https://bellacentral.com.ar/producto/mascara-de-pestanas-minii-tango-dh-mt-m342-13429/?attribute_cantidad=CAJA+36U) × 1
$ 68.400,00
[ACEITE DE CUTICULAS 15ML NAVI 91518 - X6 UNIDAD](https://bellacentral.com.ar/producto/aceite-de-cuticula-navi-91518/?attribute_cantidad=X6+UNIDAD) × 1
$ 12.300,00
[CUARTETO DE SOMBRAS TYL1407 - 10 UNIDAD](https://bellacentral.com.ar/producto/cuarteto-de-sombras-tyl1407/?attribute_pa_unidad-12unidad-caja-24u=10-unidad) × 4
$ 48.000,00
[Paleta De Sombras 9 Tonos Smoked Eyeshadow Palette Tonos Oscuros K'APEINE DD-KPE-YY009028/740367 - 6 UNIDAD](https://bellacentral.com.ar/producto/paleta-de-sombras-9-tonos-smoked-eyeshadow-palette-tonos-oscuros-kapeine-dd-kpe-yy009028-74036/?attribute_pa_unidad-12unidad-caja-24u=6-unidad) × 4
$ 67.200,00
[Paleta De Sombras 9 Tonos Chocolate Eyeshadow Palette K'APEINE DD-KPE-YY009030/74051 - 6 UNIDAD](https://bellacentral.com.ar/producto/paleta-de-sombras-9-tonos-chocolate-eyeshadow-palette-kapeine-dd-kpe-yy009030-74051/?attribute_pa_unidad-12unidad-caja-24u=6-unidad) × 4
$ 67.200,00
[PALETA DE SOMBRAS 48 COLORES TEI TEI8383/16978 - CAJA 6 UNIDAD](https://bellacentral.com.ar/producto/paleta-de-sombras-48-colores-tei-tei8383-16978/?attribute_pa_unidad-12unidad-caja-24u=caja-6-unidad) × 2
$ 99.600,00
[SOMBRAS LÍQUIDAS PARA OJOS TEI TEI8555 - CAJA 24U](https://bellacentral.com.ar/producto/sombras-liquidas-para-ojos-tei-tei8555/?attribute_pa_unidad-12unidad-caja-24u=caja-24u) × 1
$ 44.400,00
[Pack 12pcs Esponjas de Maquillaje Blender Difuminadoras en Tonos Rosa y Beige NAEZ DD3080/23038](https://bellacentral.com.ar/producto/pack-12pcs-esponjas-de-maquillaje-blender-difuminadoras-en-tonos-rosa-y-beige-naez-dd3080-23038/) × 6
$ 39.600,00
[RUBOR EN POLVO MISS LARA MS-503/31825 - CAJA 12U](https://bellacentral.com.ar/producto/rubor-en-polvo-miss-lara-ms-503-31825/?attribute_cantidad=CAJA+12U) × 1
$ 30.000,00
[Pack 15pcs Aceite Revitalizante para Cutículas en Lápiz BC1322/13226 Naez](https://bellacentral.com.ar/producto/pack-12pcs-aceite-revitalizante-para-cuticulas-en-lapiz-bc1322-13226-naez/) × 1
$ 12.750,00
[LABIAL LIP GLOSS BARBY DH75043/23370 - CAJA DE 24](https://bellacentral.com.ar/producto/labial-lip-gloss-barby-dh75043-23370/?attribute_labial=CAJA+DE+24) × 1
$ 30.000,00
[GLOSS DE ALOE VERA QOIDEN ROSE 60105 - X 6 UNIDADES](https://bellacentral.com.ar/producto/gloss-de-aloe-vera-qoiden-rose/?attribute_labial-aloe-vera=X+6+UNIDADES) × 6
$ 43.200,00
[MASCARA DE PESTAÑAS 2 EN 1 4ANGEL AR1174 - X6U](https://bellacentral.com.ar/producto/mascara-de-pestanas-2-en-1-4angel-ar1174/?attribute_cantidad=X6U) × 1
$ 9.900,00
[LABIAL LIP STICK COLOR 2IN1 MISS BETTY 33386/83002 - CAJA DE 24](https://bellacentral.com.ar/producto/labial-lip-stick-color-2in1-miss-betty-6923958583002/?attribute_cantidad=CAJA+DE+24) × 1
$ 19.200,00
[ILUMINADOR EN CREMA 80145/12963 - CAJA DE 24](https://bellacentral.com.ar/producto/iluminador-en-crema-80145/?attribute_cantidad=CAJA+DE+24) × 1
$ 31.200,00
[ILUMINADOR LIQUIDO MISS LARA 03510/DH83524 - X CAJA DE 24](https://bellacentral.com.ar/producto/iluminador-liquido-miss-lara-03510-dh83524/?attribute_cantidad=X+CAJA+DE+24) × 1
$ 40.800,00
"""

# Let's parse each item: url, quantity multiplier, and total price
pattern = re.compile(r'\[(.*?)\]\((https://bellacentral\.com\.ar/producto/[^\)\?]+)[^\)]*\)\s*×\s*(\d+)\s*\n\s*\$\s*([\d\.\,]+)', re.MULTILINE)
matches = pattern.findall(order_text)

print(f"Total parsed order items: {len(matches)}")

conn = pymysql.connect(host='localhost', user='root', password='admin123', database='supplier_crawler', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

order_sync_data = []
total_calc = 0.0

for name, url, qty_str, price_str in matches:
    clean_url = url.rstrip('/') + '/'
    qty_num = int(qty_str)
    price_val = float(price_str.replace('.', '').replace(',', '.'))
    total_calc += price_val
    order_sync_data.append({
        'name': name,
        'url': clean_url,
        'order_qty': qty_num,
        'line_total': price_val
    })

print(f"Parsed total amount: ${total_calc:,.2f}")

# Match with database products
matched_count = 0
unmatched = []

with conn.cursor() as cur:
    for item in order_sync_data:
        # Match by product_url prefix
        cur.execute("SELECT id, name, sku, price, package_qty, sub_pack_qty FROM products WHERE supplier_id = 18 AND product_url LIKE %s", (item['url'] + '%',))
        p = cur.fetchone()
        if not p:
            # Try matching by title start
            cur.execute("SELECT id, name, sku, price, package_qty, sub_pack_qty FROM products WHERE supplier_id = 18 AND name LIKE %s", (item['name'][:25] + '%',))
            p = cur.fetchone()
        if p:
            item['product_id'] = p['id']
            item['sku'] = p['sku']
            item['db_price'] = float(p['price'] or 0)
            item['package_qty'] = p['package_qty'] or 1
            item['sub_pack_qty'] = p['sub_pack_qty'] or 1
            matched_count += 1
        else:
            unmatched.append(item)

print(f"Matched with DB: {matched_count}/{len(order_sync_data)}, Unmatched: {len(unmatched)}")
if unmatched:
    for u in unmatched:
        print("Unmatched:", u['name'][:40], u['url'])
