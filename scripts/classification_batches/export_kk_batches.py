import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 导出全量KK数据，分批供AI复查
cur.execute("""
    SELECT id, name, category 
    FROM products WHERE supplier_id=10 
    ORDER BY id
""")
rows = cur.fetchall()

# 分成50条一批
batch_size = 50
batches = []
for i in range(0, len(rows), batch_size):
    batch = [{"id": r[0], "name": r[1], "current_cat": r[2]} for r in rows[i:i+batch_size]]
    batches.append(batch)

print(f"总数据: {len(rows)} 条")
print(f"分批: {len(batches)} 批 (每批{batch_size}条)")

# 保存前5批用于启动
for i, batch in enumerate(batches[:5]):
    with open(f'D:/projects/supplier_crawler/kk_batch_{i}.json', 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f"  kk_batch_{i}.json: ID {batch[0]['id']}-{batch[-1]['id']}")

conn.close()
