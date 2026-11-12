import pymysql, json, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 查 benabi 供应商ID和未分类商品
cur.execute("SELECT id FROM suppliers WHERE name LIKE '%benabi%'")
row = cur.fetchone()
if not row:
    print("未找到 benabi 供应商")
    conn.close()
    exit()
supplier_id = row[0]
print(f"benabi supplier_id={supplier_id}")

# 拉取所有未分类商品
cur.execute("""
    SELECT id, image_local FROM products 
    WHERE supplier_id=%s AND is_available=1 
    AND (category IS NULL OR category = '' OR category = '未分类')
    ORDER BY id
""", (supplier_id,))

products = []
for r in cur.fetchall():
    pid = r[0]
    img = r[1]
    if img:
        # 标准化路径
        img_path = img.replace('\\', '/')
        if not img_path.startswith('D:/'):
            img_path = f"D:/projects/supplier_crawler/images/benabi/{img_path.split('/')[-1]}"
        products.append({"id": pid, "img": img_path})
    else:
        print(f"  警告: ID:{pid} 无图片路径")

print(f"未分类商品: {len(products)} 条")

# 生成分批，每批10个
batches = []
for i in range(0, len(products), 10):
    batches.append(products[i:i+10])

print(f"共 {len(batches)} 批")

with open('D:/projects/supplier_crawler/benabi_batches.json', 'w', encoding='utf-8') as f:
    json.dump(batches, f, ensure_ascii=False, indent=2)

print("已保存到 benabi_batches.json")

# 显示前几批
for i in range(min(3, len(batches))):
    print(f"\n=== BATCH {i} ===")
    for j, item in enumerate(batches[i]):
        print(f"{j+1}. ID:{item['id']}, 路径: {item['img']}")

conn.close()
