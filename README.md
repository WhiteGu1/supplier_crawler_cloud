# 供应商爬虫管理系统

通用网站爬虫管理平台，支持可视化配置供应商、定时爬取商品数据、价格历史追踪。

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. 创建 MySQL 数据库

```sql
CREATE DATABASE supplier_crawler DEFAULT CHARSET=utf8mb4;
```

### 3. 配置数据库密码

**方式A：直接修改 api/main.py 第144行**
```python
password="your_password",
```

**方式B：设置环境变量（推荐）**
```bash
# 复制模板
copy .env.example .env

# 编辑 .env 填入密码
DB_PASSWORD=your_mysql_password
```

### 4. 启动系统

```bash
cd api
python main.py
```

浏览器访问：http://localhost:8100

---

## 添加供应商（以 sfpanda.com.ar 为例）

在 **供应商管理 → 添加供应商** 中填写：

| 字段 | 示例值 |
|------|--------|
| 供应商名称 | SFPanda |
| 网站根地址 | https://sfpanda.com.ar |
| 商品列表页 | https://sfpanda.com.ar/tienda |
| 商品链接选择器 | `a.single-product__more-info` |
| 商品名称选择器 | `h1.product_title` |
| 价格选择器 | `p.price .woocommerce-Price-amount` |
| 图片选择器 | `div.woocommerce-product-gallery img` |
| 翻页选择器 | `a.next.page-numbers` |

> **如何找选择器**：浏览器打开目标页面 → F12 → 点击元素 → 右键 Copy → Copy selector

---

## 项目结构
 
```
supplier_crawler/
├── api/
│   └── main.py              # FastAPI 后端（端口 8100）
├── crawler/
│   ├── spider.py            # 爬虫核心（静态+JS渲染）
│   ├── scheduler.py         # 定时任务调度
│   └── pdf_parsers/         # PDF解析器兼容导入层
├── pdf_parsers/             # PDF 解析器插件模块（独立定制各类PDF货单）
│   ├── __init__.py          # 动态插件发现与加载入口
│   ├── gaston.py, ...       # 各供应商专属解析器
│   ├── docs/                # 解析器分析与设计文档
│   └── samples/             # 样本货单 PDF 文件
├── database/
│   └── db_manager.py        # MySQL 管理（连接池+CRUD+缺失阈值保护）
├── frontend/
│   └── dashboard.html       # 可视化管理面板
├── images/                  # 爬取与 PDF 提取的商品图片（按供应商分目录）
├── scripts/                 # 批次分类与系统维护脚本归档
├── plans/                   # 开发规划与体系方案文档
├── crawler.log              # 运行日志（自动创建）
├── .env.example             # 环境变量模板
├── requirements.txt
└── README.md
```

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/dashboard | 仪表盘统计 |
| GET | /api/suppliers | 供应商列表 |
| POST | /api/suppliers | 添加供应商 |
| PUT | /api/suppliers/{id} | 更新供应商 |
| DELETE | /api/suppliers/{id} | 删除供应商 |
| POST | /api/crawl/start/{id} | 启动爬虫 |
| POST | /api/crawl/stop/{id} | 停止爬虫 |
| GET | /api/crawl/status | 运行状态 |
| GET | /api/crawl-logs | 爬取日志 |
| GET | /api/products | 商品列表（支持搜索/筛选/分页） |
| GET | /api/products/categories | 分类列表 |
| GET | /api/products/{id}/price-history | 价格历史 |
| DELETE | /api/products/{id} | 删除商品 |
| POST | /api/products/delete-batch | 批量删除 |

---

## 常见问题

**Q: 爬取后商品数为0？**
A: 检查 CSS 选择器是否正确。建议先用浏览器 F12 验证选择器。

**Q: 需要 JS 渲染的网站如何处理？**
A: 勾选"需要 JavaScript 渲染"，需要提前运行 `python -m playwright install chromium`。

**Q: 如何设置自动定时爬取？**
A: 在供应商配置中填写 Cron 表达式，例如 `0 2 * * *` 表示每天凌晨2点。
