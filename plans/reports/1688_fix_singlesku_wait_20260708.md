# 单SKU商品被跳过问题 - 修复记录

## 时间
2026-07-08 19:31

## 问题描述
单SKU商品（如 offer/761961127073.html）在爬取时被跳过，无法入库。

## 根因分析
通过用户下载的真实HTML文件分析发现：

1. **旧等待条件 `indexOf('subject')` 过于宽松**
   - "subject" 这个词在验证码拦截页面、CSS类名、meta标签中都可能出现
   - 爬虫在页面跳转到验证码拦截页时就通过了等待条件
   - 此时拿到的HTML不包含商品JSON数据，`_RE_SUBJECT` 正则匹配不到 `"subject":"xxx"` 格式
   - `_extract_detail` 返回空列表 `[]`，商品被跳过

2. **单SKU页面没有 `skuProps` 字段**
   - 单SKU商品的HTML中只有 `"subject":"xxx"` 和 `"offerMinPrice":"xxx"`，没有 `skuProps`/`skuMap`
   - 旧条件 `indexOf('skuProps') > -1 || indexOf('subject') > -1` 中，`skuProps` 分支永远不会满足
   - 实际靠 `subject` 分支通过，但因为过于宽松而提前通过

## 验证证据
用真实下载的HTML（2.8MB）测试：
- `_RE_SUBJECT` 正则匹配成功：`"subject":"洗衣机置物架厕所马桶储物架滚筒波轮落地浴室上方收纳洗衣机架子"`
- `_RE_MIN_PRICE` 正则匹配成功：`"offerMinPrice":"300.00"`
- `_RE_IMAGE_LIST` 正则匹配成功
- `_extract_detail()` 返回1条完整记录（name/price/image_url均正确）
- `skuProps` 在HTML中不存在（单SKU预期行为）

验证码页面HTML测试：
- 旧条件 `indexOf('subject')`: **会通过**（meta标签含"subject"）
- 新条件 `/skuProps|"subject"\s*:\s*"/`: **不会通过**

## 修复内容
文件：`D:\projects\supplier_crawler\crawler\alibaba1688_spider.py`

两处等待条件（工厂页L421 + 旺铺页L619）：
```python
# 旧（有bug）：
"() => document.documentElement.innerHTML.indexOf('skuProps') > -1 || document.documentElement.innerHTML.indexOf('subject') > -1"

# 新（已修复）：
r"""() => /skuProps|"subject"\s*:\s*"/.test(document.documentElement.innerHTML)"""
```

新条件用JS正则 `/skuProps|"subject"\s*:\s*"/` 测试：
- 多SKU页面：匹配 `skuProps` → 通过
- 单SKU页面：匹配 `"subject":"` → 通过（只有JSON数据渲染后才匹配）
- 验证码/加载中页面：两者都不匹配 → 继续等待

## 结论
- `_extract_detail` 逻辑本身正确，单SKU能正确提取
- 问题完全在等待条件，已修复
- Python语法验证通过（`ast.parse` OK）
