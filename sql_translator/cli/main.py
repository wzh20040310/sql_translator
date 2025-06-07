import sys
import argparse
from sql_translator.core import SQLExecutor
from sql_translator.utils import SQLResultDisplay

def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(description='SQL翻译器命令行工具')
    parser.add_argument('-f', '--file', help='从文件读取SQL语句')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互模式')
    parser.add_argument('sql', nargs='?', help='SQL语句')
    return parser

def read_sql_from_file(file_path):
    """从文件读取SQL语句"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)

def interactive_mode():
    """交互模式"""
    executor = SQLExecutor()
    display = SQLResultDisplay()
    
    print("欢迎使用SQL翻译器！输入SQL语句执行，输入'exit'或'quit'退出。")
    print("支持的SQL语句类型：")
    print("1. CREATE TABLE")
    print("2. INSERT INTO")
    print("3. DELETE FROM")
    print("4. SELECT")
    print("5. UPDATE")
    print("6. ALTER TABLE")
    print("7. DROP TABLE")
    print("8. SHOW TABLES")
    print()
    
    while True:
        try:
            sql = input("sql> ").strip()
            
            if sql.lower() in ('exit', 'quit'):
                break
            
            if not sql:
                continue
                
            result = executor.execute_sql(sql)
            print("\n" + display.format_operation_result(result) + "\n")
            
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}\n")

def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    executor = SQLExecutor()
    display = SQLResultDisplay()
    
    if args.interactive:
        interactive_mode()
    elif args.file:
        sql = read_sql_from_file(args.file)
        results = executor.execute_batch(sql)
        for result in results:
            print(display.format_operation_result(result))
    elif args.sql:
        result = executor.execute_sql(args.sql)
        print(display.format_operation_result(result))
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 