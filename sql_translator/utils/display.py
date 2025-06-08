from typing import List, Any, Dict, Optional
from prettytable import PrettyTable

class SQLResultDisplay:
    """SQL结果显示工具类"""
    
    @staticmethod
    def format_table_data(data: List[List[Any]], headers: List[str] = None) -> str:
        """格式化表格数据"""
        if not data:
            return "空表"
            
        table = PrettyTable()
        
        # 确保每行数据都有相同的长度
        if headers:
            # 使用提供的表头
            table.field_names = headers
            
            # 检查每行数据是否匹配表头数量，如果不匹配则进行调整
            for i in range(len(data)):
                row = data[i]
                # 如果行数据短于表头，添加空字符串补齐
                if len(row) < len(headers):
                    data[i] = row + [''] * (len(headers) - len(row))
                # 如果行数据长于表头，截断多余的数据
                elif len(row) > len(headers):
                    data[i] = row[:len(headers)]
        else:
            # 如果没有提供表头，使用第一行数据的长度确定列数
            max_cols = max([len(row) for row in data]) if data else 0
            # 使用列索引作为表头
            table.field_names = [f"Column_{i}" for i in range(max_cols)]
            
            # 统一每行数据的长度
            for i in range(len(data)):
                row = data[i]
                if len(row) < max_cols:
                    data[i] = row + [''] * (max_cols - len(row))
        
        # 添加数据行
        for row in data:
            table.add_row(row)
            
        return str(table)
    
    @staticmethod
    def format_table_structure(structure: Optional[Dict[str, str]]) -> str:
        """格式化表结构"""
        if structure is None:
            return "表不存在或无法获取表结构"
            
        table = PrettyTable()
        table.field_names = ["Column Name", "Data Type"]
        
        for col_name, col_type in structure.items():
            table.add_row([col_name, col_type])
            
        return str(table)
    
    @staticmethod
    def format_tables_list(tables: List[str]) -> str:
        """格式化表名列表"""
        if not tables:
            return "数据库中没有表"
            
        table = PrettyTable()
        table.field_names = ["Table Name"]
        
        for table_name in tables:
            if isinstance(table_name, str):
                table.add_row([table_name])
            else:
                # 处理非字符串类的表名
                table.add_row([str(table_name)])
            
        return str(table)
    
    @staticmethod
    def format_operation_result(result: Any) -> str:
        """格式化操作结果"""
        if result is None:
            return "操作未返回结果"
            
        if isinstance(result, list):
            if not result:
                return "操作成功，但没有返回数据"
            if isinstance(result[0], list):
                # 结果是表格数据
                return SQLResultDisplay.format_table_data(result)
            else:
                # 结果是表名列表
                return SQLResultDisplay.format_tables_list(result)
        elif isinstance(result, dict):
            # 结果是表结构
            return SQLResultDisplay.format_table_structure(result)
        else:
            # 结果是普通消息
            return str(result) 