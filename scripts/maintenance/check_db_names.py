# -*- coding: utf-8 -*-
"""检查数据库中各供应商的商品数量"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\projects\supplier_crawler')
from database.db_manager import DatabaseManager
import configparser

config = configparser.ConfigParser()
config.read(r'D:\projects\supplier_crawler\config.ini', encoding='utf-8')

db = DatabaseManager(config['database'])
names = db.get_existing_product_names(8)  # 1688供应商ID
print(f"供应商8 (1688) 数据库中已有商品名数量: {len(names)}")
if names:
    for n in list(names)[:10]:
        print(f"  {n}")
else:
    print("  (空) — 断点续传不会跳过任何商品")

# 再查所有供应商
for sid in range(1, 9):
    names = db.get_existing_product_names(sid)
    print(f"供应商{sid}: {len(names)} 条记录")
