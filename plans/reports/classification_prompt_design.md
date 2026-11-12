# 商品分类提示词 + 规则 v2

## 完整提示词

```
你是一个专业的商品分类专家。你的任务是将一批商品分配到最合适的分类标签中。

## 分类规则

1. 分类格式为三级结构：一级分类 > 二级分类 > 三级分类
2. 必须从现有分类标签列表中选择；如果列表中没有合适的分类，可以创建新分类
3. 创建新分类时，必须在现有的一级分类体系内创建，不得新建一级分类
4. 一级分类固定为以下13个，不可修改：
   - 厨房用品
   - 家居生活
   - 拖件礼品
   - 文具
   - 玩具
   - 化妆品饰品
   - 箱包皮具
   - 电子电器
   - 运动户外
   - 母婴用品
   - 宠物
   - 五金
   - 服装鞋帽

5. 分类精度要求：
   - 尽量分到三级（最精确）
   - 如果商品信息不足以判断三级，可以保留在二级
   - 不得只分到一级

## 现有分类标签列表

{{CATEGORY_LIST}}

## 输入数据

每批100个商品，格式为JSON数组：
```json
[
  {"id": 12345, "name": "商品名称", "sku": "SKU123", "brand": "品牌", "supplier": "供应商", "price": 12.50, "current_category": "厨房用品 > 餐具"},
  ...
]
```

## 输出格式

返回JSON，包含两个部分：

```json
{
  "assignments": [
    {"id": 12345, "category": "厨房用品 > 餐具 > 刀叉勺"},
    {"id": 12346, "category": "厨房用品 > 餐具 > 盘子"}
  ],
  "new_categories": [
    {
      "category": "厨房用品 > 餐具 > 封口夹",
      "reason": "现有列表中没有封口夹相关分类，新增三级分类"
    }
  ]
}
```

## 分类原则

1. **以商品名称为主要依据**：商品名称通常包含最关键的分类信息
2. **参考SKU和品牌**：辅助判断
3. **不要过度细分**：如果二级已经足够精确，不必强制分到三级
4. **新分类要通用**：新创建的三级分类应该能覆盖多件商品，而非只为一件商品创建
5. **保持一致性**：同类商品必须分到同一分类
6. **名称规范**：三级分类名简洁明了，2-6个字，用"XX"或"XX/XX"格式（如"刀叉勺"、"保温壶/保温杯"）
7. **每个商品必须分配分类**，不允许跳过

## 执行流程

1. 读取现有分类标签列表
2. 逐个分析商品，匹配最合适的分类
3. 如果现有分类都不合适，在对应一级>二级下创建新的三级分类
4. 如果连二级都不合适，在对应一级下创建新的二级分类
5. 记录所有新建的分类及创建理由
6. 输出完整的JSON结果
```

## v2 规则：缓存比对验证机制

### 核心流程

```
商品数据 → AI分类（每批100条）→ 缓存文件 → 与数据库比对 → 识图验证差异 → 取优写入数据库
```

### 四个阶段

**阶段1：AI分类 → 缓存文件**
- 取100条商品，调用AI分类
- 结果写入 `classify_cache/batch_{N}.json`，**不写数据库**
- 新分类标签追加到列表，供下一批使用

**阶段2：与数据库比对**
- 缓存中的new_category vs 数据库中的old_category
- 标记：changed / same / new_l2 / new_l3
- 写入 `batch_{N}_diff.json`

**阶段3：识图验证差异项**
- 对 changed 且有图的商品，用 image 工具验证
- 有图商品：识图确认分类是否正确
- 无图商品：信任AI基于名称的分类

**阶段4：取优写入**
- 识图通过 → 写入新分类
- 识图不通过 → 保留原分类，记录到 mismatch.log
- 无图 → 直接写入新分类

### 缓存文件格式

