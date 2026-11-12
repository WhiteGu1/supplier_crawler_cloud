"""分析二级分类筛选bug"""
import pymysql

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

# 查看前端选"全部二级"时传的值
# 前端: ssel.innerHTML = '<option value="' + main + '">全部二级分类</option>'
# 即 value = main (一级分类名，如 "厨房用品")
# loadProducts: catVal = catL3 || catSub || catMain
# 如果只选了一级没选二级，catSub=""，catVal = catMain = "厨房用品"
# 后端: if ' > ' in cat → 精确匹配; else → (category=%s OR category LIKE %s + ' > %')
# 这个逻辑是对的，应该能匹配到

# 但如果选了二级"全部"（value=main），catSub=main
# catVal = catL3("") || catSub(main) || catMain(main) = main
# 这和只选一级是一样的，应该也能匹配

# 问题可能出在：选了二级分类后，二级value是"main > sub"
# 然后选"全部三级"时catL3=""，catVal=catSub="main > sub"
# 后端 ' > ' in cat → 精确匹配 category="main > sub"
# 但实际数据库中三级分类是"main > sub > l3"，不会精确等于"main > sub"

# 验证：
cur.execute("SELECT DISTINCT category FROM products WHERE category LIKE '厨房用品 > 餐具%' LIMIT 10")
for r in cur.fetchall():
    print(r['category'])

print("\n--- 测试精确匹配二级 ---")
# 如果传 category="厨房用品 > 餐具"，后端走精确匹配
cur.execute("SELECT COUNT(*) as cnt FROM products WHERE category='厨房用品 > 餐具'")
print(f"精确匹配 '厨房用品 > 餐具': {cur.fetchone()['cnt']}")

cur.execute("SELECT COUNT(*) as cnt FROM products WHERE category LIKE '厨房用品 > 餐具 > %'")
print(f"前缀匹配 '厨房用品 > 餐具 > %': {cur.fetchone()['cnt']}")

# 确认bug：选了二级分类"餐具"后，catSub="厨房用品 > 餐具"
# catVal = catSub = "厨房用品 > 餐具"（有" > "）
# 后端走 conditions.append("p.category=%s") → 精确匹配
# 但数据库中没有 category='厨房用品 > 餐具' 的记录，只有 '厨房用品 > 餐具 > 碗/盆'
# 所以结果为空！

print("\n--- 结论 ---")
print("Bug根因：选了二级分类后，catVal含' > '，后端走精确匹配")
print("但二级分类名不是实际商品分类（三级才是），所以匹配不到任何商品")
print("修复方案：后端对含' > '的分类也增加 LIKE 前缀匹配")

conn.close()
