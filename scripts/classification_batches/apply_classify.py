import pymysql, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# 4个子agent的完整结果
results = [
  {"id": 15240, "category": "厨房餐具", "description": "透明塑料长柄汤勺/水瓢，带螺旋纹手柄"},
  {"id": 15241, "category": "餐饮用品", "description": "透明塑料装饰餐盘，菱形切割花纹"},
  {"id": 15242, "category": "收纳整理", "description": "镂空塑料编织长方形收纳篮，有黑白米三色"},
  {"id": 15243, "category": "厨房餐具", "description": "透明塑料沙拉碗，带花瓣装饰花纹"},
  {"id": 15244, "category": "餐饮用品", "description": "透明塑料装饰点心盘/果盘，八角形放射状花纹"},
  {"id": 15245, "category": "厨房储物", "description": "透明亚克力钻石形冰格制冰模具"},
  {"id": 15246, "category": "餐饮用品", "description": "麦秸秆材质长方形托盘（米色/砖红/蓝/绿四色套装）"},
  {"id": 15249, "category": "厨房炊具", "description": "黑色不粘烤盘/烘焙托盘配绿色防滑边框"},
  {"id": 15250, "category": "厨房炊具", "description": "红黑硅胶铲漏式煎铲/牛排铲"},
  {"id": 15251, "category": "厨房餐具", "description": "透明钻石纹玻璃威士忌杯/水杯（6件套）"},
  {"id": 15263, "category": "收纳整理", "description": "塑料镂空洗衣篮/收纳筐，带提手，米色"},
  {"id": 15264, "category": "清洁用品", "description": "塑料镂空垃圾桶/废纸篓，带盖，黑色"},
  {"id": 15265, "category": "收纳整理", "description": "塑料长方形镂空收纳篮/储物筐，黑色"},
  {"id": 15266, "category": "厨房餐具", "description": "高脚玻璃甜品杯/布丁杯，6件套装"},
  {"id": 15267, "category": "卫浴用品", "description": "方形塑料边框镜子，PRIMAFER品牌，粉色包装"},
  {"id": 15268, "category": "卫浴用品", "description": "Primafer圆形镜子，带粉色包装盒"},
  {"id": 15269, "category": "厨房炊具", "description": "Imperial心形铝制蛋糕烤模"},
  {"id": 15270, "category": "厨房炊具", "description": "Imperial星形铝制蛋糕烤模"},
  {"id": 15271, "category": "美妆个护", "description": "Iluminarte香薰精油（多种香味10ml装）"},
  {"id": 15272, "category": "美妆个护", "description": "Aromanza藏式香薰棒（5种香味礼盒装）"}
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

updated = 0
for r in results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount

conn.commit()
print(f"成功更新 {updated}/{len(results)} 条商品分类")

# 验证
cur.execute("SELECT id, name, category FROM products WHERE id IN (%s)" % ','.join(str(r['id']) for r in results))
for row in cur.fetchall():
    print(f"  {row[0]}\t{row[2]}\t{row[1]}")

conn.close()
