import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import pandas as pd
from typing import Dict, List, Optional, Any

from src.models.survey_designer import SurveyGenerator, SurveyDataGenerator
from src.utils.file_handler import FileHandler
from src.utils.logger import setup_logger
from src.gui.components.scrolled_text import ScrolledText
from src.gui.components.progress_bar import ProgressBar
from src.gui.components.tooltip import ToolTip

logger = setup_logger(__name__)

class SurveyGenerator(ttk.Frame):
    """问卷生成页面"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.file_handler = FileHandler()
        self.survey_generator = SurveyGenerator()
        self.data_generator = SurveyDataGenerator()
        
        # 创建界面
        self.create_widgets()
        logger.info("初始化问卷生成页面")
        
    def create_widgets(self):
        """创建页面组件"""
        # 创建标签页
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.survey_page = ttk.Frame(self.notebook)
        self.data_page = ttk.Frame(self.notebook)
        
        self.notebook.add(self.survey_page, text="问卷设计")
        self.notebook.add(self.data_page, text="问卷数据生成")
        
        # 创建各页面内容
        self.create_survey_page()
        self.create_data_page()
        
    def create_survey_page(self):
        """创建问卷设计页面"""
        frame = ttk.Frame(self.survey_page)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 顶部说明
        desc = ttk.Label(frame, 
                        text="问卷设计: 可通过上传文件反向制作问卷，或直接输入问卷题目",
                        wraplength=600)
        desc.pack(anchor='w', pady=5)
        
        # 模式选择
        mode_frame = ttk.Frame(frame)
        mode_frame.pack(fill='x', pady=10)
        
        ttk.Label(mode_frame, text="生成模式:").pack(side='left')
        self.survey_mode_var = tk.StringVar(value="文本生成")
        modes = ["文本生成", "数据反向生成"]
        mode_cb = ttk.Combobox(mode_frame, textvariable=self.survey_mode_var, 
                              values=modes, width=15, state="readonly")
        mode_cb.pack(side='left', padx=5)
        mode_cb.bind("<<ComboboxSelected>>", self.on_survey_mode_change)
        
        # 文件上传框（初始隐藏）
        self.survey_file_frame = ttk.LabelFrame(frame, text="上传数据文件")
        
        self.survey_file_path_var = tk.StringVar()
        ttk.Entry(self.survey_file_frame, textvariable=self.survey_file_path_var, 
                 width=50, state='readonly').pack(side='left', padx=5, pady=5, fill='x', expand=True)
        ttk.Button(self.survey_file_frame, text="选择文件", 
                  command=self.select_survey_file).pack(side='right', padx=5, pady=5)
        
        # 问卷标题
        title_frame = ttk.LabelFrame(frame, text="问卷标题")
        title_frame.pack(fill='x', pady=10)
        
        self.survey_title_var = tk.StringVar()
        ttk.Entry(title_frame, textvariable=self.survey_title_var, width=60).pack(padx=10, pady=10, fill='x')
        
        # 问卷内容编辑
        content_frame = ttk.LabelFrame(frame, text="问卷内容")
        content_frame.pack(fill='both', expand=True, pady=10)
        
        # 提示文本
        hint = """请输入问卷内容，格式如下：
        
1. 单选题：您的性别是？
A. 男
B. 女

2. 多选题：您平时喜欢哪些运动？（多选）
A. 跑步
B. 游泳
C. 篮球
D. 足球

3. 填空题：请问您的年龄是？
__________

4. 量表题：您对我们的服务满意度如何？（1-5分，1分最低，5分最高）
1 2 3 4 5

