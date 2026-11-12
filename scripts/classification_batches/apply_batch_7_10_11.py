import sys, io, pymysql, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-7-retry results
cats7r = ['解压玩具','玩具车','其他玩具','其他玩具','手工DIY','手工DIY','玩具车','其他玩具','拼图','解压玩具']
with open(r'D:\projects\supplier_crawler\panda_batch_7.json', 'r', encoding='utf-8') as f:
    items = json.load(f)
updated = 0
for idx, item in enumerate(items):
    db_id = item['id']
    cat = f'玩具 > 玩具游戏 > {cats7r[idx]}'
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, db_id))
    updated += 1
print(f'Batch-7-retry: updated {updated} products')

# batch-10 results
cats10 = ['其他玩具','手工DIY','桌游','其他玩具','手工DIY','手工DIY','桌游','桌游','积木/拼装','角色扮演']
with open(r'D:\projects\supplier_crawler\panda_batch_10.json', 'r', encoding='utf-8') as f:
    items = json.load(f)
updated = 0
for idx, item in enumerate(items):
    db_id = item['id']
    cat = f'玩具 > 玩具游戏 > {cats10[idx]}'
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, db_id))
    updated += 1
print(f'Batch-10: updated {updated} products')

# batch-11 results (from sessions_history - classify by name pattern)
# ARMA JOYAS = jewelry making = 手工DIY, MONOPATIN = scooter = 玩具车, BUBBLE = bubble toy = 其他玩具, KIT ARTE = art kit = 手工DIY
# SINGLE ROW = unknown, likely 其他玩具
cats11 = ['其他玩具','手工DIY','手工DIY','手工DIY','手工DIY','手工DIY','手工DIY','玩具车','其他玩具','手工DIY']
with open(r'D:\projects\supplier_crawler\panda_batch_11.json', 'r', encoding='utf-8') as f:
    items = json.load(f)
updated = 0
for idx, item in enumerate(items):
    db_id = item['id']
    cat = f'玩具 > 玩具游戏 > {cats11[idx]}'
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, db_id))
    updated += 1
print(f'Batch-11: updated {updated} products')

conn.commit()

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND category != '玩具 > 玩具游戏'")
print(f'Classified: {cur.fetchone()[0]}')
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND category = '玩具 > 玩具游戏'")
print(f'Pending: {cur.fetchone()[0]}')

conn.close()
