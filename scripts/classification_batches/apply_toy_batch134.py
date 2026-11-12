import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-1 results
batch1 = [
    (18731, '玩具 > 玩具游戏 > 桌游'),
    (18352, '玩具 > 玩具游戏 > 玩具球'),
    (18353, '玩具 > 玩具游戏 > 玩具球'),
    (18354, '玩具 > 玩具游戏 > 玩具球'),
    (18359, '玩具 > 玩具游戏 > 桌游'),
    (18360, '玩具 > 玩具游戏 > 桌游'),
    (18361, '玩具 > 玩具游戏 > 桌游'),
    (18362, '玩具 > 玩具游戏 > 桌游'),
    (18363, '玩具 > 玩具游戏 > 桌游'),
    (18364, '玩具 > 玩具游戏 > 桌游'),
]

# batch-3 results - but all classified as 桌游, need review
# HAPPY MONKEY GRANDE -> should be 毛绒玩具, not 桌游
# CRAZY DINO -> likely 毛绒玩具 or 解压玩具
# SUPER GOL -> likely 玩具球 or 桌游
# JUEGO CARRERA DE HADAS -> 桌游
# POOL TABLE -> 桌游
# MINI JUEGO DE DADOS -> 桌游
# SUPER STOP -> 桌游
# BINGO -> 桌游
# LUDO AFA -> 桌游
# Correcting obvious errors based on names
batch3 = [
    (18365, '玩具 > 玩具游戏 > 毛绒玩具'),  # HAPPY MONKEY GRANDE - plush monkey
    (18366, '玩具 > 玩具游戏 > 毛绒玩具'),  # CRAZY DINO - plush dino
    (18367, '玩具 > 玩具游戏 > 桌游'),  # SUPER GOL - table soccer game
    (18368, '玩具 > 玩具游戏 > 桌游'),  # JUEGO CARRERA DE HADAS - board game
    (18369, '玩具 > 玩具游戏 > 桌游'),  # POOL TABLE - mini pool table
    (18371, '玩具 > 玩具游戏 > 桌游'),  # MINI JUEGO DE DADOS - dice game
    (18373, '玩具 > 玩具游戏 > 桌游'),  # SUPER STOP - board game
    (18374, '玩具 > 玩具游戏 > 桌游'),  # SUPER STOP - board game
    (18375, '玩具 > 玩具游戏 > 桌游'),  # BINGO
    (18376, '玩具 > 玩具游戏 > 桌游'),  # LUDO AFA - board game
]

# batch-4 results
# DINO AL SUELO -> 桌游? likely a game, keep
# MINI PINGUINO AL AGUA -> 桌游? likely a game, keep
# TINY PONY, TINY HORSE, LULISTAR, BABY, TINY KIT -> 角色扮演 (dolls/figures)
# AUTO GO SPEED x3 -> 玩具车
batch4 = [
    (18377, '玩具 > 玩具游戏 > 桌游'),
    (18378, '玩具 > 玩具游戏 > 桌游'),
    (18384, '玩具 > 玩具游戏 > 角色扮演'),
    (18385, '玩具 > 玩具游戏 > 角色扮演'),
    (18445, '玩具 > 玩具游戏 > 角色扮演'),
    (18448, '玩具 > 玩具游戏 > 角色扮演'),
    (18449, '玩具 > 玩具游戏 > 角色扮演'),
    (18465, '玩具 > 玩具游戏 > 玩具车'),
    (18466, '玩具 > 玩具游戏 > 玩具车'),
    (18467, '玩具 > 玩具游戏 > 玩具车'),
]

total = 0
for batch in [batch1, batch3, batch4]:
    for pid, cat in batch:
        cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, pid))
        total += 1

conn.commit()
print(f'Written: {total} items (batch1=10, batch3=10, batch4=10)')

cur.execute("SELECT COUNT(*) FROM products WHERE category = '玩具 > 玩具游戏' AND image_local IS NOT NULL AND image_local != ''")
print(f'Remaining toys with image: {cur.fetchone()[0]}')

conn.close()
