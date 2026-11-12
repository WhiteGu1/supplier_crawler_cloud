# 修复 sfpanda 和 osa 爬虫

## 问题诊断

### sfpanda (ID=1)
- **根因**: 网站从 WooCommerce 迁移到 Jumpseller 平台，旧选择器完全失效
- **现状**: 静态 HTML 中有 56 个商品块，但选择器 `h3 a.single-product__more-info` 匹配不到
- **平台**: Jumpseller（`assets.jumpseller.com`）

### osa (ID=5)
- **根因**: `list_url` 设置为 `?mpage=300` 导致超大页面，Playwright 浏览器 OOM 崩溃
- **现状**: Cloudflare 429 拦截 + 内存溢出双重问题

---

## 修复方案

### 步骤 1: 更新 sfpanda 数据库配置

通过 API 更新 sfpanda (ID=1) 的 selectors：

```json
{
  "selectors": {
    "card_container": "article.product-block[data-product-id]",
    "product_name": "a.product-block__anchor",
    "price": "span.product-block__price",
    "image": "img.product-block__image",
    "pagination": "li.next a",
    "product_links": ""
  }
}
```

### 步骤 2: 在 spider.py 中添加 Jumpseller 平台提取方法

新增 `_extract_from_jumpseller(soup)` 方法，处理 Jumpseller 平台的特殊逻辑：
- 从 `a.product-block__anchor` 的 `title` 属性获取商品名称（去掉 "Ir a " 前缀）
- 从 `span.product-block__price` 获取价格文本（格式如 `$36.000`）
- 从 `img.product-block__image` 的 `src` 获取图片 URL
- 从 `article.product-block` 的 `data-product-id` 获取产品 ID
- 商品链接从 `a.product-block__anchor` 的 `href` 获取

在 `_extract_from_list_page` 方法之前优先调用此方法。

### 步骤 3: 更新 osa 数据库配置

将 osa (ID=5) 的 list_url 从：
`https://www.osadistribuidora.com.ar/productos/?mpage=300`
改为：
`https://www.osadistribuidora.com.ar/productos/`

### 步骤 4: Playwright 内存优化

在 `spider.py` 的 `crawl_js` 和 `_crawl_js_btn_pagination` 方法中，为 Playwright 启动参数增加内存优化：
- 添加 `--disable-gpu` 参数
- 添加 `--disable-extensions` 参数
- 添加 `--disable-background-networking` 参数
- 设置 `--js-flags="--max-old-space-size=512"` 限制 V8 堆内存

---

## 涉及文件

1. **spider.py** - 添加 `_extract_from_jumpseller()` 方法 + Playwright 内存优化
2. **数据库 suppliers 表** - 更新 sfpanda 和 osa 的配置（通过 API 调用）

## 验证

1. 启动服务器：`cd api && python main.py`
2. 触发 sfpanda 爬取：`curl -X POST http://localhost:8100/api/crawl/start/1`
3. 触发 osa 爬取：`curl -X POST http://localhost:8100/api/crawl/start/5`
4. 检查日志和商品入库数量
