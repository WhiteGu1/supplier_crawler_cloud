import sqlite3
conn = sqlite3.connect(r'D:\projects\supplier_crawler\database\supplier_crawler.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("Tables:", tables)
for t in tables:
    cursor.execute(f"PRAGMA table_info({t})")
    cols = [(r[1], r[2]) for r in cursor.fetchall()]
    print(f"\n{t}: {cols}")
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  rows: {cursor.fetchone()[0]}")
conn.close()
