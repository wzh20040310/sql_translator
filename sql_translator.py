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
        # 首先找到表名
        table_name = sql.split('(')[0].split()[-1].strip()

        # 提取列定义部分
        columns_str = sql[sql.find('(') + 1:sql.rfind(')')]

        # 分割列定义，但要注意括号内的内容
        columns = []
        current_col = ""
        bracket_count = 0

        for char in columns_str:
            if char == '(':
                bracket_count += 1
                current_col += char
            elif char == ')':
                bracket_count -= 1
                current_col += char
            elif char == ',' and bracket_count == 0:
                columns.append(current_col.strip())
                current_col = ""
            else:
                current_col += char

        if current_col.strip():
            columns.append(current_col.strip())

        table_structure = {}
        for col in columns:
            col = col.strip()
            # 找到第一个空格的位置，用于分割列名和类型
            first_space = col.find(' ')
            if first_space != -1:
                col_name = col[:first_space].strip()
                col_type = col[first_space:].strip()
                table_structure[col_name] = col_type

        self.tables[table_name] = table_structure
        self.data[table_name] = []
        return f"创建表 {table_name} 成功"

    def parse_insert(self, sql):
        """解析INSERT语句"""
        parts = sql.split('VALUES')
        table_name = parts[0].split()[2].strip()
        # 先去除所有空格，再去除括号，最后分割
        values = parts[1].strip().strip('()').split(',')
        # 只去除空格，保留引号
        values = [v.strip() for v in values]

        if table_name not in self.data:
            return f"表 {table_name} 不存在"

        # 获取表结构
        table_structure = self.tables[table_name]
        col_types = list(table_structure.values())
        
        # 检查值的数量是否匹配列数
        if len(values) != len(col_types):
            return f"错误：值的数量({len(values)})与列数({len(col_types)})不匹配"

        # 检查每个值的类型
        for i, (value, type_str) in enumerate(zip(values, col_types)):
            # 检查是否带有引号
            has_quotes = value.startswith("'") and value.endswith("'")
            # 去除引号用于类型检查
            value_without_quotes = value.strip("'")
            
            if 'INT' in type_str.upper():
                if has_quotes:
                    return f"错误：第{i+1}列的值 '{value}' 不应该使用引号，因为它是INT类型"
                try:
                    int(value_without_quotes)
                except ValueError:
                    return f"错误：第{i+1}列的值 '{value}' 不是有效的整数"
            elif 'VARCHAR' in type_str.upper() or 'CHAR' in type_str.upper():
                if not has_quotes:
                    return f"错误：第{i+1}列的值 {value} 应该使用引号，因为它是字符串类型"
            elif 'DECIMAL' in type_str.upper() or 'FLOAT' in type_str.upper() or 'DOUBLE' in type_str.upper():
                if has_quotes:
                    return f"错误：第{i+1}列的值 '{value}' 不应该使用引号，因为它是数值类型"
                try:
                    float(value_without_quotes)
                except ValueError:
                    return f"错误：第{i+1}列的值 '{value}' 不是有效的数值"

        # 存储时去除引号
        values = [v.strip("'") for v in values]
        self.data[table_name].append(values)
        return f"向表 {table_name} 插入数据成功"

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
        col_types = list(self.tables[table_name].values())
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
            selected_types = []
            for col in selected_cols:
                idx = self.get_column_index(col_names, col)
                if idx != -1:
                    col_indices.append(idx)
                    selected_types.append(col_types[idx])
            result = [[row[i] for i in col_indices] for row in result]
            col_types = selected_types
        else:
            col_types = list(self.tables[table_name].values())

        # 根据列类型转换数据
        formatted_result = []
        for row in result:
            formatted_row = []
            for value, type_str in zip(row, col_types):
                if 'INT' in type_str.upper():
                    # 整数类型转换为int
                    formatted_row.append(int(value))
                elif 'DECIMAL' in type_str.upper() or 'FLOAT' in type_str.upper() or 'DOUBLE' in type_str.upper():
                    # 浮点数类型转换为float
                    formatted_row.append(float(value))
                else:
                    # 字符串类型保持原样
                    formatted_row.append(value)
            formatted_result.append(formatted_row)

        return formatted_result

    def parse_update(self, sql):
        """解析UPDATE语句"""
        parts = sql.split('SET')
        table_name = parts[0].split()[1].strip()

        if table_name not in self.data:
            return f"表 {table_name} 不存在"

        set_part = parts[1].split('WHERE')[0].strip()
        updates = {}
        for update in set_part.split(','):
            col, value = update.split('=')
            col = col.strip()
            value = value.strip().strip("'")
            updates[col] = value

        col_names = list(self.tables[table_name].keys())
        
        # 检查要更新的列是否存在
        for col in updates.keys():
            if col not in col_names:
                return f"更新失败：列 '{col}' 不存在于表 {table_name} 中"

        # 记录是否有行被更新
        rows_updated = 0

        if 'WHERE' in sql:
            condition = parts[1].split('WHERE')[1].strip()
            for i, row in enumerate(self.data[table_name]):
                if self.evaluate_condition(row, col_names, condition):
                    for col, value in updates.items():
                        col_index = self.get_column_index(col_names, col)
                        if col_index != -1:
                            self.data[table_name][i][col_index] = value
                    rows_updated += 1
        else:
            for i, row in enumerate(self.data[table_name]):
                for col, value in updates.items():
                    col_index = self.get_column_index(col_names, col)
                    if col_index != -1:
                        self.data[table_name][i][col_index] = value
                rows_updated += 1

        if rows_updated == 0:
            return f"更新失败：没有找到匹配的记录"
        return f"更新表 {table_name} 成功，更新了 {rows_updated} 行"

    def parse_alter_table(self, sql):
        """解析ALTER TABLE语句"""
        parts = sql.split()
        table_name = parts[2].strip()

        if table_name not in self.tables:
            return f"表 {table_name} 不存在"

        if 'ADD' in sql:
            col_def = ' '.join(parts[4:])
            col_name = col_def.split()[0]
            col_type = col_def.split()[1]
            self.tables[table_name][col_name] = col_type
            # 为现有数据添加新列，默认值为空字符串
            for row in self.data[table_name]:
                row.append('')
            return f"向表 {table_name} 添加列 {col_name} 成功"
        elif 'DROP' in sql:
            col_name = parts[4].strip()
            if col_name in self.tables[table_name]:
                col_index = self.get_column_index(list(self.tables[table_name].keys()), col_name)
                del self.tables[table_name][col_name]
                # 从现有数据中删除该列
                for row in self.data[table_name]:
                    del row[col_index]
                return f"从表 {table_name} 删除列 {col_name} 成功"
            return f"列 {col_name} 不存在"

    def parse_drop_table(self, sql):
        """解析DROP TABLE语句"""
        table_name = sql.split()[2].strip()
        if table_name in self.tables:
            del self.tables[table_name]
            del self.data[table_name]
            return f"删除表 {table_name} 成功"
        return f"表 {table_name} 不存在"

    def parse_show_tables(self, sql):
        """解析SHOW TABLES语句"""
        return list(self.tables.keys())

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
        elif sql.startswith('UPDATE'):
            return self.parse_update(sql)
        elif sql.startswith('ALTER TABLE'):
            return self.parse_alter_table(sql)
        elif sql.startswith('DROP TABLE'):
            return self.parse_drop_table(sql)
        elif sql.startswith('SHOW TABLES'):
            return self.parse_show_tables(sql)
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
    CREATE TABLE users (id INT, name VARCHAR(50), age INT, email VARCHAR(100))
    INSERT INTO users VALUES (1, 'John', 25, 'john@example.com')
    INSERT INTO users VALUES (2, 'Alice', 30, 'alice@example.com')
    INSERT INTO users VALUES (3, 'Bob', 35, 'bob@example.com')
    
    SELECT * FROM users
    SELECT name, age FROM users WHERE age > 25
    
    UPDATE users SET age = 40 WHERE name = 'Bob'
    UPDATE users SET email = 'new_email@example.com' WHERE id = 1
    SELECT * FROM users
    
    ALTER TABLE users ADD phone VARCHAR(20)
    ALTER TABLE users ADD address VARCHAR(200)
    SELECT * FROM users
    
    SHOW TABLES
    
    CREATE TABLE orders (order_id INT, user_id INT, amount DECIMAL(10,2))
    INSERT INTO orders VALUES (1, 1, 100.50)
    INSERT INTO orders VALUES (2, 2, 200.75)
    SHOW TABLES
    
    ALTER TABLE users DROP phone
    SELECT * FROM users
    
    DROP TABLE orders
    SHOW TABLES
    
    UPDATE nonexistent SET age = 30
    ALTER TABLE nonexistent ADD column INT
    DROP TABLE nonexistent
    '''

    # 将测试SQL语句分割成单独的语句
    statements = [stmt.strip() for stmt in test.split('\n') if stmt.strip()]
    
    # 逐条执行并立即输出结果
    for sql in statements:
        print(f"\n执行SQL: {sql}")
        result = translator.execute_sql(sql)
        print(f"结果: {result}")
