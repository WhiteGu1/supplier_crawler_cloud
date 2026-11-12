"""
Trapoman 第二轮：对剩余82条中名称可判断的直接分类，
仅 BICHO RED REJILLA 系列(7条) 用图片审查
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# 手动审查后的分类
CLASSIFICATIONS = {
    # 厨房储物（密封罐套装/储物容器）
    17538: '厨房储物',  # SET SAN REMO X4 RECTANGULAR
    17539: '厨房储物',  # SET SAN REMO X5 RECTANGULAR
    17540: '厨房储物',  # SET SAN REMO X6 RECTANGULAR
    17541: '厨房储物',  # SET SAN REMO X8 RECTANGULAR
    17636: '厨房储物',  # SET SAN REMO FACIL X3
    17637: '厨房储物',  # SET SAN REMO FACIL X3
    17638: '厨房储物',  # SET SAN REMO FACIL X3
    18192: '厨房储物',  # SET X2 MARMITA RECTANGULAR
    18194: '厨房储物',  # SET SAN REMO FACIL X3
    18195: '厨房储物',  # SET SAN REMO FLOR X3
    18196: '厨房储物',  # SET SAN REMO FLOR X3
    18197: '厨房储物',  # SET SAN REMO FLOR X3
    18198: '厨房储物',  # SET SAN REMO FLOR X3
    18267: '厨房储物',  # POTE CHICO OPENING
    18268: '厨房储物',  # POTE MEDIANO OPENING
    18269: '厨房储物',  # POTE GRANDE OPENING
    18129: '厨房储物',  # QUESERA VIDRIO

    # 厨房餐具（炊具配件/餐具）
    17509: '清洁用品',   # ESPONJA GO! POWER
    17651: '厨房餐具',   # PIEDRA AFILADORA 磨刀石
    17652: '厨房餐具',   # TAMIZADOR 筛子
    17754: '厨房餐具',   # SALERO/PIMENTERO
    18017: '厨房餐具',   # AZUCARERA TAPA BAMBU
    18028: '厨房餐具',   # COLADOR ACERO PLUS
    18053: '厨房餐具',   # PRENSA AJO
    18054: '厨房餐具',   # CORTA HUEVO
    18064: '厨房餐具',   # ACEITERO SPRAY
    18098: '餐饮用品',   # PACK SORBETES PAPEL 吸管
    18105: '厨房餐具',   # SET 5 TABLAS DE PICAR
    18120: '厨房餐具',   # TABLA PREMIUM BAMBU 20X30
    18121: '厨房餐具',   # TABLA PREMIUM BAMBU 22X32
    18122: '厨房餐具',   # TABLA PREMIUM BAMBU 24X34
    18123: '厨房餐具',   # TABLA PREMIUM BAMBU 26X36
    18125: '厨房餐具',   # MOLINILLO MADERA 21CM
    18126: '厨房餐具',   # MOLINILLO MADERA 25CM
    18128: '厨房餐具',   # PIMENTERO ELECTRICO
    18130: '厨房餐具',   # TAPON DE VINO
    18154: '清洁用品',   # REPASADOR 抹布
    18170: '清洁用品',   # CEPILLITO X3
    18208: '厨房餐具',   # BOLS 14CM 碗
    18209: '厨房餐具',   # BOLS 20CM 碗
    18213: '厨房餐具',   # CUBETERA SILICONA
    18214: '厨房餐具',   # CUBETERA SILICONA
    18215: '厨房餐具',   # CUBETERA SILICONA
    18216: '厨房餐具',   # CUBETERA PLASTICA
    18217: '厨房餐具',   # CUBETERA PLASTICA
    18278: '厨房餐具',   # COLADOR CON ASA PLEGABLE
    18279: '厨房餐具',   # COLADOR CON MANGO PLEGABLE
    18321: '厨房餐具',   # MOLINILLO MADERA BAMBU BLANCO
    18322: '厨房餐具',   # MOLINILLO MADERA BAMBU NEGRO
    17662: '餐饮用品',   # HIELERA ACERO 冰桶
    20193: '餐饮用品',   # PACK X3 COPA DE HELADO

    # 卫浴用品
    17612: '卫浴用品',   # ORGANIZADOR DE DUCHA DOBLE ESTANTE
    18323: '卫浴用品',   # TAPA P PILETA
    18324: '卫浴用品',   # REJILLA P PILETA
    18325: '卫浴用品',   # TAPA Y REJILLA P PILETA
    18347: '卫浴用品',   # FILTRO PILETA

    # 清洁用品
    18067: '清洁用品',   # SACAPELUSA 粘毛器

    # 宠物用品
    17677: '宠物用品',   # BOLSITA PARA MASCOTA
    18165: '宠物用品',   # CAMA PARA PERROS S
    18166: '宠物用品',   # CAMA PARA PERROS M

    # 厨房炊具
    18069: '厨房炊具',   # BANQUET CHAROLADA 烤盘

    # 玩具游戏
    18378: '玩具游戏',   # MINI PINGUINO AL AGUA
    18384: '玩具游戏',   # TINY PONY Y SU CARRUAJE
    18385: '玩具游戏',   # TINY HORSE
    18446: '玩具游戏',   # BEBE RAFA/AGUS
    18447: '玩具游戏',   # BEBE ELU
    18482: '玩具游戏',   # BLISTER 5 AUTITOS
    18483: '玩具游戏',   # BLISTER 10 AUTITOS
    18587: '玩具游戏',   # SUPER MOTO A CONTROL REMOTO
    18589: '玩具游戏',   # GAME POP STITCH
    18599: '玩具游戏',   # TINY BIJOU
    24486: '玩具游戏',   # ANDARIN DAKOTA NENE
    24487: '玩具游戏',   # ANDARIN DAKOTA NENA

    # 运动户外
    20460: '运动户外',   # PELOTITA SOFT AFA

    # 装饰品
    24423: '装饰品',     # RELOJ
}

# 需要图片审查的：BICHO RED REJILLA 系列 (7条)
NEEDS_IMAGE_IDS = [18327, 18328, 18329, 18330, 18331, 18332, 18333]

conn = pymysql.connect(
    host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler',
    charset='utf8mb4'
)
cur = conn.cursor()

# 写入名称可判断的分类
updated = 0
for pid, cat in CLASSIFICATIONS.items():
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
    updated += cur.rowcount
conn.commit()
print(f"第二轮名称分类: 写入 {updated}/{len(CLASSIFICATIONS)} 条")

# 查看剩余
cur.execute("""
    SELECT id, name, image_local FROM products
    WHERE supplier_id=3 AND (category IS NULL OR category='')
      AND is_available=1
    ORDER BY id
""")
remaining = cur.fetchall()
print(f"\n剩余未分类: {len(remaining)} 条")
for pid, name, img in remaining:
    full_path = f"D:/projects/supplier_crawler/{img}" if img else "N/A"
    print(f"  ID:{pid}  {name}  img={full_path}")

conn.close()
