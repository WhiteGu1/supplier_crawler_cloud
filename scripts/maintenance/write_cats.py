"""将分类列表写入简洁文件供subagent读取"""
import pymysql, json, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category!='' ORDER BY category")
cats = [r[0] for r in cur.fetchall()]
conn.close()

with open(r"D:\projects\supplier_crawler\classify_cache\new_products\cats.txt", "w", encoding="utf-8") as f:
    for c in cats:
        f.write(c + "\n")
print(f"写入{len(cats)}个分类")
