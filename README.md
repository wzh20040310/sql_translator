# SQL翻译器

一个将SQL语句转换为Python数组操作的工具，支持基本的SQL操作。

## 功能特点

- 支持基本的SQL操作：
  - CREATE TABLE：创建表
  - INSERT INTO：插入数据
  - DELETE FROM：删除数据
  - SELECT：查询数据
  - UPDATE：更新数据
  - ALTER TABLE：修改表结构
  - DROP TABLE：删除表
  - SHOW TABLES：显示所有表

- 提供美观的命令行界面
- 支持交互模式和批处理模式
- 支持从文件读取SQL语句
- 使用PrettyTable美化输出结果

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/sql_translator.git
cd sql_translator
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行工具

1. 交互模式：
```bash
python -m sql_translator.cli.main -i
```

2. 执行单条SQL语句：
```bash
python -m sql_translator.cli.main "SELECT * FROM users"
```

3. 从文件执行SQL语句：
```bash
python -m sql_translator.cli.main -f queries.sql
```

### 作为Python包使用

```python
from sql_translator import SQLExecutor, SQLResultDisplay

# 创建执行器实例
executor = SQLExecutor()

# 执行SQL语句
result = executor.execute_sql("CREATE TABLE users (id INT, name VARCHAR(50))")
print(result)

# 插入数据
result = executor.execute_sql("INSERT INTO users VALUES (1, 'John')")
print(result)

# 查询数据
result = executor.execute_sql("SELECT * FROM users")
print(SQLResultDisplay.format_operation_result(result))
```

## 示例

### 创建表
```sql
CREATE TABLE users (
    id INT,
    name VARCHAR(50),
    age INT,
    email VARCHAR(100)
)
```

### 插入数据
```sql
INSERT INTO users VALUES (1, 'John', 25, 'john@example.com')
INSERT INTO users VALUES (2, 'Alice', 30, 'alice@example.com')
```

### 查询数据
```sql
SELECT * FROM users
SELECT name, age FROM users WHERE age > 25
```

### 更新数据
```sql
UPDATE users SET age = 40 WHERE name = 'John'
```

### 修改表结构
```sql
ALTER TABLE users ADD phone VARCHAR(20)
```

### 删除数据
```sql
DELETE FROM users WHERE age > 30
```

### 删除表
```sql
DROP TABLE users
```

## 项目结构

```
sql_translator/
├── core/                 # 核心功能模块
│   ├── __init__.py
│   ├── parser.py        # SQL解析器
│   ├── executor.py      # SQL执行器
│   └── operations.py    # SQL操作实现
├── utils/               # 工具模块
│   ├── __init__.py
│   └── display.py      # 结果显示工具
├── cli/                 # 命令行界面
│   ├── __init__.py
│   └── main.py         # 命令行入口
├── tests/              # 测试用例
├── examples/           # 示例代码
├── __init__.py
├── requirements.txt    # 项目依赖
└── README.md          # 项目说明
```


