from sql_translator.core.parser import SQLParser
from sql_translator.core.operations import (
    CreateTableOperation, InsertOperation, DeleteOperation,
    SelectOperation, UpdateOperation, AlterTableOperation,
    DropTableOperation, ShowTablesOperation
)

class SQLExecutor:
    """SQL执行器，负责执行SQL操作并返回结果"""
    
    def __init__(self):
        self.parser = SQLParser()
        self.tables = {}  # 存储表结构
        self.data = {}    # 存储表数据
        self.operations = {
            'CREATE_TABLE': CreateTableOperation(self.tables, self.data),
            'INSERT': InsertOperation(self.tables, self.data),
            'DELETE': DeleteOperation(self.tables, self.data),
            'SELECT': SelectOperation(self.tables, self.data),
            'UPDATE': UpdateOperation(self.tables, self.data),
            'ALTER_TABLE': AlterTableOperation(self.tables, self.data),
            'DROP_TABLE': DropTableOperation(self.tables, self.data),
            'SHOW_TABLES': ShowTablesOperation(self.tables, self.data)
        }
    
    def execute_sql(self, sql):
        """执行单条SQL语句"""
        # 处理SQL语句末尾的分号
        if sql.strip().endswith(';'):
            sql = sql.strip()[:-1]  # 去掉末尾的分号
            
        parsed = self.parser.parse_sql(sql)
        operation_type = parsed['type']
        
        if operation_type == 'COMMENT':
            # 对于纯注释语句，直接返回注释内容但不执行
            return f"注释: {parsed['original']}"
        elif operation_type in self.operations:
            return self.operations[operation_type].execute(parsed['content'])
        else:
            return f"不支持的SQL语句: {parsed['original']}"
    
    def execute_batch(self, sql_batch):
        """执行批量SQL语句"""
        results = []
        # 按分号分割SQL语句，并过滤掉空语句
        statements = []
        current_stmt = ""
        in_string = False
        string_quote = None
        
        # 更智能地分割SQL语句，考虑字符串中的分号和注释
        for i, char in enumerate(sql_batch):
            if char in ["'", '"'] and (i == 0 or sql_batch[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_quote = char
                elif char == string_quote:
                    in_string = False
                current_stmt += char
            elif char == ';' and not in_string:
                # 遇到分号时，添加当前语句（除非是空的）
                if current_stmt.strip():
                    statements.append(current_stmt.strip())
                current_stmt = ""
            else:
                current_stmt += char
        
        # 添加最后一个语句（如果不为空）
        if current_stmt.strip():
            statements.append(current_stmt.strip())
        
        for sql in statements:
            # 确保语句不为空
            if sql.strip():
                result = self.execute_sql(sql)
                results.append(result)
        
        return results
    
    def get_tables(self):
        """获取所有表名"""
        return list(self.tables.keys())
    
    def get_table_structure(self, table_name):
        """获取指定表的结构"""
        if table_name in self.tables:
            return self.tables[table_name]
        return None
    
    def get_table_data(self, table_name):
        """获取指定表的数据"""
        if table_name in self.data:
            return self.data[table_name]
        return None 