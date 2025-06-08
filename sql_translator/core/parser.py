class SQLParser:
    """SQL语句解析器，负责将SQL语句解析为中间表示"""
    
    def __init__(self):
        pass
    
    def remove_comments(self, sql):
        """移除SQL语句中的注释
        
        支持两种类型的注释:
        1. 单行注释: 以 -- 开头
        2. 多行注释: 以 /* 开始, 以 */ 结束
        """
        # 去除空白字符
        sql = sql.strip()
        
        # 用于存储处理后的SQL
        result = []
        i = 0
        in_string = False
        string_quote = None
        
        while i < len(sql):
            # 处理字符串字面量，避免误删字符串中的内容
            if sql[i] in ["'", '"'] and (i == 0 or sql[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_quote = sql[i]
                elif sql[i] == string_quote:
                    in_string = False
                result.append(sql[i])
                i += 1
                continue
            
            # 如果在字符串内，直接添加
            if in_string:
                result.append(sql[i])
                i += 1
                continue
            
            # 单行注释 --
            if i < len(sql) - 1 and sql[i:i+2] == '--':
                # 找到行尾
                newline_pos = sql.find('\n', i)
                if newline_pos == -1:  # 如果找不到换行符，说明注释一直到结尾
                    i = len(sql)
                else:
                    i = newline_pos + 1  # 跳过注释和换行符
                # 添加空格代替注释，保持SQL语句的格式
                result.append(' ')
                continue
            
            # 多行注释 /* */
            if i < len(sql) - 1 and sql[i:i+2] == '/*':
                # 找到注释结束
                end_comment = sql.find('*/', i+2)
                if end_comment == -1:  # 如果找不到结束标记，认为注释到文件末尾
                    i = len(sql)
                else:
                    i = end_comment + 2  # 跳过注释结束标记
                # 添加空格代替注释，保持SQL语句的格式
                result.append(' ')
                continue
            
            # 正常字符
            result.append(sql[i])
            i += 1
        
        return ''.join(result)
    
    def parse_sql(self, sql):
        """解析SQL语句，返回解析结果"""
        # 首先移除注释
        sql_no_comments = self.remove_comments(sql)
        
        # 转换为大写便于比较
        sql_upper = sql_no_comments.strip().upper()
        
        # 保存原始SQL(包含注释)用于显示
        original_sql = sql
        
        if sql_upper.startswith('CREATE TABLE'):
            return {'type': 'CREATE_TABLE', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('INSERT INTO'):
            return {'type': 'INSERT', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('DELETE FROM'):
            return {'type': 'DELETE', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('SELECT'):
            return {'type': 'SELECT', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('UPDATE'):
            return {'type': 'UPDATE', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('ALTER TABLE'):
            return {'type': 'ALTER_TABLE', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('DROP TABLE'):
            return {'type': 'DROP_TABLE', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('SHOW TABLES'):
            return {'type': 'SHOW_TABLES', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('JOIN'):
            return {'type': 'JOIN', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('GROUP BY'):
            return {'type': 'GROUP_BY', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('ORDER BY'):
            return {'type': 'ORDER_BY', 'content': sql_no_comments, 'original': original_sql}
        elif sql_upper.startswith('-- ') or sql_upper.startswith('/*'):
            # 纯注释，不执行任何操作
            return {'type': 'COMMENT', 'content': '', 'original': original_sql}
        else:
            return {'type': 'UNKNOWN', 'content': sql_no_comments, 'original': original_sql} 