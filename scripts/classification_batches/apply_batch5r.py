import sys, io, pymysql, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-5-retry results
cats5r = ['玩具车','手工DIY','玩具车','玩具车','其他玩具','手工DIY','桌游','其他玩具','角色扮演','手工DIY']
with open(r'D:\projects\supplier_crawler\panda_batch_5.json', 'r', encoding='utf-8') as f:
    items = json.load(f)
updated = 0
for idx, item in enumerate(items):
    db_id = item['id']
    cat = f'玩具 > 玩具游戏 > {cats5r[idx]}'
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, db_id))
    updated += 1
print(f'Batch-5-retry: updated {updated} products')

conn.commit()

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND category != '玩具 > 玩具游戏'")
print(f'Classified: {cur.fetchone()[0]}')
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND category = '玩具 > 玩具游戏'")
print(f'Pending: {cur.fetchone()[0]}')

conn.close()
