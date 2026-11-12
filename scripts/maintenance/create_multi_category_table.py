"""创建多分类关联表并迁移现有数据"""
import pymysql

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

# 1. 创建多分类表
cur.execute("""
CREATE TABLE IF NOT EXISTS product_categories (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id  BIGINT NOT NULL,
    category    VARCHAR(100) NOT NULL,
    is_primary  TINYINT(1) DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_product (product_id),
    INDEX idx_category (category),
    UNIQUE KEY uk_product_category (product_id, category),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
conn.commit()
print("表创建成功")

# 2. 迁移现有分类数据
cur.execute("""
INSERT IGNORE INTO product_categories (product_id, category, is_primary)
SELECT id, category, 1 FROM products WHERE category IS NOT NULL AND category != ''
""")
conn.commit()
print(f"迁移完成: {cur.rowcount} 条记录")

cur.execute("SELECT COUNT(*) FROM product_categories")
print(f"关联表总数: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM products WHERE category IS NOT NULL AND category != ''")
print(f"有分类商品数: {cur.fetchone()[0]}")

# 3. 检查二级筛选bug：看看有多少商品的category没有" > "分隔符
cur.execute("SELECT COUNT(*) FROM products WHERE category IS NOT NULL AND category != '' AND category NOT LIKE '% > %'")
print(f"扁平分类(无>分隔)商品数: {cur.fetchone()[0]}")

cur.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' AND category NOT LIKE '% > %' LIMIT 20")
flat_cats = [r[0] for r in cur.fetchall()]
print(f"扁平分类示例: {flat_cats}")

conn.close()
