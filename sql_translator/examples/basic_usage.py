"""
SQL翻译器基本使用示例
"""

from sql_translator import SQLExecutor, SQLResultDisplay

def main():
    # 创建执行器实例
    executor = SQLExecutor()
    display = SQLResultDisplay()
    
    # 创建用户表
    print("\n1. 创建用户表")
    sql = """
    CREATE TABLE users (
        id INT,
        name VARCHAR(50),
        age INT,
        email VARCHAR(100)
    )
    """
    result = executor.execute_sql(sql)
    print(result)
    
    # 插入用户数据
    print("\n2. 插入用户数据")
    # 分别执行每条INSERT语句
    insert_statements = [
        "INSERT INTO users VALUES (1, 'John', 25, 'john@example.com')",
        "INSERT INTO users VALUES (2, 'Alice', 30, 'alice@example.com')",
        "INSERT INTO users VALUES (3, 'Bob', 35, 'bob@example.com')"
    ]
    for sql in insert_statements:
        result = executor.execute_sql(sql)
        print(result)
    
    # 查询所有用户
    print("\n3. 查询所有用户")
    result = executor.execute_sql("SELECT * FROM users")
    print(display.format_operation_result(result))
    
    # 查询年龄大于25的用户
    print("\n4. 查询年龄大于25的用户")
    result = executor.execute_sql("SELECT name, age FROM users WHERE age > 25")
    print(display.format_operation_result(result))
    
    # 更新用户年龄
    print("\n5. 更新用户年龄")
    result = executor.execute_sql("UPDATE users SET age = 40 WHERE name = 'Bob'")
    print(result)
    
    # 查看更新后的结果
    print("\n6. 查看更新后的结果")
    result = executor.execute_sql("SELECT * FROM users")
    print(display.format_operation_result(result))
    
    # 添加新列
    print("\n7. 添加电话号码列")
    result = executor.execute_sql("ALTER TABLE users ADD phone VARCHAR(20)")
    print(result)
    
    # 查看表结构
    print("\n8. 查看表结构")
    structure = executor.get_table_structure('users')
    print(display.format_table_structure(structure))
    
    # 删除用户
    print("\n9. 删除年龄大于30的用户")
    result = executor.execute_sql("DELETE FROM users WHERE age > 30")
    print(result)
    
    # 查看最终结果
    print("\n10. 查看最终结果")
    result = executor.execute_sql("SELECT * FROM users")
    print(display.format_operation_result(result))
    
    # 显示所有表
    print("\n11. 显示所有表")
    result = executor.execute_sql("SHOW TABLES")
    print(display.format_operation_result(result))
    
    # 删除表
    print("\n12. 删除用户表")
    result = executor.execute_sql("DROP TABLE users")
    print(result)

if __name__ == '__main__':
    main() 