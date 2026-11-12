"""
PDF 解析器插件系统

每个解析器是一个独立的 Python 模块，放置在此目录下。
文件名即为解析器 ID（例如 gaston.py -> parser_id="gaston"）。

每个解析器模块需实现：
    PARSER_NAME: str        # 解析器名称，如 "gaston — Gaston 目录 (SKU/Código/ROTACION 网格)"
    PARSER_DESC: str        # 解析器功能描述
    def parse(pdf_path, images_dir, supplier_id) -> list[dict]:
        # 返回商品数据列表，每个 dict 包含：
        # {sku, name, price, category, image}
        # image 为 "/images/xxx.jpg" 或 None
"""

import os
import importlib.util

_PARSERS_DIR = os.path.dirname(__file__)


def list_parsers() -> list[dict]:
    """列出所有可用解析器"""
    parsers = []
    for fname in sorted(os.listdir(_PARSERS_DIR)):
        if fname.startswith('_') or not fname.endswith('.py'):
            continue
        parser_id = fname[:-3]
        try:
            mod = _load(parser_id)
            parsers.append({
                "id": parser_id,
                "name": getattr(mod, 'PARSER_NAME', parser_id),
                "desc": getattr(mod, 'PARSER_DESC', ''),
            })
        except Exception as e:
            parsers.append({"id": parser_id, "name": parser_id, "desc": f"加载失败: {e}"})
    return parsers


def get_parser(parser_id: str):
    """获取解析器模块，若不存在返回 None"""
    try:
        return _load(parser_id)
    except Exception:
        return None


def _load(parser_id: str):
    path = os.path.join(_PARSERS_DIR, f"{parser_id}.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"解析器不存在: {parser_id}")
    spec = importlib.util.spec_from_file_location(parser_id, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
