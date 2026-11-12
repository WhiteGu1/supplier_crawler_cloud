# 商品分类规则 v2 —— 缓存比对验证机制

## 核心流程

```
商品数据 → AI分类（每批100条）→ 缓存文件 → 与数据库比对 → 识图验证 → 取优写入
```

## 阶段说明

### 阶段1：AI分类 → 缓存文件

1. 从数据库取100条商品（id、name、sku、brand、supplier_name、price、current_category、image_local）
2. 调用AI模型分类，输出JSON（assignments + new_categories）
3. **不写数据库**，写入缓存文件：`D:\projects\supplier_crawler\classify_cache\batch_{N}.json`

### 阶段2：与数据库比对

1. 读取缓存文件中的分类结果
2. 与数据库中现有category逐条比对
3. 标记差异：
   - `changed`：分类发生了变化
   - `same`：分类未变
   - `new_l2`：新建了二级分类
   - `new_l3`：新建了三级分类

### 阶段3：识图验证差异项

对`changed`的商品，用图片验证AI分类是否正确：

- **有图商品**：用 `image` 工具或 `modelroute_api` 多模态模型识图，验证分类是否匹配
- **无图商品**：跳过识图，直接信任AI基于商品名称的分类

### 阶段4：取优写入

- 识图验证通过 → 写入新分类
- 识图验证不通过 → 保留原分类，记录到 `mismatch.log`
- 无图商品 → 直接写入新分类

## 缓存文件格式

文件路径：`D:\projects\supplier_crawler\classify_cache\batch_{N}.json`

```json
{
  "batch_id": 1,
  "timestamp": "2026-07-18T14:00:00",
  "total": 100,
  "model": "pool-glm-5.2",
  "category_list_version": 213,
  "assignments": [
    {
      "id": 12345,
      "name": "CACEROLA CON ASA 20CM",
      "old_category": "厨房用品 > 炊具",
      "new_category": "厨房用品 > 炊具 > 汤锅/炖锅",
      "image_local": "images/sfpanda/xxx.jpg",
      "has_image": true,
      "verification": null
    }
  ],
  "new_categories": [
    {
      "category": "厨房用品 > 餐具 > 封口夹",
      "reason": "现有列表无封口夹分类"
    }
  ],
  "diff": {
    "changed": 65,
    "same": 35,
    "new_l2": 0,
    "new_l3": 3
  }
}
```

## 比对结果文件

文件路径：`D:\projects\supplier_crawler\classify_cache\batch_{N}_diff.json`

```json
{
  "batch_id": 1,
  "total": 100,
  "summary": {
    "changed": 65,
    "same": 35,
    "need_image_verify": 45,
    "no_image": 20
  },
  "items": [
    {
      "id": 12345,
      "name": "CACEROLA CON ASA 20CM",
      "old_category": "厨房用品 > 炊具",
      "new_category": "厨房用品 > 炊具 > 汤锅/炖锅",
      "has_image": true,
      "image_path": "D:/projects/supplier_crawler/images/sfpanda/xxx.jpg",
      "image_verified": null,
      "image_result": null,
      "final_category": null
    }
  ]
}
```

## 识图验证方案

### 方案A：OpenClaw image工具（子agent方式）

通过 `sessions_spawn` 启动子agent，用 `image` 工具逐张验证：

```javascript
sessions_spawn({
  task: `你是商品分类验证员。用 image 工具查看以下图片，判断分类是否正确。

图片路径: D:/projects/supplier_crawler/images/sfpanda/xxx.jpg
商品名称: CACEROLA CON ASA 20CM
AI建议分类: 厨房用品 > 炊具 > 汤锅/炖锅

请判断：
1. 图片中的商品是什么？
2. AI建议的分类是否正确？
3. 如果不正确，建议什么分类？

输出JSON: {"match": true/false, "description": "商品描述", "suggested": "正确分类或null"}`,
  model: "qclaw/pool-minimax-m3",
  mode: "run",
  taskName: "verify-batch-1-001"
})
```

### 方案B：modelroute_api（脚本方式）

直接调用 Gateway API，用多模态模型批量验证：

```python
import sys
sys.path.insert(0, r"C:\Users\Administrator\Desktop\modelroute_api")
from modelroute_api import call_model

prompt = f"""看这张商品图片，判断分类是否正确。
商品名称: {name}
AI建议分类: {new_category}

如果分类正确回复: {{"match": true}}
如果分类错误回复: {{"match": false, "suggested": "正确分类"}}
"""

# 调用多模态模型（需模型支持图片输入）
# 注意：modelroute_api.py 的 call_model 是纯文本接口
# 图片验证需要用 OpenClaw 的 image 工具或支持图片的 API
```

> **注意**：`modelroute_api.py` 当前是纯文本接口，不支持图片输入。图片验证需要通过 OpenClaw `image` 工具（方案A），或扩展 modelroute_api 支持图片。

## 执行流程伪代码

```python
import json, os
import pymysql

CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache"

def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # 加载现有分类标签列表
    category_list = load_categories_from_db()
    
    batch_num = 1
    while True:
        # 阶段1: AI分类 → 缓存
        products = fetch_batch(100)
        if not products:
            break
        
        assignments, new_cats = call_ai_classify(products, category_list)
        
        # 写缓存文件（不写数据库）
        cache = {
            "batch_id": batch_num,
            "total": len(assignments),
            "assignments": [
                {
                    "id": a["id"],
                    "new_category": a["category"],
                    # 附带商品信息用于后续验证
                    "name": p["name"],
                    "old_category": p["current_category"],
                    "image_local": p["image_local"],
                    "has_image": bool(p["image_local"]),
                }
                for a, p in zip(assignments, products)
            ],
            "new_categories": new_cats,
        }
        write_json(f"{CACHE_DIR}/batch_{batch_num}.json", cache)
        
        # 阶段2: 比对
        diff = compare_with_db(cache)
        write_json(f"{CACHE_DIR}/batch_{batch_num}_diff.json", diff)
        
        # 阶段3: 识图验证差异项
        for item in diff["items"]:
            if item["old_category"] != item["new_category"]:
                if item["has_image"]:
                    # 调用 image 工具验证
                    result = verify_by_image(item)
                    item["image_verified"] = result["match"]
                    item["image_result"] = result
                    if result["match"]:
                        item["final_category"] = item["new_category"]
                    else:
                        item["final_category"] = result.get("suggested") or item["old_category"]
                else:
                    # 无图，信任AI
                    item["final_category"] = item["new_category"]
            else:
                # 未变化，直接保留
                item["final_category"] = item["old_category"]
        
        # 更新diff文件
        write_json(f"{CACHE_DIR}/batch_{batch_num}_diff.json", diff)
        
        # 阶段4: 写入数据库
        for item in diff["items"]:
            if item["final_category"] and item["final_category"] != item["old_category"]:
                update_db(item["id"], item["final_category"])
        
        # 新分类加入列表
        for nc in new_cats:
            category_list.append(nc["category"])
        
        print(f"Batch {batch_num}: {len(assignments)}条, 差异{diff['summary']['changed']}条, 已写入")
        batch_num += 1
```

## 目录结构

```
D:\projects\supplier_crawler\classify_cache\
├── batch_1.json              # 第1批AI分类结果
├── batch_1_diff.json         # 第1批比对+验证结果
├── batch_2.json
├── batch_2_diff.json
├── ...
├── mismatch.log              # 识图验证不匹配记录
└── summary.json              # 全局统计
```
