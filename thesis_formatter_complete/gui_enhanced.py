#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版GUI界面
包含论文信息输入框和更友好的用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from datetime import datetime
from .main_formatter import CompleteThesisFormatter

class EnhancedFormatterGUI:
    """增强版格式化工具GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("毕业论文格式化工具 v2.0")
        self.root.geometry("800x700")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 变量
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        
        # 论文信息变量
        self.thesis_info = {
            'title': tk.StringVar(value=''),
            'major': tk.StringVar(value=''),
            'class': tk.StringVar(value=''),
            'student_id': tk.StringVar(value=''),
            'name': tk.StringVar(value=''),
            'advisor': tk.StringVar(value=''),
            'date': tk.StringVar(value=datetime.now().strftime('%Y年%m月'))
        }
        
        # 格式化器
        self.formatter = CompleteThesisFormatter()
        
        # 创建界面
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建notebook（标签页）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 文件选择标签页
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text='文件选择')
        self._create_file_frame(file_frame)
        
        # 论文信息标签页
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text='论文信息')
        self._create_info_frame(info_frame)
        
        # 格式化选项标签页
        options_frame = ttk.Frame(notebook)
        notebook.add(options_frame, text='格式化选项')
        self._create_options_frame(options_frame)
        
        # 进度和日志标签页
        progress_frame = ttk.Frame(notebook)
        notebook.add(progress_frame, text='处理进度')
        self._create_progress_frame(progress_frame)
        
        # 底部按钮
        self._create_bottom_buttons()
    
    def _create_file_frame(self, parent):
        """创建文件选择界面"""
        # 标题
        title_label = ttk.Label(parent, text="选择要格式化的Word文档", 
                               font=('微软雅黑', 14, 'bold'))
        title_label.pack(pady=20)
        
        # 输入文件
        input_frame = ttk.LabelFrame(parent, text="输入文件", padding=20)
        input_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(input_frame, text="选择文件:").grid(row=0, column=0, sticky='w', padx=5)
        ttk.Entry(input_frame, textvariable=self.input_file, width=50).grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="浏览...", 
                  command=self._browse_input).grid(row=0, column=2, padx=5)
        
        # 输出文件
        output_frame = ttk.LabelFrame(parent, text="输出文件", padding=20)
        output_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(output_frame, text="保存为:").grid(row=0, column=0, sticky='w', padx=5)
        ttk.Entry(output_frame, textvariable=self.output_file, width=50).grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(output_frame, text="浏览...", 
                  command=self._browse_output).grid(row=0, column=2, padx=5)
        
        # 提示信息
        tip_frame = ttk.Frame(parent)
        tip_frame.pack(fill='x', padx=20, pady=20)
        
        tip_text = """使用提示：
