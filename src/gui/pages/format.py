import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional, Any

from src.models.format_fixer import FormatFixer
from src.utils.file_handler import FileHandler
from src.utils.logger import setup_logger
from src.gui.components.scrolled_text import ScrolledText
from src.gui.components.progress_bar import ProgressBar
from src.gui.components.tooltip import ToolTip

logger = setup_logger(__name__)

class FormatFixer(ttk.Frame):
    """格式修改页面"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.file_handler = FileHandler()
        self.format_fixer = FormatFixer()
        
        # 文件路径
        self.source_file = None
        self.template_file = None
        
        # 创建界面
        self.create_widgets()
        logger.info("初始化格式修改页面")
        
    def create_widgets(self):
        """创建页面组件"""
        # 主页面分为上中下三部分
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill='x', padx=10, pady=5)
        
        self.middle_frame = ttk.Frame(self)
        self.middle_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(fill='x', padx=10, pady=5)
        
        # 顶部控制区
        self.create_top_controls()
        
        # 中间文件区
        self.create_file_area()
        
        # 底部按钮区
        self.create_bottom_controls()
        
    def create_top_controls(self):
        """创建顶部控制区"""
        # 标题
        ttk.Label(self.top_frame, text="文档格式修改", style="Title.TLabel").pack(anchor='w', pady=5)
        
        # 说明
        desc = ttk.Label(self.top_frame, 
                        text="上传需要修改的文件和格式模板文件，系统将自动将源文件调整为模板文件的格式。",
                        wraplength=600)
        desc.pack(anchor='w', pady=5)
        
    def create_file_area(self):
        """创建文件区域"""
        # 源文件区域
        source_frame = ttk.LabelFrame(self.middle_frame, text="源文件（需要修改格式的文件）")
        source_frame.pack(fill='x', pady=10)
        
        source_inner = ttk.Frame(source_frame)
        source_inner.pack(fill='x', padx=10, pady=10)
        
        self.source_path_var = tk.StringVar()
        ttk.Entry(source_inner, textvariable=self.source_path_var, width=60, state='readonly').pack(side='left', fill='x', expand=True)
        ttk.Button(source_inner, text="选择文件", command=self.select_source_file).pack(side='right', padx=5)
        
        # 源文件预览（仅在选择文件后显示）
        self.source_preview_frame = ttk.LabelFrame(self.middle_frame, text="源文件预览")
        
        self.source_preview = ScrolledText(self.source_preview_frame, height=10)
        self.source_preview.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 模板文件区域
        template_frame = ttk.LabelFrame(self.middle_frame, text="格式模板文件")
        template_frame.pack(fill='x', pady=10)
        
        template_inner = ttk.Frame(template_frame)
        template_inner.pack(fill='x', padx=10, pady=10)
        
        self.template_path_var = tk.StringVar()
        ttk.Entry(template_inner, textvariable=self.template_path_var, width=60, state='readonly').pack(side='left', fill='x', expand=True)
        ttk.Button(template_inner, text="选择文件", command=self.select_template_file).pack(side='right', padx=5)
        
        # 模板文件预览（仅在选择文件后显示）
        self.template_preview_frame = ttk.LabelFrame(self.middle_frame, text="模板文件预览")
        
        self.template_preview = ScrolledText(self.template_preview_frame, height=10)
        self.template_preview.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 格式调整选项
        options_frame = ttk.LabelFrame(self.middle_frame, text="格式调整选项")
        options_frame.pack(fill='x', pady=10)
        
        options_inner = ttk.Frame(options_frame)
        options_inner.pack(fill='x', padx=10, pady=10)
        
        # 选项
        self.adjust_fonts_var = tk.BooleanVar(value=True)
        self.adjust_spacing_var = tk.BooleanVar(value=True)
        self.adjust_margins_var = tk.BooleanVar(value=True)
        self.adjust_headings_var = tk.BooleanVar(value=True)
        self.keep_content_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_inner, text="调整字体", variable=self.adjust_fonts_var).grid(row=0, column=0, padx=5, sticky='w')
        ttk.Checkbutton(options_inner, text="调整行距和段落间距", variable=self.adjust_spacing_var).grid(row=0, column=1, padx=5, sticky='w')
        ttk.Checkbutton(options_inner, text="调整页边距", variable=self.adjust_margins_var).grid(row=1, column=0, padx=5, sticky='w')
        ttk.Checkbutton(options_inner, text="调整标题样式", variable=self.adjust_headings_var).grid(row=1, column=1, padx=5, sticky='w')
        ttk.Checkbutton(options_inner, text="保留原文内容", variable=self.keep_content_var).grid(row=2, column=0, padx=5, sticky='w')
        
    def create_bottom_controls(self):
        """创建底部控制区"""
        # 状态信息
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(self.bottom_frame, textvariable=self.status_var)
        status_label.pack(side='left', padx=5)
        
        # 进度条
        self.progress = ProgressBar(self.bottom_frame, width=200)
        self.progress.pack(side='left', padx=10)
        
        # 操作按钮
        buttons_frame = ttk.Frame(self.bottom_frame)
        buttons_frame.pack(side='right')
        
        self.fix_btn = ttk.Button(buttons_frame, text="开始格式调整", 
                                 command=self.start_format_fixing)
        self.fix_btn.pack(side='left', padx=5)
        
        self.download_btn = ttk.Button(buttons_frame, text="下载结果", 
                                      command=self.download_result, state='disabled')
        self.download_btn.pack(side='left', padx=5)
        
    def select_source_file(self):
        """选择源文件"""
        filetypes = [
            ("Word文档", "*.docx"),
            ("Word文档旧版", "*.doc"),
            ("所有文件", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="选择源文件",
            filetypes=filetypes
        )
        
        if not filepath:
            return
            
        try:
            self.status_var.set(f"正在读取源文件: {os.path.basename(filepath)}")
            self.update_idletasks()
            
            # 读取文件内容
            text = self.file_handler.read_file(filepath)
            
            # 更新UI
            self.source_path_var.set(filepath)
            self.source_file = filepath
            
            # 显示预览
            self.source_preview.delete('1.0', tk.END)
            preview_text = text[:1000] + "..." if len(text) > 1000 else text
            self.source_preview.insert('1.0', preview_text)
            
            # 显示预览框
            self.source_preview_frame.pack(fill='both', expand=True, pady=10, after=source_frame)
            
            self.status_var.set(f"已加载源文件: {os.path.basename(filepath)}")
            logger.info(f"已加载源文件: {filepath}")
            
        except Exception as e:
            messagebox.showerror("文件读取错误", f"无法读取文件: {str(e)}")
            logger.error(f"文件读取错误: {str(e)}")
            self.status_var.set("源文件读取失败")
            
    def select_template_file(self):
        """选择模板文件"""
        filetypes = [
            ("Word文档", "*.docx"),
            ("Word文档旧版", "*.doc"),
            ("所有文件", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="选择格式模板文件",
            filetypes=filetypes
        )
        
        if not filepath:
            return
            
        try:
            self.status_var.set(f"正在读取模板文件: {os.path.basename(filepath)}")
            self.update_idletasks()
            
            # 读取文件内容
            text = self.file_handler.read_file(filepath)
            
            # 更新UI
            self.template_path_var.set(filepath)
            self.template_file = filepath
            
            # 显示预览
            self.template_preview.delete('1.0', tk.END)
            preview_text = text[:1000] + "..." if len(text) > 1000 else text
            self.template_preview.insert('1.0', preview_text)
            
            # 显示预览框
            self.template_preview_frame.pack(fill='both', expand=True, pady=10, after=template_frame)
            
            self.status_var.set(f"已加载模板文件: {os.path.basename(filepath)}")
            logger.info(f"已加载模板文件: {filepath}")
            
        except Exception as e:
            messagebox.showerror("文件读取错误", f"无法读取文件: {str(e)}")
            logger.error(f"文件读取错误: {str(e)}")
            self.status_var.set("模板文件读取失败")
            
    def start_format_fixing(self):
        """开始格式调整"""
        # 检查是否选择了文件
        if not self.source_file:
            messagebox.showwarning("提示", "请先选择源文件")
            return
            
        if not self.template_file:
            messagebox.showwarning("提示", "请先选择格式模板文件")
            return
            
        # 获取选项
        options = {
            "adjust_fonts": self.adjust_fonts_var.get(),
            "adjust_spacing": self.adjust_spacing_var.get(),
            "adjust_margins": self.adjust_margins_var.get(),
            "adjust_headings": self.adjust_headings_var.get(),
            "keep_content": self.keep_content_var.get()
        }
        
        # 更新UI状态
        self.status_var.set("正在调整格式...")
        self.fix_btn.config(state='disabled')
        self.progress.start()
        self.update_idletasks()
        
        # 在后台线程中处理
        self.after(100, lambda: self.process_in_background(options))
        
    def process_in_background(self, options):
        """在后台处理格式调整"""
        try:
            # 调整格式
            result_path = self.format_fixer.fix_format(
                self.source_file,
                self.template_file,
                options
            )
            
            if result_path:
                # 成功生成
                self.result_file = result_path
                self.status_var.set("格式调整完成")
                self.download_btn.config(state='normal')
                messagebox.showinfo("成功", "文档格式已调整完成，可以下载结果")
            else:
                raise Exception("格式调整失败")
                
        except Exception as e:
            messagebox.showerror("处理错误", f"格式调整失败: {str(e)}")
            logger.error(f"格式调整失败: {str(e)}")
            self.status_var.set("处理失败")
            
        finally:
            # 恢复UI状态
            self.fix_btn.config(state='normal')
            self.progress.stop()
            
    def download_result(self):
        """下载调整后的文件"""
        if not hasattr(self, 'result_file') or not os.path.exists(self.result_file):
            messagebox.showinfo("提示", "没有可下载的结果文件")
            return
            
        # 选择保存位置
        source_basename = os.path.basename(self.source_file)
        name, ext = os.path.splitext(source_basename)
        default_name = f"{name}_格式已调整{ext}"
        
        filepath = filedialog.asksaveasfilename(
            title="保存调整后的文件",
            defaultextension=".docx",
            initialfile=default_name,
            filetypes=[
                ("Word文档", "*.docx"),
                ("Word文档旧版", "*.doc"),
                ("所有文件", "*.*")
            ]
        )
        
        if not filepath:
            return
            
        try:
            # 复制结果文件到选择的位置
            import shutil
            shutil.copy2(self.result_file, filepath)
            
            self.status_var.set(f"文件已保存: {os.path.basename(filepath)}")
            messagebox.showinfo("成功", f"文件已保存至:\n{filepath}")
            logger.info(f"调整后的文件已保存: {filepath}")
                
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存文件: {str(e)}")
            logger.error(f"保存文件错误: {str(e)}")
            self.status_var.set("保存失败")