# -*- coding: utf-8 -*-
"""修复数据库中1688供应商的cdp_url: 9223 -> 9222"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import mysql.connector

conn = mysql.connector.connect(
    host="localhost", port=3306, user="root", password="admin123",
    database="supplier_crawler", use_pure=True
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, name, selectors FROM suppliers WHERE name LIKE '%1688%'")
for row in cursor.fetchall():
    sel = json.loads(row['selectors']) if isinstance(row['selectors'], str) else row['selectors']
    print(f"供应商 {row['id']} ({row['name']}): cdp_url={sel.get('cdp_url','N/A')}")
    if '9223' in sel.get('cdp_url', ''):
        sel['cdp_url'] = 'http://localhost:9222'
        cursor.execute("UPDATE suppliers SET selectors=%s WHERE id=%s",
                      (json.dumps(sel, ensure_ascii=False), row['id']))
        conn.commit()
        print(f"  ✅ 已修复为 9222")
    else:
        print(f"  无需修复")
conn.close()
