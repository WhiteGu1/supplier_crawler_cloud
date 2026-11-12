"""
crawler/pdf_parsers/__init__.py
兼容层：统一转发到顶级 pdf_parsers 模块
"""

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from pdf_parsers import list_parsers, get_parser, _load
