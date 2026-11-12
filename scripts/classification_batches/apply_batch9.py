import sys, io, pymysql, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# batch-9 results
cats9 = ['玩具车','玩具车','玩具车','角色扮演','解压玩具','积木/拼装','角色扮演','角色扮演','角色扮演','毛绒玩具']
with open(r'D:\projects\supplier_crawler\panda_batch_9.json', 'r', encoding='utf-8') as f:
    items = json.load(f)
updated = 0
for idx, item in enumerate(items):
    db_id = item['id']
    cat = f'玩具 > 玩具游戏 > {cats9[idx]}'
    cur.execute('UPDATE products SET category=%s WHERE id=%s', (cat, db_id))
    updated += 1
print(f'Batch-9: updated {updated} products')

conn.commit()

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND category != '玩具 > 玩具游戏'")
print(f'Classified: {cur.fetchone()[0]}')
cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=11 AND category = '玩具 > 玩具游戏'")
print(f'Pending: {cur.fetchone()[0]}')

conn.close()