1. 选择需要格式化的Word文档（.docx格式）
2. 指定输出文件的保存位置
3. 切换到"论文信息"标签页填写相关信息
4. 点击"开始格式化"按钮进行处理"""
        
        tip_label = ttk.Label(tip_frame, text=tip_text, justify='left',
                             background='#f0f0f0', padding=10)
        tip_label.pack(fill='x')
    
    def _create_info_frame(self, parent):
        """创建论文信息输入界面"""
        # 标题
        title_label = ttk.Label(parent, text="填写论文基本信息", 
                               font=('微软雅黑', 14, 'bold'))
        title_label.pack(pady=20)
        
        # 信息输入框架
        info_frame = ttk.LabelFrame(parent, text="论文信息（用于生成封面）", padding=20)
        info_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 创建输入字段
        fields = [
            ('论文题目:', 'title', 60),
            ('专业:', 'major', 30),
            ('班级:', 'class', 30),
            ('学号:', 'student_id', 30),
            ('姓名:', 'name', 30),
            ('指导教师:', 'advisor', 30),
            ('日期:', 'date', 30)
        ]
        
        for i, (label, key, width) in enumerate(fields):
            ttk.Label(info_frame, text=label).grid(row=i, column=0, 
                                                   sticky='e', padx=10, pady=8)
            
            if key == 'title':
                # 论文题目使用Text组件支持多行
                text_widget = tk.Text(info_frame, height=2, width=width, wrap='word')
                text_widget.grid(row=i, column=1, padx=10, pady=8, sticky='ew')
                
                # 绑定变量
                def on_title_change(event=None):
                    self.thesis_info['title'].set(text_widget.get('1.0', 'end-1c'))
                
                text_widget.bind('<KeyRelease>', on_title_change)
                text_widget.insert('1.0', self.thesis_info['title'].get())
            else:
                entry = ttk.Entry(info_frame, textvariable=self.thesis_info[key], 
                                 width=width)
                entry.grid(row=i, column=1, padx=10, pady=8, sticky='w')
        
        # 配置列权重
        info_frame.columnconfigure(1, weight=1)
        
        # 按钮框架
        button_frame = ttk.Frame(info_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="使用默认值", 
                  command=self._use_default_info).pack(side='left', padx=5)
        ttk.Button(button_frame, text="清空所有", 
                  command=self._clear_info).pack(side='left', padx=5)
        ttk.Button(button_frame, text="保存配置", 
                  command=self._save_config).pack(side='left', padx=5)
        ttk.Button(button_frame, text="加载配置", 
                  command=self._load_config).pack(side='left', padx=5)
    
    def _create_options_frame(self, parent):
        """创建格式化选项界面"""
        # 标题
        title_label = ttk.Label(parent, text="格式化选项设置", 
                               font=('微软雅黑', 14, 'bold'))
        title_label.pack(pady=20)
        
        # 选项框架
        options_frame = ttk.LabelFrame(parent, text="选择要执行的格式化操作", padding=20)
        options_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 格式化选项
        self.format_options = {
            'cover': tk.BooleanVar(value=True),
            'commitment': tk.BooleanVar(value=True),
            'page_number': tk.BooleanVar(value=True),
            'keywords': tk.BooleanVar(value=True),
            'figures_tables': tk.BooleanVar(value=True),
            'footnotes': tk.BooleanVar(value=True),
            'math': tk.BooleanVar(value=True),
            'toc': tk.BooleanVar(value=True),
            'acknowledgment': tk.BooleanVar(value=True),
            'appendix': tk.BooleanVar(value=True),
            'reorganize': tk.BooleanVar(value=True),
            'basic': tk.BooleanVar(value=True)
        }
        
        option_labels = {
            'cover': '生成封面',
            'commitment': '生成诚信承诺书',
            'page_number': '设置页码（罗马/阿拉伯）',
            'keywords': '格式化关键词',
            'figures_tables': '图表自动编号',
            'footnotes': '格式化脚注',
            'math': '格式化数学公式',
            'toc': '生成/更新目录',
            'acknowledgment': '格式化致谢',
            'appendix': '格式化附录',
            'reorganize': '重组文档结构',
            'basic': '基础格式化（字体、段落等）'
        }
        
        # 创建选项复选框
        for i, (key, label) in enumerate(option_labels.items()):
            row = i // 2
            col = i % 2
            cb = ttk.Checkbutton(options_frame, text=label, 
                               variable=self.format_options[key])
            cb.grid(row=row, column=col, sticky='w', padx=20, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(options_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="全选", 
                  command=self._select_all_options).pack(side='left', padx=5)
        ttk.Button(button_frame, text="全不选", 
                  command=self._deselect_all_options).pack(side='left', padx=5)
        ttk.Button(button_frame, text="推荐设置", 
                  command=self._recommended_options).pack(side='left', padx=5)
    
    def _create_progress_frame(self, parent):
        """创建进度显示界面"""
        # 标题
        title_label = ttk.Label(parent, text="格式化进度", 
                               font=('微软雅黑', 14, 'bold'))
        title_label.pack(pady=20)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var,
                                          maximum=100, length=400)
        self.progress_bar.pack(pady=10)
        
        # 进度文本
        self.progress_label = ttk.Label(parent, text="准备就绪")
        self.progress_label.pack(pady=5)
        
        # 日志显示
        log_frame = ttk.LabelFrame(parent, text="处理日志", padding=10)
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill='both', expand=True)
    
    def _create_bottom_buttons(self):
        """创建底部按钮"""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(side='bottom', pady=10)
        
        self.format_button = ttk.Button(button_frame, text="开始格式化", 
                                       command=self._start_format,
                                       style='Accent.TButton')
        self.format_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="退出", 
                  command=self.root.quit).pack(side='left', padx=5)
    
    def _browse_input(self):
        """浏览输入文件"""
        filename = filedialog.askopenfilename(
            title="选择Word文档",
            filetypes=[("Word文档", "*.docx"), ("所有文件", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # 自动生成输出文件名
            base_name = os.path.splitext(filename)[0]
            self.output_file.set(f"{base_name}_formatted.docx")
    
    def _browse_output(self):
        """浏览输出文件"""
        filename = filedialog.asksaveasfilename(
            title="保存格式化后的文档",
            defaultextension=".docx",
            filetypes=[("Word文档", "*.docx"), ("所有文件", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def _use_default_info(self):
        """使用默认论文信息"""
        defaults = {
            'title': '基于深度学习的图像识别研究',
            'major': '计算机科学与技术',
            'class': '计科1901',
            'student_id': '20190001',
            'name': '张三',
            'advisor': '李教授',
            'date': '2024年6月'
        }
        
        for key, value in defaults.items():
            self.thesis_info[key].set(value)
    
    def _clear_info(self):
        """清空所有信息"""
        for key in self.thesis_info:
            if key != 'date':
                self.thesis_info[key].set('')
    
    def _save_config(self):
        """保存配置到文件"""
        config = {key: var.get() for key, var in self.thesis_info.items()}
        
        filename = filedialog.asksaveasfilename(
            title="保存配置",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for key, value in config.items():
                        f.write(f"{key}={value}\n")
                messagebox.showinfo("成功", "配置已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")
    
    def _load_config(self):
        """从文件加载配置"""
        filename = filedialog.askopenfilename(
            title="加载配置",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key in self.thesis_info:
                                self.thesis_info[key].set(value)
                messagebox.showinfo("成功", "配置已加载")
            except Exception as e:
                messagebox.showerror("错误", f"加载失败：{str(e)}")
    
    def _select_all_options(self):
        """全选所有选项"""
        for var in self.format_options.values():
            var.set(True)
    
    def _deselect_all_options(self):
        """取消所有选项"""
        for var in self.format_options.values():
            var.set(False)
    
    def _recommended_options(self):
        """设置推荐选项"""
        # 推荐的选项配置
        recommended = {
            'cover': True,
            'commitment': True,
            'page_number': True,
            'keywords': True,
            'figures_tables': True,
            'footnotes': True,
            'math': True,
            'toc': True,
            'acknowledgment': True,
            'appendix': True,
            'reorganize': True,
            'basic': True
        }
        
        for key, value in recommended.items():
            self.format_options[key].set(value)
    
    def _log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        self.root.update()
    
    def _update_progress(self, value, message):
        """更新进度"""
        self.progress_var.set(value)
        self.progress_label.config(text=message)
        self._log(message)
    
    def _start_format(self):
        """开始格式化"""
        # 验证输入
        if not self.input_file.get():
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        if not self.output_file.get():
            messagebox.showerror("错误", "请指定输出文件")
            return
        
        # 收集论文信息
        thesis_info = {key: var.get() for key, var in self.thesis_info.items()}
        
        # 收集格式化选项
        options = {key: var.get() for key, var in self.format_options.items()}
        
        # 禁用按钮
        self.format_button.config(state='disabled')
        
        # 在新线程中执行格式化
        thread = threading.Thread(
            target=self._format_thread,
            args=(self.input_file.get(), self.output_file.get(), 
                  thesis_info, options)
        )
        thread.start()
    
    def _format_thread(self, input_file, output_file, thesis_info, options):
        """格式化线程"""
        try:
            self._update_progress(0, "开始格式化...")
            
            # 设置格式化选项
            self.formatter.format_options = options
            
            # 执行格式化
            self.formatter.format_document(
                input_file,
                output_file,
                thesis_info,
                self._update_progress
            )
            
            self._update_progress(100, "格式化完成！")
            
            # 显示成功消息
            self.root.after(0, lambda: messagebox.showinfo(
                "成功", 
                f"文档格式化完成！\n输出文件：{output_file}"
            ))
            
        except Exception as e:
            self._update_progress(0, f"格式化失败：{str(e)}")
            self.root.after(0, lambda: messagebox.showerror(
                "错误", 
                f"格式化失败：{str(e)}"
            ))
        
        finally:
            # 重新启用按钮
            self.root.after(0, lambda: self.format_button.config(state='normal'))
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    # 测试GUI
    app = EnhancedFormatterGUI()
    app.run()