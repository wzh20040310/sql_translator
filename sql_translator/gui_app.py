import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
from prettytable import PrettyTable

# 添加项目根目录到路径中，以便能够正确导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sql_translator.core.executor import SQLExecutor

class SQLTranslatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL翻译器")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 设置主题颜色
        self.bg_color = "#f5f5f5"
        self.text_bg = "#ffffff"
        self.button_color = "#4a86e8"
        self.result_bg = "#e8f0fe"
        
        self.root.configure(bg=self.bg_color)
        
        # 初始化SQL执行器
        self.executor = SQLExecutor()
        
        # 创建并设置框架
        self.create_widgets()
        
        # 默认插入示例SQL
        self.insert_examples()

    def create_widgets(self):
        # 顶部框架 - 标题
        top_frame = tk.Frame(self.root, bg=self.bg_color)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = tk.Label(top_frame, text="SQL翻译器可视化界面", font=("Arial", 16, "bold"), bg=self.bg_color)
        title_label.pack(pady=10)
        
        # 中间框架 - 输入区域
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        input_label = tk.Label(input_frame, text="SQL语句:", font=("Arial", 12), bg=self.bg_color)
        input_label.pack(anchor="w")
        
        # 创建SQL输入区域
        self.sql_input = scrolledtext.ScrolledText(input_frame, height=8, font=("Courier New", 12))
        self.sql_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.execute_button = tk.Button(button_frame, text="执行", font=("Arial", 12), 
                                 command=self.execute_sql, bg=self.button_color, fg="white", 
                                 width=10, relief=tk.RAISED)
        self.execute_button.pack(side=tk.LEFT, padx=5)
        
        self.execute_batch_button = tk.Button(button_frame, text="执行多条", font=("Arial", 12),
                                   command=self.execute_batch, bg="#4CAF50", fg="white",
                                   width=10, relief=tk.RAISED)
        self.execute_batch_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(button_frame, text="清空", font=("Arial", 12), 
                               command=self.clear_fields, bg="#e0e0e0", 
                               width=10, relief=tk.RAISED)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 表格选择框架
        tables_frame = tk.Frame(button_frame, bg=self.bg_color)
        tables_frame.pack(side=tk.RIGHT, padx=5)
        
        tables_label = tk.Label(tables_frame, text="现有表:", bg=self.bg_color)
        tables_label.pack(side=tk.LEFT)
        
        self.tables_combobox = ttk.Combobox(tables_frame, width=20)
        self.tables_combobox.pack(side=tk.LEFT, padx=5)
        self.tables_combobox.bind("<<ComboboxSelected>>", self.on_table_selected)
        
        self.refresh_button = tk.Button(tables_frame, text="刷新表", command=self.refresh_tables)
        self.refresh_button.pack(side=tk.LEFT)
        
        # 结果框架
        result_frame = tk.Frame(self.root, bg=self.bg_color)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        result_label = tk.Label(result_frame, text="执行结果:", font=("Arial", 12), bg=self.bg_color)
        result_label.pack(anchor="w")
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=12, font=("Courier New", 12), bg=self.result_bg)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def insert_examples(self):
        # 插入一些示例SQL
        examples = [
            "/* SQL翻译器示例 */",
            "",
            "-- 创建表示例:",
            "CREATE TABLE users (id INT, name VARCHAR(50), age INT, email VARCHAR(100));",
            "",
            "-- 插入数据示例:",
            "INSERT INTO users VALUES (1, 'Zhang San', 25, 'zhangsan@example.com');",
            "",
            "-- 查询数据示例:",
            "SELECT * FROM users WHERE age > 20;",
        ]
        self.sql_input.insert(tk.INSERT, '\n'.join(examples))

    def execute_sql(self):
        """执行单个SQL语句"""
        self.status_var.set("执行中...")
        self.root.update()
        
        sql = self.sql_input.get(1.0, tk.END).strip()
        
        if not sql:
            messagebox.showinfo("提示", "请输入SQL语句")
            self.status_var.set("就绪")
            return
        
        try:
            # 执行SQL并获取结果
            result = self.executor.execute_sql(sql)
            
            # 清空结果区域
            self.result_text.delete(1.0, tk.END)
            
            # 显示结果
            self.display_result(result, sql)
            
            # 更新表格列表
            self.refresh_tables()
            self.status_var.set("执行完成")
            
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.INSERT, f"错误: {str(e)}")
            self.status_var.set("执行出错")

    def execute_batch(self):
        """执行多条SQL语句"""
        self.status_var.set("批量执行中...")
        self.root.update()
        
        sql_batch = self.sql_input.get(1.0, tk.END).strip()
        
        if not sql_batch:
            messagebox.showinfo("提示", "请输入SQL语句")
            self.status_var.set("就绪")
            return
        
        try:
            # 执行批量SQL并获取结果
            results = self.executor.execute_batch(sql_batch)
            
            # 清空结果区域
            self.result_text.delete(1.0, tk.END)
            
            # 显示所有结果
            for i, result in enumerate(results):
                if i > 0:
                    self.result_text.insert(tk.INSERT, "\n\n" + "-" * 50 + "\n\n")
                
                if isinstance(result, str) and result.startswith("注释:"):
                    # 注释结果用蓝色显示
                    self.result_text.insert(tk.INSERT, result)
                    self.highlight_comment(result)
                else:
                    # 其他结果
                    self.result_text.insert(tk.INSERT, str(result))
            
            # 更新表格列表
            self.refresh_tables()
            self.status_var.set(f"执行完成 ({len(results)}条语句)")
            
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.INSERT, f"错误: {str(e)}")
            self.status_var.set("执行出错")
    
    def display_result(self, result, sql):
        """显示单条SQL的执行结果"""
        if isinstance(result, str) and result.startswith("注释:"):
            # 注释结果用蓝色显示
            self.result_text.insert(tk.INSERT, result)
            self.highlight_comment(result)
        elif isinstance(result, list) and result and isinstance(result[0], list):
            # 结果是表格数据
            table_name = None
            sql_upper = sql.upper()
            if "FROM" in sql_upper:
                words = sql_upper.split()
                from_index = words.index("FROM")
                if from_index + 1 < len(words):
                    table_name = words[from_index + 1].strip().rstrip(';')
            
            if table_name:
                table_structure = self.executor.get_table_structure(table_name)
                if table_structure:
                    # 创建PrettyTable实例
                    pt = PrettyTable()
                    pt.field_names = list(table_structure.keys())
                    
                    for row in result:
                        pt.add_row(row)
                    
                    self.result_text.insert(tk.INSERT, str(pt))
                else:
                    self.result_text.insert(tk.INSERT, str(result))
            else:
                self.result_text.insert(tk.INSERT, str(result))
        else:
            # 结果是文本
            self.result_text.insert(tk.INSERT, str(result))
    
    def highlight_comment(self, comment_text):
        """对注释文本进行高亮显示"""
        self.result_text.tag_configure("comment", foreground="blue")
        
        # 找到注释文本的起始和结束位置
        start = "1.0"
        while True:
            pos = self.result_text.search("注释:", start, tk.END)
            if not pos:
                break
            
            end = self.result_text.index(f"{pos} lineend")
            self.result_text.tag_add("comment", pos, end)
            start = end
    
    def clear_fields(self):
        self.sql_input.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("就绪")
    
    def refresh_tables(self):
        tables = self.executor.get_tables()
        self.tables_combobox['values'] = tables
    
    def on_table_selected(self, event):
        selected_table = self.tables_combobox.get()
        if selected_table:
            # 在SQL输入框生成查询当前表的SQL
            self.sql_input.delete(1.0, tk.END)
            self.sql_input.insert(tk.INSERT, f"SELECT * FROM {selected_table};")
            
            # 自动执行查询
            self.execute_sql()

def main():
    root = tk.Tk()
    app = SQLTranslatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 