import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 随机抽取100条做测试
cur.execute("""
    SELECT id, name, category 
    FROM products WHERE supplier_id=10 
    ORDER BY RAND() LIMIT 100
""")
rows = cur.fetchall()

# 输出为JSON供子agent复查
data = [{"id": r[0], "name": r[1], "current_cat": r[2]} for r in rows]
with open('D:/projects/supplier_crawler/kk_review_sample.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"已导出100条抽样数据到 kk_review_sample.json")
print(f"ID范围: {rows[0][0]} - {rows[-1][0]}")
print("\n抽样数据:")
for d in data[:20]:
    print(f"  ID:{d['id']} [{d['current_cat']}] {d['name'][:70] if d['name'] else 'N/A'}")

conn.close()
