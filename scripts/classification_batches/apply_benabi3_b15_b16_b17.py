import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# batch-15 results
results15 = [
  {"id": 25114, "category": "卫浴用品", "desc": "浴室洗漱套装皂液器收纳罐肥皂碟"},
  {"id": 25115, "category": "美妆个护", "desc": "猫爪按摩气垫梳粉色和米黄色两款"},
  {"id": 25116, "category": "宠物用品", "desc": "宠物毛发梳按摩梳卡通造型带亮片装饰"},
  {"id": 25117, "category": "美妆个护", "desc": "气垫按摩梳粉蓝渐变马卡龙配色"},
  {"id": 25118, "category": "美妆个护", "desc": "平板按摩梳深棕色带圆柱梳齿"},
  {"id": 25119, "category": "美妆个护", "desc": "木柄气垫按摩梳浅粉色椭圆底座"},
  {"id": 25120, "category": "美妆个护", "desc": "粉色椭圆形三脚架桌台式化妆镜"},
  {"id": 25121, "category": "美妆个护", "desc": "15倍放大化妆镜带吸盘便携式"},
  {"id": 25122, "category": "美妆个护", "desc": "LED台式化妆镜粉色和白色两款带灯补光"},
  {"id": 25123, "category": "文具办公", "desc": "减压陀螺笔彩虹云朵卡通造型"},
]

# batch-16 results
results16 = [
  {"id": 25124, "category": "文具办公", "desc": "Benabi魔法变色马克笔套装8支彩色马克笔红色纸盒"},
  {"id": 25125, "category": "文具办公", "desc": "Benabi变色神奇马克笔套装10支彩色马克笔红色盒子"},
  {"id": 25126, "category": "文具办公", "desc": "12色丙烯马克笔套装透明塑料收纳盒防水不掉色"},
  {"id": 25127, "category": "收纳整理", "desc": "迷你笑脸收纳盒3件套马卡龙色系塑料材质带翻盖"},
  {"id": 25128, "category": "文具办公", "desc": "BESTDI QUQU系列荧光笔4色装动物造型笔盖"},
  {"id": 25129, "category": "文具办公", "desc": "马卡龙色高亮笔套装6支护眼色系"},
  {"id": 25130, "category": "文具办公", "desc": "Benabi双头荧光笔套装凿子形笔尖每包2支"},
  {"id": 25131, "category": "文具办公", "desc": "Benabi修正带12米长度4色可选彩虹条纹包装"},
  {"id": 25132, "category": "文具办公", "desc": "彩色便签纸标签贴套装含5色窄条标签贴和长条便签纸"},
  {"id": 25133, "category": "文具办公", "desc": "Jinxin星形箭头便利贴索引标签3色PET材质"},
]

# batch-17 results
results17 = [
  {"id": 25134, "category": "文具办公", "desc": "4D战斗机造型橡皮擦彩色立体飞机形状橡皮独立包装"},
  {"id": 25135, "category": "文具办公", "desc": "双叶文具2B橡皮擦彩虹色包装30块每盒"},
  {"id": 25136, "category": "文具办公", "desc": "8英寸剪刀三把套装橙红绿三色金属刀片配塑料手柄"},
  {"id": 25137, "category": "文具办公", "desc": "2合1卷笔刀橡皮擦EXCELLENT BABY品牌樱花兔卡通造型"},
  {"id": 25138, "category": "文具办公", "desc": "鼎力固体胶棒DL K15 15g每支无毒无酸24支每盒"},
  {"id": 25139, "category": "文具办公", "desc": "金鑫彩色便利贴索引贴5色装长条书签型"},
  {"id": 25140, "category": "文具办公", "desc": "学生文具袋铅笔袋4款拉链式长方形清新可爱图案"},
  {"id": 25141, "category": "文具办公", "desc": "螺旋装订笔记本4本套装植物花卉主题文艺水彩手绘"},
  {"id": 25142, "category": "日用百货", "desc": "儿童卡通雨伞5把动物图案印花波浪花边装饰"},
  {"id": 25143, "category": "日用百货", "desc": "黑色长柄弯柄雨伞经典商务款多骨伞架"},
]

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()
all_results = results15 + results16 + results17
updated = 0
for r in all_results:
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (r['category'], r['id']))
    updated += cur.rowcount
conn.commit()
print(f"batch-15 + batch-16 + batch-17: 成功更新 {updated}/{len(all_results)} 条")

cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id=4 AND (category IS NULL OR category='') AND image_local IS NOT NULL AND image_local != ''")
remaining = cur.fetchone()[0]
print(f"benabi 剩余有图未分类: {remaining}")

conn.close()
