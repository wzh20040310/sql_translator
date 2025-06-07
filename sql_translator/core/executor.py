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
        parsed = self.parser.parse_sql(sql)
        operation_type = parsed['type']
        
        if operation_type in self.operations:
            return self.operations[operation_type].execute(parsed['content'])
        else:
            return "不支持的SQL语句"
    
    def execute_batch(self, sql_batch):
        """执行批量SQL语句"""
        results = []
        statements = [stmt.strip() for stmt in sql_batch.split(';') if stmt.strip()]
        
        for sql in statements:
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