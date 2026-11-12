import pymysql, json, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT id, name, image_local FROM products WHERE supplier_id=5 AND image_local IS NOT NULL AND image_local != '' AND id > 2475 ORDER BY id")
rows = cur.fetchall()
print(f'remaining: {len(rows)}')
batches = []
for i in range(0, len(rows), 50):
    batch = [{'id': r[0], 'name': r[1], 'img': r[2]} for r in rows[i:i+50]]
    batches.append(batch)
print(f'batches(50/batch): {len(batches)}')
for i, b in enumerate(batches[:5]):
    print(f'batch-{i}: ID {b[0]["id"]}-{b[-1]["id"]}, {len(b)} items')
with open('D:/projects/supplier_crawler/diego_50_batches.json', 'w', encoding='utf-8') as f:
    json.dump(batches, f, ensure_ascii=False)
conn.close()
