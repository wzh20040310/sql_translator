class SQLTranslator:
    def __init__(self):
        self.tables = {}  # 存储表结构
        self.data = {}  # 存储表数据

    def parse_condition(self, condition):
        """解析WHERE条件"""
        operators = ['=', '>', '<', '>=', '<=', '!=']
        for op in operators:
            if op in condition:
                col, value = condition.split(op)
                col = col.strip()
                value = value.strip().strip("'")
                return col, op, value
        return None, None, None

    def get_column_index(self, col_names, target_col):
        """获取列索引，不区分大小写"""
        target_col = target_col.upper()
        for i, col in enumerate(col_names):
            if col.upper() == target_col:
                return i
        return -1

    def evaluate_condition(self, row, col_names, condition):
        """评估条件是否满足"""
        if not condition:
            return True
            
        col, op, value = self.parse_condition(condition)
        if not col or not op:
            return True
            
        col_index = self.get_column_index(col_names, col)
        if col_index == -1:
            return True
            
        row_value = row[col_index]
        
        # 尝试将值转换为数字进行比较
        try:
            row_value = float(row_value)
            value = float(value)
        except ValueError:
            pass
            
        if op == '=':
            return row_value == value
        elif op == '>':
            return row_value > value
        elif op == '<':
            return row_value < value
        elif op == '>=':
            return row_value >= value
        elif op == '<=':
            return row_value <= value
        elif op == '!=':
            return row_value != value
        return True

    def parse_create_table(self, sql):
        """解析CREATE TABLE语句"""
        parts = sql.split('(')
        table_name = parts[0].split()[-1].strip()
        columns = parts[1].rstrip(')').split(',')

        table_structure = {}
        for col in columns:
            col = col.strip()
            col_parts = col.split()
            col_name = col_parts[0]
            col_type = col_parts[1]
            table_structure[col_name] = col_type

        self.tables[table_name] = table_structure
        self.data[table_name] = []
        return f"创建表 {table_name} 成功"

    def parse_insert(self, sql):
        """解析INSERT语句"""
        parts = sql.split('VALUES')
        table_name = parts[0].split()[2].strip()
        values = parts[1].strip('()').split(',')
        values = [v.strip().strip("'") for v in values]

        if table_name in self.data:
            self.data[table_name].append(values)
            return f"向表 {table_name} 插入数据成功"
        return f"表 {table_name} 不存在"

    def parse_delete(self, sql):
        """解析DELETE语句"""
        parts = sql.split('WHERE')
        table_name = parts[0].split()[2].strip()

        if table_name not in self.data:
            return f"表 {table_name} 不存在"

        if 'WHERE' in sql:
            condition = parts[1].strip()
            col_names = list(self.tables[table_name].keys())
            # 过滤掉不满足条件的数据
            self.data[table_name] = [
                row for row in self.data[table_name]
                if not self.evaluate_condition(row, col_names, condition)
            ]
            return f"从表 {table_name} 删除数据成功"
        else:
            self.data[table_name] = []
            return f"清空表 {table_name} 成功"

    def parse_select(self, sql):
        """解析SELECT语句"""
        parts = sql.split('FROM')
        columns = parts[0].split()[1].strip()
        table_info = parts[1].split('WHERE')
        table_name = table_info[0].strip()

        if table_name not in self.data:
            return f"表 {table_name} 不存在"

        col_names = list(self.tables[table_name].keys())
        result = self.data[table_name]

        if 'WHERE' in sql:
            condition = table_info[1].strip()
            result = [
                row for row in result
                if self.evaluate_condition(row, col_names, condition)
            ]

        if columns != '*':
            selected_cols = [col.strip() for col in columns.split(',')]
            col_indices = []
            for col in selected_cols:
                idx = self.get_column_index(col_names, col)
                if idx != -1:
                    col_indices.append(idx)
            result = [[row[i] for i in col_indices] for row in result]

        return result

    def execute_sql(self, sql):
        """执行单条SQL语句"""
        sql = sql.strip().upper()
        if sql.startswith('CREATE TABLE'):
            return self.parse_create_table(sql)
        elif sql.startswith('INSERT INTO'):
            return self.parse_insert(sql)
        elif sql.startswith('DELETE FROM'):
            return self.parse_delete(sql)
        elif sql.startswith('SELECT'):
            return self.parse_select(sql)
        else:
            return "不支持的SQL语句"

    def execute_batch(self, sql_batch):
        """执行批量SQL语句"""
        results = []
        statements = [stmt.strip() for stmt in sql_batch.split('\n') if stmt.strip()]

        for sql in statements:
            result = self.execute_sql(sql)
            results.append(result)

        return results

# 使用示例
if __name__ == "__main__":
    translator = SQLTranslator()

    test = '''
    CREATE TABLE users (id INT, name VARCHAR(50), age INT)
    INSERT INTO users VALUES (1, 'John', 25)
    INSERT INTO users VALUES (2, 'Alice', 30)
    INSERT INTO users VALUES (3, 'Bob', 35)
    SELECT * FROM users WHERE age > 25
    DELETE FROM users WHERE id = 1
    SELECT name, age FROM users
    '''

    results = translator.execute_batch(test)
    for result in results:
        print(result)