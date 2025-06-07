"""
SQL翻译器
将SQL语句转换为Python数组操作的工具
"""

from sql_translator.core import SQLExecutor, SQLParser
from sql_translator.utils import SQLResultDisplay

__version__ = '1.0.0'
__all__ = ['SQLExecutor', 'SQLParser', 'SQLResultDisplay'] 