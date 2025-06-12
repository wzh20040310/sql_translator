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
                col, value = condition.split(op, 1)  # 只分割第一个
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

        # 处理带表名的列（table.column）
        if '.' in col:
            table_name, col_name = col.split('.', 1)
            # 在多表查询中，需要特殊处理
            col_index = self.get_column_index(col_names, col_name)
        else:
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
                    return f"错误：第{i + 1}列的值 '{value}' 不应该使用引号，因为它是INT类型"
                try:
                    int(value_without_quotes)
                except ValueError:
                    return f"错误：第{i + 1}列的值 '{value}' 不是有效的整数"
            elif 'VARCHAR' in type_str.upper() or 'CHAR' in type_str.upper():
                if not has_quotes:
                    return f"错误：第{i + 1}列的值 {value} 应该使用引号，因为它是字符串类型"
            elif 'DECIMAL' in type_str.upper() or 'FLOAT' in type_str.upper() or 'DOUBLE' in type_str.upper():
                if has_quotes:
                    return f"错误：第{i + 1}列的值 '{value}' 不应该使用引号，因为它是数值类型"
                try:
                    float(value_without_quotes)
                except ValueError:
                    return f"错误：第{i + 1}列的值 '{value}' 不是有效的数值"

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
        sql = sql.strip()

        # 使用更精确的方式分割SQL语句
        parts = self.split_sql_parts(sql)

        # 解析SELECT子句
        select_part = parts.get('SELECT', '')
        columns = select_part.strip()

        # 解析FROM子句
        from_part = parts.get('FROM', '')
        if not from_part:
            return "错误：缺少FROM子句"

        # 解析WHERE子句
        where_part = parts.get('WHERE', '')

        # 解析ORDER BY子句
        order_by_part = parts.get('ORDER BY', '')

        # 解析表和JOIN
        tables, join_conditions = self.parse_from_clause(from_part)

        # 检查所有表是否存在
        for table in tables:
            if table not in self.data:
                return f"表 {table} 不存在"

        # 获取所有表的列名和类型
        all_col_names = {}
        all_col_types = {}
        combined_col_names = []
        combined_col_types = []

        for table in tables:
            table_cols = list(self.tables[table].keys())
            table_types = list(self.tables[table].values())
            all_col_names[table] = table_cols
            all_col_types[table] = table_types
            combined_col_names.extend(table_cols)
            combined_col_types.extend(table_types)

        # 执行JOIN操作
        if len(tables) == 1:
            # 单表查询
            result = self.data[tables[0]].copy()
        else:
            # 多表JOIN
            result = self.execute_joins(tables, join_conditions, all_col_names)

        # 处理WHERE条件
        if where_part:
            result = [
                row for row in result
                if self.evaluate_condition(row, combined_col_names, where_part)
            ]

        # 处理列选择
        if columns == '*':
            selected_result = result
            selected_col_names = combined_col_names
            selected_col_types = combined_col_types
        else:
            selected_result, selected_col_names, selected_col_types = self.select_columns(
                result, columns, tables, all_col_names, all_col_types
            )

        # 处理ORDER BY
        if order_by_part:
            selected_result = self.apply_order_by(
                selected_result, order_by_part, selected_col_names, selected_col_types
            )

        # 格式化结果
        formatted_result = self.format_result(selected_result, selected_col_types)

        return formatted_result

    def split_sql_parts(self, sql):
        """将SQL语句分割为各个子句"""
        parts = {}
        keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'HAVING']

        sql_upper = sql.upper()
        positions = {}

        # 找到所有关键字的位置
        for keyword in keywords:
            pos = sql_upper.find(keyword)
            if pos != -1:
                positions[keyword] = pos

        # 按位置排序
        sorted_positions = sorted(positions.items(), key=lambda x: x[1])

        # 提取各部分
        for i, (keyword, pos) in enumerate(sorted_positions):
            start = pos + len(keyword)
            if i + 1 < len(sorted_positions):
                end = sorted_positions[i + 1][1]
            else:
                end = len(sql)

            parts[keyword] = sql[start:end].strip()

        return parts

    def parse_from_clause(self, from_clause):
        """解析FROM子句，提取表和JOIN条件"""
        tables = []
        join_conditions = []

        # 简单的JOIN解析
        parts = from_clause.split()
        i = 0

        while i < len(parts):
            if parts[i].upper() not in ['JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'ON']:
                # 这是一个表名
                tables.append(parts[i])
            elif parts[i].upper() == 'JOIN':
                # 下一个应该是表名
                if i + 1 < len(parts):
                    tables.append(parts[i + 1])
                    i += 1
            elif parts[i].upper() == 'ON':
                # 收集ON条件
                condition_parts = []
                i += 1
                while i < len(parts) and parts[i].upper() not in ['JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL']:
                    condition_parts.append(parts[i])
                    i += 1
                join_conditions.append(' '.join(condition_parts))
                i -= 1  # 回退一步，因为外层循环会增加
            i += 1

        return tables, join_conditions

    def execute_joins(self, tables, join_conditions, all_col_names):
        """执行JOIN操作"""
        result = self.data[tables[0]].copy()

        for i, table in enumerate(tables[1:], 1):
            new_result = []
            for row1 in result:
                for row2 in self.data[table]:
                    # 检查JOIN条件
                    if i - 1 < len(join_conditions):
                        condition = join_conditions[i - 1]
                        if self.evaluate_join_condition(row1, row2, tables[:i], [table], condition, all_col_names):
                            new_result.append(row1 + row2)
                    else:
                        # 没有JOIN条件，执行笛卡尔积
                        new_result.append(row1 + row2)
            result = new_result

        return result

    def evaluate_join_condition(self, row1, row2, tables1, tables2, condition, all_col_names):
        """评估JOIN条件"""
        # 解析JOIN条件（例如：table1.column = table2.column）
        parts = condition.split('=')
        if len(parts) != 2:
            return False

        col1_spec = parts[0].strip()
        col2_spec = parts[1].strip()

        # 解析列规格（table.column）
        table1_name, col1_name = self.parse_column_spec(col1_spec, tables1)
        table2_name, col2_name = self.parse_column_spec(col2_spec, tables2)

        if not table1_name or not table2_name:
            return False

        # 获取列索引
        idx1 = self.get_column_index(all_col_names[table1_name], col1_name)
        idx2 = self.get_column_index(all_col_names[table2_name], col2_name)

        if idx1 == -1 or idx2 == -1:
            return False

        # 计算在合并行中的实际索引
        offset1 = sum(len(all_col_names[t]) for t in tables1 if t != table1_name)
        actual_idx1 = offset1 + idx1

        # row2的索引就是idx2
        actual_idx2 = idx2

        # 比较值
        return row1[actual_idx1] == row2[actual_idx2]

    def parse_column_spec(self, col_spec, available_tables):
        """解析列规格，返回表名和列名"""
        if '.' in col_spec:
            table_name, col_name = col_spec.split('.', 1)
            if table_name in available_tables:
                return table_name, col_name
        else:
            # 没有指定表名，在可用表中查找
            for table in available_tables:
                if col_spec in self.tables[table]:
                    return table, col_spec

        return None, None

    def select_columns(self, result, columns, tables, all_col_names, all_col_types):
        """选择指定的列"""
        selected_col_indices = []
        selected_col_names = []
        selected_col_types = []

        selected_cols = [col.strip() for col in columns.split(',')]

        for col in selected_cols:
            if '.' in col:
                # 带表名的列
                table_name, col_name = col.split('.', 1)
                if table_name in tables:
                    idx = self.get_column_index(all_col_names[table_name], col_name)
                    if idx != -1:
                        # 计算在合并结果中的索引
                        table_idx = tables.index(table_name)
                        offset = sum(len(all_col_names[t]) for t in tables[:table_idx])
                        selected_col_indices.append(offset + idx)
                        selected_col_names.append(col)
                        selected_col_types.append(all_col_types[table_name][idx])
            else:
                # 不带表名的列
                found = False
                for table in tables:
                    idx = self.get_column_index(all_col_names[table], col)
                    if idx != -1:
                        table_idx = tables.index(table)
                        offset = sum(len(all_col_names[t]) for t in tables[:table_idx])
                        selected_col_indices.append(offset + idx)
                        selected_col_names.append(col)
                        selected_col_types.append(all_col_types[table][idx])
                        found = True
                        break
                if not found:
                    return [], [], [f"列 {col} 不存在"]

        # 选择指定的列
        selected_result = [[row[i] for i in selected_col_indices] for row in result]

        return selected_result, selected_col_names, selected_col_types

    def apply_order_by(self, result, order_by_part, col_names, col_types):
        """应用ORDER BY排序"""
        order_specs = []

        # 解析ORDER BY子句
        for col_spec in order_by_part.split(','):
            col_spec = col_spec.strip()
            if ' DESC' in col_spec.upper():
                col_name = col_spec.upper().replace(' DESC', '').strip()
                desc = True
            else:
                col_name = col_spec.upper().replace(' ASC', '').strip()
                desc = False

            # 找到列索引
            col_idx = self.get_column_index(col_names, col_name)
            if col_idx != -1:
                order_specs.append((col_idx, desc))

        # 执行排序
        if order_specs:
            for col_idx, is_desc in reversed(order_specs):
                col_type = col_types[col_idx] if col_idx < len(col_types) else ''

                if col_type and ('INT' in col_type.upper() or 'DECIMAL' in col_type.upper() or
                                 'FLOAT' in col_type.upper() or 'DOUBLE' in col_type.upper()):
                    def get_numeric_value(value):
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return 0

                    result.sort(key=lambda row: get_numeric_value(row[col_idx]), reverse=is_desc)
                else:
                    result.sort(key=lambda row: str(row[col_idx]).lower(), reverse=is_desc)

        return result

    def format_result(self, result, col_types):
        """格式化结果，根据列类型转换数据"""
        formatted_result = []

        for row in result:
            formatted_row = []
            for i, value in enumerate(row):
                if i < len(col_types):
                    type_str = col_types[i]
                    if 'INT' in type_str.upper():
                        try:
                            formatted_row.append(int(value))
                        except (ValueError, TypeError):
                            formatted_row.append(value)
                    elif 'DECIMAL' in type_str.upper() or 'FLOAT' in type_str.upper() or 'DOUBLE' in type_str.upper():
                        try:
                            formatted_row.append(float(value))
                        except (ValueError, TypeError):
                            formatted_row.append(value)
                    else:
                        formatted_row.append(value)
                else:
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
            col, value = update.split('=', 1)  # 只分割第一个=
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
                    if col_index < len(row):
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