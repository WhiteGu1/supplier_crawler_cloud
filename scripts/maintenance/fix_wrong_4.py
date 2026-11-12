"""修正4条验证错误的分类"""
import sys, pymysql
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}

corrections = {
    13497: "家居生活 > 收纳整理",  # 纸巾架，保留旧分类
    13512: "厨房用品 > 炊具 > 烹饪工具",  # 烧烤3件套，应为烹饪工具
    13514: "厨房用品 > 炊具 > 烹饪工具",  # 24件烧烤套装，应为烹饪工具
    13532: "厨房用品 > 炊具 > 烹饪工具",  # 厨房秤，放在炊具下比餐饮水具合理
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

for pid, cat in corrections.items():
    cursor.execute("UPDATE products SET category = %s WHERE id = %s", (cat, pid))
    print(f"  id={pid} -> {cat} (affected={cursor.rowcount})")

conn.commit()
conn.close()
print(f"\n修正完成，共{len(corrections)}条")
