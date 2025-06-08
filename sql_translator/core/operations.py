class BaseOperation:
    """SQL操作的基类"""
    
    def __init__(self, tables, data):
        self.tables = tables
        self.data = data
    
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


class CreateTableOperation(BaseOperation):
    """CREATE TABLE操作实现"""
    
    def execute(self, sql):
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


class InsertOperation(BaseOperation):
    """INSERT操作实现"""
    
    def execute(self, sql):
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


class DeleteOperation(BaseOperation):
    """DELETE操作实现"""
    
    def execute(self, sql):
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


class SelectOperation(BaseOperation):
    """SELECT操作实现"""
    
    def execute(self, sql):
        """解析SELECT语句"""
        parts = sql.split('FROM')
        columns = parts[0].split()[1].strip()
        
        # 处理FROM子句，需要考虑可能存在的WHERE和ORDER BY
        from_part = parts[1]
        table_part = from_part.split('WHERE')[0] if 'WHERE' in from_part else (from_part.split('ORDER BY')[0] if 'ORDER BY' in from_part else from_part)
        table_name = table_part.strip()

        if table_name not in self.data:
            return f"表 {table_name} 不存在"

        col_names = list(self.tables[table_name].keys())
        col_types = list(self.tables[table_name].values())
        result = self.data[table_name].copy()  # 使用拷贝避免修改原始数据

        # 处理WHERE条件
        if 'WHERE' in from_part:
            where_part = from_part.split('WHERE')[1]
            condition = where_part.split('ORDER BY')[0].strip() if 'ORDER BY' in where_part else where_part.strip()
            result = [
                row for row in result
                if self.evaluate_condition(row, col_names, condition)
            ]

        # 处理列选择
        selected_col_indices = []
        selected_col_names = []
        selected_types = []
        
        if columns == '*':
            selected_col_indices = list(range(len(col_names)))
            selected_col_names = col_names
            selected_types = col_types
        else:
            selected_cols = [col.strip() for col in columns.split(',')]
            for col in selected_cols:
                idx = self.get_column_index(col_names, col)
                if idx != -1:
                    selected_col_indices.append(idx)
                    selected_col_names.append(col_names[idx])
                    selected_types.append(col_types[idx])
            
            result = [[row[i] for i in selected_col_indices] for row in result]
            col_names = selected_col_names
            col_types = selected_types

        # 处理ORDER BY子句
        if 'ORDER BY' in sql.upper():
            order_by_part = sql.upper().split('ORDER BY')[1].strip()
            order_cols = []
            desc_flags = []
            
            # 解析ORDER BY子句中的列和排序方向
            for col_spec in order_by_part.split(','):
                col_spec = col_spec.strip()
                if ' DESC' in col_spec:
                    col_name = col_spec.replace(' DESC', '').strip()
                    desc = True
                else:
                    col_name = col_spec.replace(' ASC', '').strip()  # ASC是默认的，可以省略
                    desc = False
                
                # 找到列在当前结果集中的索引
                if columns == '*':
                    col_index = self.get_column_index(col_names, col_name)
                else:
                    col_index = selected_col_names.index(col_name) if col_name in selected_col_names else -1
                
                if col_index != -1:
                    order_cols.append(col_index)
                    desc_flags.append(desc)
            
            # 如果有有效的排序列，执行排序
            if order_cols:
                # 多级排序，从最后一个指定的列开始排
                for i in range(len(order_cols) - 1, -1, -1):
                    col_idx = order_cols[i]
                    is_desc = desc_flags[i]
                    
                    # 确定数据类型以进行正确比较
                    if columns == '*':
                        col_type = col_types[col_idx]
                    else:
                        col_type = selected_types[col_idx]
                    
                    # 根据数据类型进行排序
                    # 数值类型需要转换为数值再比较，字符串类型直接比较
                    if 'INT' in col_type.upper() or 'DECIMAL' in col_type.upper() or 'FLOAT' in col_type.upper() or 'DOUBLE' in col_type.upper():
                        def get_numeric_value(value):
                            try:
                                return float(value)
                            except (ValueError, TypeError):
                                return 0  # 对于无法转换的值，返回0
                        
                        result.sort(key=lambda row: get_numeric_value(row[col_idx]), reverse=is_desc)
                    else:
                        # 字符串排序
                        result.sort(key=lambda row: str(row[col_idx]).lower(), reverse=is_desc)

        # 根据列类型转换数据
        formatted_result = []
        for row in result:
            formatted_row = []
            for i, value in enumerate(row):
                type_str = col_types[i]
                if 'INT' in type_str.upper():
                    # 整数类型转换为int
                    try:
                        formatted_row.append(int(value))
                    except (ValueError, TypeError):
                        formatted_row.append(value)  # 如果无法转换，保持原样
                elif 'DECIMAL' in type_str.upper() or 'FLOAT' in type_str.upper() or 'DOUBLE' in type_str.upper():
                    # 浮点数类型转换为float
                    try:
                        formatted_row.append(float(value))
                    except (ValueError, TypeError):
                        formatted_row.append(value)  # 如果无法转换，保持原样
                else:
                    # 字符串类型保持原样
                    formatted_row.append(value)
            formatted_result.append(formatted_row)

        return formatted_result


class UpdateOperation(BaseOperation):
    """UPDATE操作实现"""
    
    def execute(self, sql):
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


class AlterTableOperation(BaseOperation):
    """ALTER TABLE操作实现"""
    
    def execute(self, sql):
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


class DropTableOperation(BaseOperation):
    """DROP TABLE操作实现"""
    
    def execute(self, sql):
        """解析DROP TABLE语句"""
        table_name = sql.split()[2].strip()
        if table_name in self.tables:
            del self.tables[table_name]
            del self.data[table_name]
            return f"删除表 {table_name} 成功"
        return f"表 {table_name} 不存在"


class ShowTablesOperation(BaseOperation):
    """SHOW TABLES操作实现"""
    
    def execute(self, sql):
        """解析SHOW TABLES语句"""
        # 返回列表的列表格式，每个表名作为一个单独的行
        return [[table_name] for table_name in self.tables.keys()] 