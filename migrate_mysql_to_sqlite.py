"""
从 MySQL 迁移数据到 SQLite
运行一次即可，迁移完成后可停用 MySQL
"""
import json, sqlite3, sys

# ── 配置 ──────────────────────────────────────
MYSQL_HOST     = "localhost"
MYSQL_PORT     = 3306
MYSQL_USER     = "root"
MYSQL_PASSWORD = "admin123"   # ← 改成你的MySQL密码
MYSQL_DB       = "supplier_crawler"
SQLITE_PATH    = "supplier_crawler.db"
# ─────────────────────────────────────────────

try:
    import pymysql
    mysql = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
                            password=MYSQL_PASSWORD, database=MYSQL_DB,
                            cursorclass=pymysql.cursors.DictCursor)
except ImportError:
    try:
        import mysql.connector
        mysql = mysql.connector.connect(host=MYSQL_HOST, port=MYSQL_PORT,
                                        user=MYSQL_USER, password=MYSQL_PASSWORD,
                                        database=MYSQL_DB)
        mysql.cursor = lambda: mysql.cursor(dictionary=True)
    except Exception as e:
        print(f"无法连接MySQL: {e}")
        sys.exit(1)

lite = sqlite3.connect(SQLITE_PATH)
lite.row_factory = sqlite3.Row
lite.execute("PRAGMA foreign_keys=OFF")

def migrate_table(table, mysql_conn, lite_conn):
    cur = mysql_conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    if not rows:
        print(f"  {table}: 0 条，跳过")
        return
    cols = list(rows[0].keys())
    placeholders = ",".join(["?"] * len(cols))
    col_names = ",".join(cols)
    # 处理datetime对象
    def clean(v):
        if hasattr(v, 'strftime'):
            return v.strftime("%Y-%m-%d %H:%M:%S")
        return v
    data = [tuple(clean(r[c]) for c in cols) for r in rows]
    lite_conn.executemany(
        f"INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})", data
    )
    lite_conn.commit()
    print(f"  {table}: 迁移 {len(rows)} 条 ✅")

print("开始迁移 MySQL → SQLite...")
for t in ["suppliers", "products", "price_history", "crawl_logs"]:
    try:
        migrate_table(t, mysql, lite)
    except Exception as e:
        print(f"  {t}: 失败 - {e}")

mysql.close()
lite.close()
print("\n迁移完成！SQLite 文件:", SQLITE_PATH)
