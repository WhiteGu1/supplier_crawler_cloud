# 历史价格Bug修复记录

## 时间
2026-07-11 19:10

## 问题描述
用户反映历史价格功能有问题：更新商品时只会覆盖之前的价格。

## 根因
PDF导入功能（`api/main.py` 的 `/api/suppliers/{id}/import-pdf` 路由）中，**新增商品**的INSERT语句（原656行）缺少 `price_history` 写入。导致通过PDF导入的2333个商品没有任何价格历史记录。

对比：
- `db_manager.py` 的 `upsert_product()`：新商品INSERT后有写price_history ✅
- `api/main.py` 的Excel导入路由：新商品INSERT后有写price_history ✅  
- `api/main.py` 的PDF导入路由：新商品INSERT后**没有**写price_history ❌

## 修复内容
1. **代码修复** (`api/main.py`)：PDF导入的新商品INSERT后，添加 `INSERT INTO price_history` 写入初始价格记录。
2. **数据修复**：补写2333个缺失价格历史记录的商品，使用各自 `created_at` 作为 `recorded_at`。

## 修复后状态
- price_history: 26371条记录，覆盖全部21184个商品
- 所有导入路径（爬虫upsert、PDF导入、Excel导入）均正确写入price_history
