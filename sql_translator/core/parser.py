class SQLParser:
    """SQL语句解析器，负责将SQL语句解析为中间表示"""
    
    def __init__(self):
        pass
    
    def parse_sql(self, sql):
        """解析SQL语句，返回解析结果"""
        sql = sql.strip().upper()
        
        if sql.startswith('CREATE TABLE'):
            return {'type': 'CREATE_TABLE', 'content': sql}
        elif sql.startswith('INSERT INTO'):
            return {'type': 'INSERT', 'content': sql}
        elif sql.startswith('DELETE FROM'):
            return {'type': 'DELETE', 'content': sql}
        elif sql.startswith('SELECT'):
            return {'type': 'SELECT', 'content': sql}
        elif sql.startswith('UPDATE'):
            return {'type': 'UPDATE', 'content': sql}
        elif sql.startswith('ALTER TABLE'):
            return {'type': 'ALTER_TABLE', 'content': sql}
        elif sql.startswith('DROP TABLE'):
            return {'type': 'DROP_TABLE', 'content': sql}
        elif sql.startswith('SHOW TABLES'):
            return {'type': 'SHOW_TABLES', 'content': sql}
        elif sql.startswith('JOIN'):
            return {'type': 'JOIN', 'content': sql}
        elif sql.startswith('GROUP BY'):
            return {'type': 'GROUP_BY', 'content': sql}
        elif sql.startswith('ORDER BY'):
            return {'type': 'ORDER_BY', 'content': sql}
        else:
            return {'type': 'UNKNOWN', 'content': sql} 