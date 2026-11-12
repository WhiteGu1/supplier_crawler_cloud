import pymysql, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# Get no-image toys items
cur.execute("SELECT id, name FROM products WHERE category = '玩具 > 玩具游戏' AND (image_local IS NULL OR image_local = '') ORDER BY id")
items = cur.fetchall()
print(f'No-image toys items: {len(items)}')

# Name-based classification rules for toys (Spanish names)
# Categories: 毛绒玩具, 益智玩具, 玩具车, 积木/拼装, 角色扮演, 音乐玩具, 手工DIY, 拼图, 桌游, 玩具球, 解压玩具, 贴纸书, 其他玩具
rules = [
    ('pistola|arma|dardos|lanza', '玩具 > 玩具游戏 > 角色扮演'),
    ('bloques|bloque', '玩具 > 玩具游戏 > 积木/拼装'),
    ('mesa|bingo|tateti|juego mesa', '玩具 > 玩具游戏 > 桌游'),
    ('destreza|desafio|descubri', '玩具 > 玩具游戏 > 益智玩具'),
    ('pelotita|pelota|futbol|rugby', '玩具 > 玩具游戏 > 玩具球'),
    ('slime|antiestres', '玩具 > 玩具游戏 > 解压玩具'),
    ('sticker|pegatina', '玩具 > 玩具游戏 > 贴纸书'),
    ('musical|musica|instrumento', '玩具 > 玩具游戏 > 音乐玩具'),
    ('rompecabezas|puzzle', '玩具 > 玩具游戏 > 拼图'),
    ('auto|camion|tractor|excavadora|lancha|arrastre|avion', '玩具 > 玩具游戏 > 玩具车'),
    ('peluche|monkey|happy', '玩具 > 玩具游戏 > 毛绒玩具'),
    ('joyas|arma joyas|collar|pulsera', '玩具 > 玩具游戏 > 手工DIY'),
    ('arte|set arte|manualidad', '玩具 > 玩具游戏 > 手工DIY'),
    ('doctor|juego doctor', '玩具 > 玩具游戏 > 角色扮演'),
    ('pizarra|magnetica', '玩具 > 玩具游戏 > 益智玩具'),
    ('bebe|avion para bebe', '玩具 > 玩具游戏 > 其他玩具'),
]

classified = 0
unmatched = []
for item_id, name in items:
    name_lower = name.lower()
    matched = False
    for pattern, cat in rules:
        if any(p in name_lower for p in pattern.split('|')):
            cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, item_id))
            classified += 1
            matched = True
            break
    if not matched:
        unmatched.append((item_id, name))
        # Default to 其他玩具
        cur.execute("UPDATE products SET category=%s WHERE id=%s", ('玩具 > 玩具游戏 > 其他玩具', item_id))

conn.commit()
print(f'Classified by rules: {classified}')
print(f'Defaulted to 其他玩具: {len(unmatched)}')
for uid, name in unmatched:
    print(f'  DEFAULTED: id={uid} name={name}')

conn.close()
