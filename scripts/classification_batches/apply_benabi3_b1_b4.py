import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-1 results
results_b1 = [
  {"id": 20362, "category": "厨房餐具", "desc": "竖纹玻璃水杯带竹木盖和玻璃吸管"},
  {"id": 20363, "category": "厨房餐具", "desc": "透明玻璃杯带粉色手柄、竹木盖和玻璃吸管"},
  {"id": 20364, "category": "厨房餐具", "desc": "方形玻璃梅森杯带手柄、竹木盖和吸管"},
  {"id": 20365, "category": "厨房餐具", "desc": "竖纹花纹玻璃马克杯带金色边饰和手柄"},
  {"id": 20366, "category": "厨房餐具", "desc": "切割花纹水晶风格透明玻璃杯"},
  {"id": 20367, "category": "厨房餐具", "desc": "四只珍珠奶茶造型创意饮水杯套装"},
  {"id": 20368, "category": "厨房餐具", "desc": "花纹玻璃啤酒杯/扎杯带手柄"},
  {"id": 20369, "category": "厨房餐具", "desc": "四只镭射渐变塑料随行杯带穹顶盖和吸管"},
  {"id": 20370, "category": "厨房餐具", "desc": "无柄葡萄酒杯"},
  {"id": 20371, "category": "厨房餐具", "desc": "星巴克渐变菱格纹冷饮随行杯带吸管"},
]

# batch-4 results
results_b4 = [
  {"id": 20432, "category": "美妆个护", "desc": "气垫梳黑色手柄带金色装饰球形梳齿"},
  {"id": 20433, "category": "美妆个护", "desc": "金色框架气垫梳黑色软垫白色球尖梳齿"},
  {"id": 20434, "category": "美妆个护", "desc": "蓝绿色气垫梳软垫底座弹性梳齿"},
  {"id": 20435, "category": "美妆个护", "desc": "圆筒通风梳木质手柄吹风造型用"},
  {"id": 20436, "category": "派对用品", "desc": "儿童派对梳皇冠手柄薄荷绿和粉色6把装"},
  {"id": 20437, "category": "美妆个护", "desc": "猫耳化妆镜粉色白色树枝造型底座"},
  {"id": 20438, "category": "美妆个护", "desc": "猫耳双面化妆镜粉色白色心形叶片装饰"},
  {"id": 20439, "category": "美妆个护", "desc": "椭圆桌面化妆镜黑色边框玫瑰金支架"},
  {"id": 20440, "category": "美妆个护", "desc": "LED椭圆化妆镜粉色白色触控调光"},
  {"id": 20441, "category": "美妆个护", "desc": "双面桌面化妆镜银色玫瑰金可旋转"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

updated = 0
for r in results_b1 + results_b4:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-1+4: 成功更新 {updated}/{len(results_b1)+len(results_b4)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
