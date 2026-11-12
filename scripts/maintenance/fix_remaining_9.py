import sys
sys.stdout.reconfigure(encoding='utf-8')
import pymysql, json

# 9条osa商品的分类（基于西班牙语名称判断）
classifications = {
    35789: ["厨房用品 > 烹饪锅具 > 炖锅"],        # Bifera "fuego roja" PYREX - 红色火焰炖锅
    35790: ["厨房用品 > 烹饪锅具 > 汤锅"],        # Cacerola "fuego roja" PYREX - 红色火焰汤锅
    35791: ["厨房用品 > 烹饪锅具 > 煎锅"],        # Sarten "fuego roja" PYREX - 红色火焰煎锅
    35792: ["厨房用品 > 调酒器具 > 摇酒器"],      # Coctelera Acero 600ml con filtro - 带滤网不锈钢摇酒器
    35793: ["厨房用品 > 厨房刀具 > 主厨刀"],      # Cuchillo Pyrex Chef Centurion 20cm - 主厨刀
    35794: ["厨房用品 > 厨房刀具 > 多功能刀"],    # Cuchillo Pyrex Utility Centurion 12cm - 多功能刀
    35795: ["厨房用品 > 厨房刀具 > 三德刀"],      # Cuchillo Pyrex Santoku Centurion 17cm - 三德刀
    35796: ["厨房用品 > 茶饮器具 > 茶杯碟套装"],  # Taza de te con plato 200cc - 带碟茶杯
    35797: ["厨房用品 > 厨房工具 > 切薯器"],      # Corta Papas de Acero Inoxidable - 不锈钢切薯条器
}

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 写入product_categories
for pid, cats in classifications.items():
    for cat in cats:
        cur.execute("INSERT IGNORE INTO product_categories (product_id, category) VALUES (%s, %s)", (pid, cat))
    # 同步products.category
    cur.execute("UPDATE products SET category = %s WHERE id = %s AND (category IS NULL OR category = '')", (cats[0], pid))
    print(f"  id={pid} -> {cats[0]}")

conn.commit()

# 验证
cur.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category = ''")
print(f"\n无分类商品数: {cur.fetchone()[0]}")

conn.close()
