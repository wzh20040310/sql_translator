"""
SQL翻译器基本使用示例，展示所有支持的功能
"""

from sql_translator import SQLExecutor, SQLResultDisplay
from sql_translator.core.executor import SQLExecutor

def main():
    # 创建执行器实例
    executor = SQLExecutor()
    display = SQLResultDisplay()
    
    print("=" * 50)
    print("SQL翻译器功能测试")
    print("=" * 50)
    
    # 测试注释功能
    print("\n1. 注释功能")
    sql = """
    -- 这是单行注释
    /* 这是多行注释
       跨越多行
       测试注释功能 */
    """
    print(sql)
    
    # 创建多个表
    print("\n2. 创建用户表")
    sql = """
    /* 创建一个存储用户信息的表 */
    CREATE TABLE users (
        id INT,          -- 用户ID
        name VARCHAR(50),  -- 用户名
        age INT,         -- 年龄
        email VARCHAR(100), -- 邮箱
        created_at VARCHAR(50)  -- 创建时间
    )
    """
    result = executor.execute_sql(sql)
    print(result)
    
    print("\n3. 创建订单表")
    sql = """
    -- 创建存储订单信息的表
    CREATE TABLE orders (
        order_id INT,     -- 订单ID
        user_id INT,      -- 关联的用户ID
        product VARCHAR(100),  -- 产品名称
        amount DECIMAL(10,2),  -- 金额
        order_date VARCHAR(50) -- 订单日期
    )
    """
    result = executor.execute_sql(sql)
    print(result)
    
    print("\n4. 创建产品表")
    sql = """
    CREATE TABLE products (
        product_id INT,
        product_name VARCHAR(100),
        price DECIMAL(10,2),
        stock INT
    )
    """
    result = executor.execute_sql(sql)
    print(result)
    
    # 插入用户数据
    print("\n5. 插入用户数据")
    insert_statements = [
        "INSERT INTO users VALUES (1, 'Zhang San', 25, 'zhangsan@example.com', '2022-01-01')",
        "INSERT INTO users VALUES (2, 'Li Si', 30, 'lisi@example.com', '2022-02-15')",
        "INSERT INTO users VALUES (3, 'Wang Wu', 35, 'wangwu@example.com', '2022-03-20')",
        "INSERT INTO users VALUES (4, 'Zhao Liu', 28, 'zhaoliu@example.com', '2022-04-10')",
        "INSERT INTO users VALUES (5, 'Sun Qi', 42, 'sunqi@example.com', '2022-05-05')"
    ]
    for sql in insert_statements:
        result = executor.execute_sql(sql)
        print(result)
    
    # 插入订单数据
    print("\n6. 插入订单数据")
    insert_statements = [
        "INSERT INTO orders VALUES (101, 1, 'Laptop', 5999.99, '2022-02-10')",
        "INSERT INTO orders VALUES (102, 2, 'Phone', 3999.99, '2022-03-15')",
        "INSERT INTO orders VALUES (103, 1, 'Tablet', 2999.99, '2022-04-20')",
        "INSERT INTO orders VALUES (104, 3, 'Monitor', 1999.99, '2022-05-25')",
        "INSERT INTO orders VALUES (105, 2, 'Keyboard', 299.99, '2022-06-30')"
    ]
    for sql in insert_statements:
        result = executor.execute_sql(sql)
        print(result)
    
    # 插入产品数据
    print("\n7. 插入产品数据")
    insert_statements = [
        "INSERT INTO products VALUES (1, 'Laptop', 5999.99, 100)",
        "INSERT INTO products VALUES (2, 'Phone', 3999.99, 200)",
        "INSERT INTO products VALUES (3, 'Tablet', 2999.99, 150)",
        "INSERT INTO products VALUES (4, 'Monitor', 1999.99, 80)",
        "INSERT INTO products VALUES (5, 'Keyboard', 299.99, 300)"
    ]
    for sql in insert_statements:
        result = executor.execute_sql(sql)
        print(result)
    
    # 基本查询
    print("\n8. 查询所有用户")
    result = executor.execute_sql("SELECT * FROM users;")
    # 获取表结构以提供表头
    table_structure = executor.get_table_structure("users")
    headers = list(table_structure.keys()) if table_structure else None
    print(display.format_table_data(result, headers))
    
    # 条件查询
    print("\n9. 查询年龄大于30的用户")
    result = executor.execute_sql("SELECT name, age, email FROM users WHERE age > 30;")
    # 为指定列提供表头
    headers = ["name", "age", "email"]
    print(display.format_table_data(result, headers))
    
    # # 更复杂的条件查询
    # print("\n10. 查询年龄在25到40之间的用户")
    # result = executor.execute_sql("SELECT * FROM users WHERE age >= 25 AND age <= 40;")
    # print(display.format_operation_result(result))
    
    # 查询订单表
    print("\n11. 查询金额大于2000的订单")
    result = executor.execute_sql("SELECT * FROM orders WHERE amount > 2000;")
    # 获取表结构以提供表头
    table_structure = executor.get_table_structure("orders")
    headers = list(table_structure.keys()) if table_structure else None
    print(display.format_table_data(result, headers))
    
    # 更新数据
    print("\n12. 更新用户年龄")
    result = executor.execute_sql("UPDATE users SET age = 36 WHERE name = 'Wang Wu';")
    print(result)
    
    # 查看更新后的结果
    print("\n13. 查看更新后的用户信息")
    result = executor.execute_sql("SELECT * FROM users WHERE id = 3;")
    headers = list(executor.get_table_structure("users").keys())
    print(display.format_table_data(result, headers))
    
    # 批量更新
    print("\n14. 批量更新产品价格")
    result = executor.execute_sql("UPDATE products SET price = 3999;")
    print(result)
    
    print("\n15. 查看更新后的产品价格")
    result = executor.execute_sql("SELECT * FROM products;")
    headers = list(executor.get_table_structure("products").keys())
    print(display.format_table_data(result, headers))
    
    # 添加新列
    print("\n16. 在用户表中添加电话号码列")
    result = executor.execute_sql("ALTER TABLE users ADD phone VARCHAR(20);")
    print(result)
    
    # 更新新列数据
    print("\n17. 更新用户电话号码")
    update_statements = [
        "UPDATE users SET phone = '1391234xxxx' WHERE id = 1;",
        "UPDATE users SET phone = '1382345xxxx' WHERE id = 2;",
        "UPDATE users SET phone = '1373456xxxx' WHERE id = 3;"
    ]
    for sql in update_statements:
        result = executor.execute_sql(sql)
        print(result)
    
    # 查看表结构变化
    print("\n18. 查看更新后的用户表数据")
    result = executor.execute_sql("SELECT * FROM users;")
    # 重新获取表结构以包含新添加的列
    headers = list(executor.get_table_structure("users").keys())
    print(display.format_table_data(result, headers))
    
    # 删除数据
    print("\n19. 删除年龄大于40的用户")
    result = executor.execute_sql("DELETE FROM users WHERE age > 40;")
    print(result)
    
    # 查看删除后的结果
    print("\n20. 查看删除后的用户数据")
    result = executor.execute_sql("SELECT * FROM users;")
    headers = list(executor.get_table_structure("users").keys())
    print(display.format_table_data(result, headers))
    
    # 批量删除
    print("\n21. 删除金额低于1000的订单")
    result = executor.execute_sql("DELETE FROM orders WHERE amount < 1000;")
    print(result)
    
    # 查看删除后的订单
    print("\n22. 查看剩余订单")
    result = executor.execute_sql("SELECT * FROM orders;")
    headers = list(executor.get_table_structure("orders").keys())
    print(display.format_table_data(result, headers))
    
    # 测试ORDER BY功能
    print("\n23. 按年龄排序(升序)")
    result = executor.execute_sql("SELECT * FROM users ORDER BY age;")
    headers = list(executor.get_table_structure("users").keys())
    print(display.format_table_data(result, headers))
    
    print("\n24. 按年龄排序(降序)")
    result = executor.execute_sql("SELECT * FROM users ORDER BY age DESC;")
    headers = list(executor.get_table_structure("users").keys())
    print(display.format_table_data(result, headers))
    
    print("\n25. 按用户名排序(升序)")
    result = executor.execute_sql("SELECT id, name, age FROM users ORDER BY name;")
    headers = ["id", "name", "age"]
    print(display.format_table_data(result, headers))
    
    print("\n26. 复合排序(先按年龄降序，再按ID升序)")
    result = executor.execute_sql("SELECT * FROM users ORDER BY age DESC, id;")
    headers = list(executor.get_table_structure("users").keys())
    print(display.format_table_data(result, headers))
    
    print("\n27. 带条件的排序(年龄大于25的用户按年龄排序)")
    result = executor.execute_sql("SELECT name, age FROM users WHERE age > 25 ORDER BY age;")
    headers = ["name", "age"]
    print(display.format_table_data(result, headers))
    
    print("\n28. 订单按金额排序(降序)")
    result = executor.execute_sql("SELECT * FROM orders ORDER BY amount DESC;")
    headers = list(executor.get_table_structure("orders").keys())
    print(display.format_table_data(result, headers))
    
    # 使用注释说明某些复杂操作
    print("\n29. 查看产品表")
    sql = """
    /* 按库存量排序，展示所有产品 */
    SELECT * FROM products ORDER BY stock DESC;
    """
    result = executor.execute_sql(sql)
    headers = list(executor.get_table_structure("products").keys())
    print(display.format_table_data(result, headers))
    
    # 显示所有表
    print("\n30. 显示所有表")
    result = executor.execute_sql("SHOW TABLES;")
    print(display.format_table_data(result, ["Table Name"]))
    
    # 批量执行测试
    print("\n31. 批量执行SQL语句")
    batch_sql = """
    -- 创建新表
    CREATE TABLE categories (id INT, name VARCHAR(50));
    
    -- 插入数据
    INSERT INTO categories VALUES (1, 'Electronics');
    INSERT INTO categories VALUES (2, 'Home Appliances');
    INSERT INTO categories VALUES (3, 'Accessories');
    INSERT INTO categories VALUES (4, 'Software');
    
    -- 查询数据(带排序)
    SELECT * FROM categories ORDER BY name;
    """
    results = executor.execute_batch(batch_sql)
    for i, result in enumerate(results):
        print(f"语句 {i+1} 结果:", end=" ")
        if i == 5 and isinstance(result, list) and result and isinstance(result[0], list):  # 如果是最后一条语句的结果（查询结果）
            headers = list(executor.get_table_structure("categories").keys())
            print("\n" + display.format_table_data(result, headers))
        else:
            print(result)
    
    # 查看新创建的表
    print("\n32. 查看categories表")
    result = executor.execute_sql("SELECT * FROM categories;")
    headers = list(executor.get_table_structure("categories").keys())
    print(display.format_table_data(result, headers))
    
    # 测试DROP TABLE
    print("\n33. 删除表测试")
    drop_statements = [
        "DROP TABLE categories;",
        "DROP TABLE users;",
        "DROP TABLE orders;",
        "DROP TABLE products;"
    ]
    for sql in drop_statements:
        result = executor.execute_sql(sql)
        print(result)
    
    print("\n34. 最终检查所有表")
    result = executor.execute_sql("SHOW TABLES;")
    print(display.format_table_data(result, ["Table Name"]))
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == '__main__':
    main() 