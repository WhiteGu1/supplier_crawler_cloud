import sys
import os
import pymysql

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.stdout.reconfigure(encoding='utf-8')

from crawler.pdf_parsers.gaston import parse

pdf_path = r"C:\Users\Administrator\Downloads\gaston\CATALOGO_SP_compressed-DZa5fbhjobJkk1dEMLOaNalotdlOFL.pdf"
images_dir = r"d:\projects\supplier_crawler\images"
sid = 16

print("=== 重新解析 CATALOGO_SP 并提取正确图片 ===")
products = parse(pdf_path, images_dir, sid)
print(f"解析提取了 {len(products)} 款商品")

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4'
)
cur = conn.cursor()

updated_count = 0
for p in products:
    sku = p.get('sku')
    img = p.get('image')
    if sku and img:
        # 确保数据库中的 image_url 更新为新生成的正确图片路径
        cur.execute("UPDATE products SET image_url=%s WHERE supplier_id=%s AND sku=%s", (img, sid, sku))
        if cur.rowcount > 0:
            updated_count += 1

conn.commit()
print(f"成功更新数据库中 {updated_count} 款商品的正确图片路径！")

# 检查几个典型商品的图片路径
cur.execute("SELECT sku, name, image_url FROM products WHERE sku IN ('C02109OR', 'C01793UC', 'C02020UC', 'C01786UC', 'SH4408MI')")
for r in cur.fetchall():
    print(r)

conn.close()