`classify_cache/batch_{N}.json`：
```json
{
  "batch_id": 1,
  "timestamp": "2026-07-18T14:00:00",
  "total": 100,
  "model": "pool-glm-5.2",
  "assignments": [
    {
      "id": 12345,
      "name": "CACEROLA CON ASA 20CM",
      "old_category": "厨房用品 > 炊具",
      "new_category": "厨房用品 > 炊具 > 汤锅/炖锅",
      "image_local": "images/sfpanda/xxx.jpg",
      "has_image": true
    }
  ],
  "new_categories": [{"category": "...", "reason": "..."}]
}
```

`classify_cache/batch_{N}_diff.json`：
```json
{
  "batch_id": 1,
  "summary": {"changed": 65, "same": 35, "need_image_verify": 45, "no_image": 20},
  "items": [
    {
      "id": 12345,
      "name": "CACEROLA CON ASA 20CM",
      "old_category": "厨房用品 > 炊具",
      "new_category": "厨房用品 > 炊具 > 汤锅/炖锅",
      "has_image": true,
      "image_path": "D:/projects/supplier_crawler/images/sfpanda/xxx.jpg",
      "image_verified": true,
      "final_category": "厨房用品 > 炊具 > 汤锅/炖锅"
    }
  ]
}
```

### 识图验证方案

用 OpenClaw `image` 工具（通过 `sessions_spawn` 子agent）：

```javascript
sessions_spawn({
  task: `用 image 工具查看图片 D:/projects/supplier_crawler/images/sfpanda/xxx.jpg
判断商品分类是否正确：
商品名称: CACEROLA CON ASA 20CM
AI建议分类: 厨房用品 > 炊具 > 汤锅/炖锅

输出JSON: {"match": true/false, "description": "商品描述", "suggested": "正确分类或null"}`,
  model: "qclaw/pool-minimax-m3",
  mode: "run",
  taskName: "verify-batch-1-001"
})
```

### 目录结构

```
D:\projects\supplier_crawler\classify_cache\
├── batch_1.json          # AI分类结果
├── batch_1_diff.json     # 比对+验证结果
├── batch_2.json
├── batch_2_diff.json
├── ...
├── mismatch.log          # 识图验证不匹配记录
└── summary.json          # 全局统计
```

### 执行流程伪代码

```python
import json, os, pymysql

CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache"

def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    category_list = load_categories_from_db()  # 初始213个
    
    batch_num = 1
    while True:
        # 阶段1: AI分类 → 缓存
        products = fetch_batch(100)
        if not products:
            break
        
        assignments, new_cats = call_ai_classify(products, category_list)
        
        cache = build_cache(batch_num, assignments, new_cats, products)
        write_json(f"{CACHE_DIR}/batch_{batch_num}.json", cache)
        
        # 阶段2: 比对
        diff = compare_with_db(cache)
        write_json(f"{CACHE_DIR}/batch_{batch_num}_diff.json", diff)
        
        # 阶段3: 识图验证
        for item in diff["items"]:
            if item["old_category"] == item["new_category"]:
                item["final_category"] = item["old_category"]
            elif item["has_image"]:
                result = verify_by_image(item)  # 调用image工具
                item["image_verified"] = result["match"]
                item["final_category"] = item["new_category"] if result["match"] else (result.get("suggested") or item["old_category"])
            else:
                item["final_category"] = item["new_category"]
        
        write_json(f"{CACHE_DIR}/batch_{batch_num}_diff.json", diff)
        
        # 阶段4: 写入数据库
        for item in diff["items"]:
            if item["final_category"] != item["old_category"]:
                update_db(item["id"], item["final_category"])
        
        # 新分类加入列表
        for nc in new_cats:
            category_list.append(nc["category"])
        
        print(f"Batch {batch_num}: {len(assignments)}条, 差异{diff['summary']['changed']}条")
        batch_num += 1
```

## 现有数据概览

| 指标 | 数值 |
|------|------|
| 商品总数 | 23596 |
| 有图商品 | 12686 (53.8%) |
| 无图商品 | 10915 (46.2%) |
| 现有分类数 | 213 (13一级/34二级/183三级) |
| 停留在二级未细分 | ~11878条 (50.3%) |
| 预计批次 | ~236批 |
