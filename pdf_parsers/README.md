# PDF 解析器插件模块 (`pdf_parsers/`)

本目录集中管理供应商 PDF 格式货单与商品目录的定制解析器。系统通过动态插件机制自动发现该目录下的所有解析器，并在前端导入窗口与后台 API 中提供选择。

---

## 目录结构

```text
pdf_parsers/
├── __init__.py         # 插件动态发现与加载入口（list_parsers, get_parser）
├── dsaza.py            # d'sazá 供应商目录解析器
├── gaston.py           # Gaston 供应商目录解析器（支持 CATALOGO_SP、GENERALES、ROTACION）
├── kandel.py           # by kandel 供应商目录解析器
├── kk.py               # KK 供应商目录解析器
├── lp.py               # LP 供应商目录解析器
├── najal.py            # Najal 供应商目录解析器
├── panda.py            # Panda 供应商目录解析器
├── docs/               # 解析器设计分析文档
│   └── kandel_parser_20260713.md
└── samples/            # 样本 PDF 货单文件
    ├── CATALOGO_2026_panda.pdf
    └── Nuevos_Ingresos_Julio.pdf
```

---

## 如何添加新的 PDF 解析器

在当前目录下创建一个新的 `.py` 文件，文件名即为解析器 ID（如 `my_supplier.py`，对应 ID 为 `my_supplier`）。

文件中需提供以下规范属性与函数：

```python
# -*- coding: utf-8 -*-

PARSER_NAME = "My Supplier 目录 (3列网格)"
PARSER_DESC = "适用于 My Supplier 供应商 PDF 货单，提取 SKU、品名、价格与图片"

def parse(pdf_path: str, images_dir: str, supplier_id: int) -> list[dict]:
    """
    解析指定路径的 PDF 文件并提取商品。
    
    参数:
        pdf_path: PDF 文件的绝对路径
        images_dir: 项目本地图片存储根目录 (如 images/)
        supplier_id: 供应商 ID (用于保存图片到子目录 images/{supplier}_{id}/)
        
    返回:
        商品字典列表，每个 dict 包含:
        {
            "sku": "ABC-123",       # 商品货号/SKU
            "name": "商品名称",      # 商品名称
            "price": 1250.00,       # 价格 (浮点数)
            "category": "厨具",     # 分类 (可选，若无填空字符串)
            "image": "/images/..."  # 相对图片访问路径或 None
        }
    """
    ...
```

系统启动时会自动扫描本目录，无需手动在后台注册。
