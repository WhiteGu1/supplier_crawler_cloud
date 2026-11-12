import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
# 清空 Trapoman 所有分类，重新审查
cur.execute("UPDATE products SET category=NULL WHERE supplier_id=3 AND is_available=1")
conn.commit()
print(f"已清空 Trapoman 分类: {cur.rowcount} 条")
conn.close()