5. 开放题：请分享您对产品的建议或意见。
__________
        """
        
        self.survey_content = ScrolledText(content_frame)
        self.survey_content.pack(fill='both', expand=True, padx=5, pady=5)
        self.survey_content.insert('1.0', hint)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(frame, text="问卷预览")
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        self.survey_preview = ScrolledText(preview_frame)
        self.survey_preview.pack(fill='both', expand=True, padx=5, pady=5)
        self.survey_preview.config(state='disabled')
        
        # 底部按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=10)
        
        self.survey_status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(button_frame, textvariable=self.survey_status_var)
        status_label.pack(side='left', padx=5)
        
        self.survey_progress = ProgressBar(button_frame, width=200)
        self.survey_progress.pack(side='left', padx=10)
        
        self.preview_btn = ttk.Button(button_frame, text="预览问卷", 
                                    command=self.preview_survey)
        self.preview_btn.pack(side='right', padx=5)
        
        self.generate_survey_btn = ttk.Button(button_frame, text="生成问卷", 
                                           command=self.generate_survey)
        self.generate_survey_btn.pack(side='right', padx=5)
        
        self.download_survey_btn = ttk.Button(button_frame, text="下载问卷", 
                                           command=self.download_survey, state='disabled')
        self.download_survey_btn.pack(side='right', padx=5)
        
    def create_data_page(self):
        """创建问卷数据生成页面"""
        frame = ttk.Frame(self.data_page)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 顶部说明
        desc = ttk.Label(frame, 
                        text="问卷数据生成: 可通过上传问卷文件或输入问卷内容，生成模拟的问卷数据",
                        wraplength=600)
        desc.pack(anchor='w', pady=5)
        
        # 模式选择
        mode_frame = ttk.Frame(frame)
        mode_frame.pack(fill='x', pady=10)
        
        ttk.Label(mode_frame, text="输入模式:").pack(side='left')
        self.data_mode_var = tk.StringVar(value="文本输入")
        modes = ["文本输入", "上传问卷文件"]
        mode_cb = ttk.Combobox(mode_frame, textvariable=self.data_mode_var, 
                              values=modes, width=15, state="readonly")
        mode_cb.pack(side='left', padx=5)
        mode_cb.bind("<<ComboboxSelected>>", self.on_data_mode_change)
        
        # 文件上传框（初始隐藏）
        self.data_file_frame = ttk.LabelFrame(frame, text="上传问卷文件")
        
        self.data_file_path_var = tk.StringVar()
        ttk.Entry(self.data_file_frame, textvariable=self.data_file_path_var, 
                 width=50, state='readonly').pack(side='left', padx=5, pady=5, fill='x', expand=True)
        ttk.Button(self.data_file_frame, text="选择文件", 
                  command=self.select_data_file).pack(side='right', padx=5, pady=5)
        
        # 问卷标题
        title_frame = ttk.LabelFrame(frame, text="问卷标题")
        title_frame.pack(fill='x', pady=10)
        
        self.data_title_var = tk.StringVar()
        ttk.Entry(title_frame, textvariable=self.data_title_var, width=60).pack(padx=10, pady=10, fill='x')
        
        # 问卷内容编辑
        content_frame = ttk.LabelFrame(frame, text="问卷内容")
        content_frame.pack(fill='both', expand=True, pady=10)
        
        self.data_content = ScrolledText(content_frame)
        self.data_content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 数据配置
        config_frame = ttk.LabelFrame(frame, text="数据生成配置")
        config_frame.pack(fill='x', pady=10)
        
        # 生成数量
        count_frame = ttk.Frame(config_frame)
        count_frame.pack(fill='x', pady=5)
        
        ttk.Label(count_frame, text="生成数量:").pack(side='left')
        self.data_count_var = tk.StringVar(value="100")
        ttk.Spinbox(count_frame, from_=10, to=1000, increment=10,
                   textvariable=self.data_count_var, width=10).pack(side='left', padx=5)
        
        # 数据倾向
        bias_frame = ttk.Frame(config_frame)
        bias_frame.pack(fill='x', pady=5)
        
        ttk.Label(bias_frame, text="数据倾向:").pack(side='left')
        self.data_bias_var = tk.StringVar(value="随机")
        biases = ["随机", "积极", "中立", "消极"]
        ttk.Combobox(bias_frame, textvariable=self.data_bias_var, 
                    values=biases, width=15, state="readonly").pack(side='left', padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=10)
        
        self.data_status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(button_frame, textvariable=self.data_status_var)
        status_label.pack(side='left', padx=5)
        
        self.data_progress = ProgressBar(button_frame, width=200)
        self.data_progress.pack(side='left', padx=10)
        
        self.generate_data_btn = ttk.Button(button_frame, text="生成数据", 
                                          command=self.generate_data)
        self.generate_data_btn.pack(side='right', padx=5)
        
        self.download_data_btn = ttk.Button(button_frame, text="下载数据", 
                                          command=self.download_data, state='disabled')
        self.download_data_btn.pack(side='right', padx=5)
        
    def on_survey_mode_change(self, event=None):
        """问卷生成模式变更处理"""
        mode = self.survey_mode_var.get()
        
        # 根据模式显示或隐藏文件上传区域
        if mode == "数据反向生成":
            self.survey_file_frame.pack(fill='x', pady=10, after=mode_frame)
        else:
            self.survey_file_frame.pack_forget()
            
        # 更新状态
        self.survey_status_var.set(f"已选择{mode}模式")
        
    def on_data_mode_change(self, event=None):
        """数据生成模式变更处理"""
        mode = self.data_mode_var.get()
        
        # 根据模式显示或隐藏文件上传区域
        if mode == "上传问卷文件":
            self.data_file_frame.pack(fill='x', pady=10, after=mode_frame)
            self.data_content.config(state='disabled')
        else:
            self.data_file_frame.pack_forget()
            self.data_content.config(state='normal')
            
        # 更新状态
        self.data_status_var.set(f"已选择{mode}模式")
        
    def select_survey_file(self):
        """选择问卷数据文件"""
        filetypes = [
            ("Excel文件", "*.xlsx *.xls"),
            ("CSV文件", "*.csv"),
            ("所有文件", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="选择问卷数据文件",
            filetypes=filetypes
        )
        
        if filepath:
            self.survey_file_path_var.set(filepath)
            self.survey_status_var.set(f"已选择文件: {os.path.basename(filepath)}")
            
    def select_data_file(self):
        """选择问卷文件"""
        filetypes = [
            ("Word文档", "*.docx *.doc"),
            ("文本文件", "*.txt"),
            ("所有文件", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="选择问卷文件",
            filetypes=filetypes
        )
        
        if filepath:
            self.data_file_path_var.set(filepath)
            self.data_status_var.set(f"已选择文件: {os.path.basename(filepath)}")
            
            # 尝试读取问卷内容
            try:
                content = self.file_handler.read_file(filepath)
                self.data_content.config(state='normal')
                self.data_content.delete('1.0', tk.END)
                self.data_content.insert('1.0', content)
                self.data_content.config(state='disabled')
            except Exception as e:
                logger.error(f"读取问卷文件失败: {str(e)}")
                
    def preview_survey(self):
        """预览问卷"""
        title = self.survey_title_var.get().strip()
        content = self.survey_content.get('1.0', tk.END).strip()
        
        if not title:
            messagebox.showwarning("提示", "请输入问卷标题")
            return
            
        if not content:
            messagebox.showwarning("提示", "请输入问卷内容")
            return
            
        # 更新预览
        self.survey_preview.config(state='normal')
        self.survey_preview.delete('1.0', tk.END)
        
        # 构建预览内容
        preview_text = f"{'=' * 50}\n{title}\n{'=' * 50}\n\n{content}"
        self.survey_preview.insert('1.0', preview_text)
        self.survey_preview.config(state='disabled')
        
        self.survey_status_var.set("问卷已预览")
        self.download_survey_btn.config(state='normal')
        
    def generate_survey(self):
        """生成问卷"""
        mode = self.survey_mode_var.get()
        title = self.survey_title_var.get().strip()
        
        if not title:
            messagebox.showwarning("提示", "请输入问卷标题")
            return
            
        # 更新UI状态
        self.survey_status_var.set("正在生成问卷...")
        self.generate_survey_btn.config(state='disabled')
        self.preview_btn.config(state='disabled')
        self.survey_progress.start()
        self.update_idletasks()
        
        # 在后台线程中处理
        threading.Thread(target=self._generate_survey_thread).start()
        
    def _generate_survey_thread(self):
        """在后台线程中生成问卷"""
        try:
            mode = self.survey_mode_var.get()
            title = self.survey_title_var.get().strip()
            
            if mode == "文本生成":
                # 直接从文本生成
                content = self.survey_content.get('1.0', tk.END).strip()
                
                if not content:
                    raise ValueError("请输入问卷内容")
                    
                # 生成问卷
                survey = self.survey_generator.generate_survey_from_text(title, content)
                
            else:
                # 从数据文件反向生成
                filepath = self.survey_file_path_var.get()
                
                if not filepath or not os.path.exists(filepath):
                    raise ValueError("请选择有效的数据文件")
                    
                # 生成问卷
                survey = self.survey_generator.generate_survey_from_data(title, filepath)
                
            # 更新UI
            self.after(0, lambda: self._update_survey_preview(survey))
            
        except Exception as e:
            logger.error(f"生成问卷失败: {str(e)}")
            self.after(0, lambda: self._handle_survey_error(str(e)))
            
    def _update_survey_preview(self, survey):
        """更新问卷预览"""
        self.survey_preview.config(state='normal')
        self.survey_preview.delete('1.0', tk.END)
        self.survey_preview.insert('1.0', survey)
        self.survey_preview.config(state='disabled')
        
        self.survey_status_var.set("问卷生成完成")
        self.survey_progress.stop()
        self.generate_survey_btn.config(state='normal')
        self.preview_btn.config(state='normal')
        self.download_survey_btn.config(state='normal')
        
        # 保存生成的问卷内容
        self.generated_survey = survey
        
        messagebox.showinfo("成功", "问卷生成完成，可以下载保存")
        
    def _handle_survey_error(self, error_msg):
        """处理问卷生成错误"""
        self.survey_status_var.set("生成失败")
        self.survey_progress.stop()
        self.generate_survey_btn.config(state='normal')
        self.preview_btn.config(state='normal')
        
        messagebox.showerror("错误", f"生成问卷失败: {error_msg}")
        
    def download_survey(self):
        """下载生成的问卷"""
        if not hasattr(self, 'generated_survey') and self.survey_preview.get('1.0', tk.END).strip():
            self.generated_survey = self.survey_preview.get('1.0', tk.END).strip()
            
        if not hasattr(self, 'generated_survey') or not self.generated_survey:
            messagebox.showinfo("提示", "没有可下载的问卷")
            return
            
        # 选择保存位置
        title = self.survey_title_var.get().strip() or "问卷"
        
        filepath = filedialog.asksaveasfilename(
            title="保存问卷",
            defaultextension=".docx",
            initialfile=f"{title}.docx",
            filetypes=[
                ("Word文档", "*.docx"),
                ("Word文档旧版", "*.doc"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if not filepath:
            return
            
        try:
            # 保存文件
            self.survey_status_var.set("正在保存文件...")
            self.update_idletasks()
            
            success = self.file_handler.save_file(filepath, self.generated_survey)
            
            if success:
                self.survey_status_var.set(f"文件已保存: {os.path.basename(filepath)}")
                messagebox.showinfo("成功", f"问卷已保存至:\n{filepath}")
                logger.info(f"问卷已保存: {filepath}")
            else:
                raise Exception("文件保存失败")
                
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存文件: {str(e)}")
            logger.error(f"保存文件错误: {str(e)}")
            self.survey_status_var.set("保存失败")
            
    def generate_data(self):
        """生成问卷数据"""
        mode = self.data_mode_var.get()
        title = self.data_title_var.get().strip()
        
        # 获取配置
        try:
            count = int(self.data_count_var.get())
            if count < 10 or count > 1000:
                raise ValueError("生成数量应在10-1000之间")
        except ValueError:
            messagebox.showwarning("提示", "生成数量应为10-1000之间的整数")
            return
            
        bias = self.data_bias_var.get()
        
        # 更新UI状态
        self.data_status_var.set("正在生成数据...")
        self.generate_data_btn.config(state='disabled')
        self.data_progress.start()
        self.update_idletasks()
        
        # 在后台线程中处理
        threading.Thread(target=lambda: self._generate_data_thread(count, bias)).start()
        
    def _generate_data_thread(self, count, bias):
        """在后台线程中生成数据"""
        try:
            mode = self.data_mode_var.get()
            title = self.data_title_var.get().strip()
            
            if mode == "文本输入":
                # 从文本生成
                content = self.data_content.get('1.0', tk.END).strip()
                
                if not content:
                    raise ValueError("请输入问卷内容")
                    
                # 生成数据
                df = self.data_generator.generate_data_from_text(
                    title, content, count=count, bias=bias
                )
                
            else:
                # 从问卷文件生成
                filepath = self.data_file_path_var.get()
                
                if not filepath or not os.path.exists(filepath):
                    raise ValueError("请选择有效的问卷文件")
                    
                # 生成数据
                df = self.data_generator.generate_data_from_file(
                    filepath, count=count, bias=bias
                )
                
            # 保存生成的数据
            self.generated_data = df
            
            # 更新UI
            self.after(0, lambda: self._update_data_status(True))
            
        except Exception as e:
            logger.error(f"生成数据失败: {str(e)}")
            self.after(0, lambda: self._handle_data_error(str(e)))
            
    def _update_data_status(self, success):
        """更新数据生成状态"""
        self.data_status_var.set("数据生成完成")
        self.data_progress.stop()
        self.generate_data_btn.config(state='normal')
        self.download_data_btn.config(state='normal')
        
        if success:
            messagebox.showinfo("成功", "问卷数据生成完成，可以下载保存")
        
    def _handle_data_error(self, error_msg):
        """处理数据生成错误"""
        self.data_status_var.set("生成失败")
        self.data_progress.stop()
        self.generate_data_btn.config(state='normal')
        
        messagebox.showerror("错误", f"生成数据失败: {error_msg}")
        
    def download_data(self):
        """下载生成的数据"""
        if not hasattr(self, 'generated_data') or self.generated_data is None:
            messagebox.showinfo("提示", "没有可下载的数据")
            return
            
        # 选择保存位置
        title = self.data_title_var.get().strip() or "问卷数据"
        
        filepath = filedialog.asksaveasfilename(
            title="保存数据",
            defaultextension=".xlsx",
            initialfile=f"{title}_数据.xlsx",
            filetypes=[
                ("Excel文件", "*.xlsx"),
                ("Excel旧版", "*.xls"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ]
        )
        
        if not filepath:
            return
            
        try:
            # 保存文件
            self.data_status_var.set("正在保存文件...")
            self.update_idletasks()
            
            # 根据文件扩展名选择保存格式
            _, ext = os.path.splitext(filepath)
            if ext.lower() == '.csv':
                self.generated_data.to_csv(filepath, index=False, encoding='utf-8-sig')
            else:
                self.generated_data.to_excel(filepath, index=False)
            
            self.data_status_var.set(f"文件已保存: {os.path.basename(filepath)}")
            messagebox.showinfo("成功", f"数据已保存至:\n{filepath}")
            logger.info(f"问卷数据已保存: {filepath}")
                
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存文件: {str(e)}")
            logger.error(f"保存文件错误: {str(e)}")
            self.data_status_var.set("保存失败")