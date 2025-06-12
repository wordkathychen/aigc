from . import BasePage
from tkinter import ttk, scrolledtext, messagebox, filedialog, StringVar
from tkinter import simpledialog
import threading
import asyncio
from src.config.settings import PROMPT_TEMPLATES
from src.models.paper_generator import PaperGenerator, OutlineEditor
from src.models.api_manager import APIManager
from src.utils.logger import setup_logger
import os
import tkinter as tk
import json
from typing import Dict, List, Optional, Any
from src.models.paper_generator import PaperGeneratorModel
from src.models.outline_generator import OutlineGenerator
from src.utils.file_handler import FileHandler
from src.gui.components.scrolled_text import ScrolledText
from src.gui.components.progress_bar import ProgressBar
from src.gui.components.tooltip import ToolTip
from src.utils.reference_generator import ReferenceGenerator

logger = setup_logger(__name__)

class PaperGenerator(ttk.Frame):
    """论文生成页面"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.file_handler = FileHandler()
        self.paper_generator = PaperGeneratorModel()
        self.outline_generator = OutlineGenerator()
        
        # 论文生成状态
        self.current_outline = None
        self.current_paper_type = None
        self.current_subject = None
        self.current_title = None
        self.current_word_count = None
        self.current_education_level = None
        self.current_images_required = False
        self.current_tables_required = False
        self.current_charts_required = False
        self.current_formulas_required = False
        
        # 创建界面
        self.create_widgets()
        logger.info("初始化论文生成页面")
        
    def create_widgets(self):
        """创建页面组件"""
        # 创建标签页
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.setup_page = ttk.Frame(self.notebook)
        self.outline_page = ttk.Frame(self.notebook)
        self.generate_page = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_page, text="1. 论文设置")
        self.notebook.add(self.outline_page, text="2. 大纲编辑")
        self.notebook.add(self.generate_page, text="3. 内容生成")
        
        # 创建各页面内容
        self.create_setup_page()
        self.create_outline_page()
        self.create_generate_page()
        
        # 默认禁用后续标签页，直到完成前置步骤
        self.notebook.tab(1, state='disabled')
        self.notebook.tab(2, state='disabled')
        
    def create_setup_page(self):
        """创建论文设置页面"""
        frame = ttk.Frame(self.setup_page)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 论文类型选择
        type_frame = ttk.LabelFrame(frame, text="论文类型")
        type_frame.pack(fill='x', pady=10)
        
        # 第一行：毕业论文、期刊论文
        row1 = ttk.Frame(type_frame)
        row1.pack(fill='x', pady=5)
        
        self.paper_type_var = tk.StringVar(value="毕业论文")
        ttk.Radiobutton(row1, text="毕业论文", variable=self.paper_type_var, 
                       value="毕业论文").pack(side='left', padx=10)
        ttk.Radiobutton(row1, text="期刊论文", variable=self.paper_type_var, 
                       value="期刊论文").pack(side='left', padx=10)
        
        # 第二行：其他论文类型
        row2 = ttk.Frame(type_frame)
        row2.pack(fill='x', pady=5)
        
        other_types = ["开题报告", "任务书", "调研报告", "实习报告", 
                      "读后感", "思想汇报", "实验报告"]
        col = 0
        for paper_type in other_types:
            ttk.Radiobutton(row2, text=paper_type, variable=self.paper_type_var, 
                           value=paper_type).grid(row=0, column=col, padx=10)
            col += 1
        
        # 学校模板选择
        template_frame = ttk.LabelFrame(frame, text="学校模板")
        template_frame.pack(fill='x', pady=10)
        
        self.template_var = tk.StringVar(value="通用模板")
        
        # 获取已有的学校模板列表
        self.school_templates = self.get_school_templates()
        
        template_combobox = ttk.Combobox(template_frame, textvariable=self.template_var, 
                                      values=self.school_templates, width=40)
        template_combobox.pack(side='left', padx=10, pady=5)
        
        # 上传模板按钮
        ttk.Button(template_frame, text="上传新模板", 
                  command=self.upload_template).pack(side='right', padx=10)
        
        # 学科选择
        subject_frame = ttk.LabelFrame(frame, text="学科选择")
        subject_frame.pack(fill='x', pady=10)
        
        subjects = ["土木工程", "学前教育", "计算机科学", "单片机", "机械工程", "通用"]
        
        self.subject_var = tk.StringVar(value="通用")
        for i, subject in enumerate(subjects):
            ttk.Radiobutton(subject_frame, text=subject, variable=self.subject_var, 
                           value=subject).pack(side='left', padx=10)
        
        # 学历选择
        edu_frame = ttk.LabelFrame(frame, text="学历层次")
        edu_frame.pack(fill='x', pady=10)
        
        self.education_var = tk.StringVar(value="本科")
        ttk.Radiobutton(edu_frame, text="大专", variable=self.education_var, 
                       value="大专").pack(side='left', padx=10)
        ttk.Radiobutton(edu_frame, text="本科", variable=self.education_var, 
                       value="本科").pack(side='left', padx=10)
        ttk.Radiobutton(edu_frame, text="研究生", variable=self.education_var, 
                       value="研究生").pack(side='left', padx=10)
        
        # 字数选择
        word_frame = ttk.LabelFrame(frame, text="字数选择")
        word_frame.pack(fill='x', pady=10)
        
        self.word_count_var = tk.StringVar(value="6000")
        word_counts = ["3000", "6000", "10000", "15000", "20000", "30000"]
        
        for count in word_counts:
            ttk.Radiobutton(word_frame, text=f"{count}字", variable=self.word_count_var, 
                           value=count).pack(side='left', padx=10)
        
        # 论文标题
        title_frame = ttk.LabelFrame(frame, text="论文标题")
        title_frame.pack(fill='x', pady=10)
        
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(title_frame, textvariable=self.title_var, width=60)
        title_entry.pack(side='left', padx=10, pady=10, fill='x', expand=True)
        
        # 按钮区域
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="生成大纲", 
                  command=self.generate_outline).pack(side='right', padx=10)
        
    def create_outline_page(self):
        """创建大纲编辑页面"""
        frame = ttk.Frame(self.outline_page)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 上半部分：大纲显示和编辑
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill='both', expand=True, pady=10)
        
        # 大纲级别选择
        level_frame = ttk.Frame(top_frame)
        level_frame.pack(fill='x', pady=5)
        
        ttk.Label(level_frame, text="大纲级别:").pack(side='left', padx=5)
        self.outline_level_var = tk.StringVar(value="三级大纲")
        ttk.Radiobutton(level_frame, text="一级大纲", variable=self.outline_level_var, 
                       value="一级大纲", command=self.update_outline_display).pack(side='left', padx=10)
        ttk.Radiobutton(level_frame, text="二级大纲", variable=self.outline_level_var, 
                       value="二级大纲", command=self.update_outline_display).pack(side='left', padx=10)
        ttk.Radiobutton(level_frame, text="三级大纲", variable=self.outline_level_var, 
                       value="三级大纲", command=self.update_outline_display).pack(side='left', padx=10)
        
        # 大纲编辑器
        outline_editor_frame = ttk.LabelFrame(top_frame, text="大纲编辑")
        outline_editor_frame.pack(fill='both', expand=True, pady=10)
        
        self.outline_editor = ScrolledText(outline_editor_frame, height=15)
        self.outline_editor.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 特殊要求区域
        req_frame = ttk.LabelFrame(frame, text="内容需求")
        req_frame.pack(fill='x', pady=10)
        
        # 图表公式等特殊需求
        self.images_var = tk.BooleanVar(value=False)
        self.tables_var = tk.BooleanVar(value=False)
        self.charts_var = tk.BooleanVar(value=False)
        self.formulas_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(req_frame, text="需要图片", variable=self.images_var).pack(side='left', padx=20)
        ttk.Checkbutton(req_frame, text="需要表格", variable=self.tables_var).pack(side='left', padx=20)
        ttk.Checkbutton(req_frame, text="需要图表", variable=self.charts_var).pack(side='left', padx=20)
        ttk.Checkbutton(req_frame, text="需要公式", variable=self.formulas_var).pack(side='left', padx=20)
        
        # 按钮区域
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="重新生成大纲", 
                  command=self.regenerate_outline).pack(side='left', padx=10)
        ttk.Button(button_frame, text="手动保存大纲", 
                  command=self.save_outline).pack(side='left', padx=10)
        ttk.Button(button_frame, text="生成论文", 
                  command=self.start_paper_generation).pack(side='right', padx=10)
        
    def create_generate_page(self):
        """创建内容生成页面"""
        frame = ttk.Frame(self.generate_page)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 上半部分：生成状态和控制
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill='x', pady=10)
        
        # 生成状态显示
        status_frame = ttk.LabelFrame(top_frame, text="生成状态")
        status_frame.pack(fill='x', pady=5)
        
        self.status_var = tk.StringVar(value="准备生成...")
        ttk.Label(status_frame, textvariable=self.status_var, 
                 font=('SimHei', 10)).pack(side='left', padx=10, pady=5)
        
        self.progress_bar = ProgressBar(status_frame, width=300)
        self.progress_bar.pack(side='right', padx=10, pady=5)
        
        # 当前生成章节信息
        section_frame = ttk.LabelFrame(top_frame, text="当前章节")
        section_frame.pack(fill='x', pady=5)
        
        self.current_section_var = tk.StringVar(value="等待开始...")
        ttk.Label(section_frame, textvariable=self.current_section_var, 
                 font=('SimHei', 10, 'bold')).pack(padx=10, pady=5)
        
        # 下半部分：论文预览
        preview_frame = ttk.LabelFrame(frame, text="论文预览")
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        self.paper_preview = ScrolledText(preview_frame)
        self.paper_preview.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 参考文献生成设置
        ref_frame = ttk.LabelFrame(frame, text="参考文献设置")
        ref_frame.pack(fill='x', pady=10)
        
        # 参考文献数量
        ref_count_frame = ttk.Frame(ref_frame)
        ref_count_frame.pack(fill='x', pady=5)
        
        ttk.Label(ref_count_frame, text="参考文献数量:").pack(side='left', padx=5)
        self.ref_count_var = tk.StringVar(value="10")
        ref_count_entry = ttk.Spinbox(ref_count_frame, from_=5, to=30, textvariable=self.ref_count_var, width=5)
        ref_count_entry.pack(side='left', padx=5)
        
        # 参考文献格式
        ref_format_frame = ttk.Frame(ref_frame)
        ref_format_frame.pack(fill='x', pady=5)
        
        ttk.Label(ref_format_frame, text="参考文献格式:").pack(side='left', padx=5)
        self.ref_format_var = tk.StringVar(value="GB/T 7714-2015")
        ttk.Radiobutton(ref_format_frame, text="GB/T 7714-2015", variable=self.ref_format_var, 
                       value="GB/T 7714-2015").pack(side='left', padx=10)
        ttk.Radiobutton(ref_format_frame, text="APA", variable=self.ref_format_var, 
                       value="APA").pack(side='left', padx=10)
        ttk.Radiobutton(ref_format_frame, text="MLA", variable=self.ref_format_var, 
                       value="MLA").pack(side='left', padx=10)
        
        # 底部按钮区
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="停止生成", 
                  command=self.stop_generation).pack(side='left', padx=10)
        ttk.Button(button_frame, text="生成参考文献", 
                  command=self.generate_references).pack(side='left', padx=10)
        ttk.Button(button_frame, text="下载论文", 
                  command=self.download_paper).pack(side='right', padx=10)
        
    def generate_outline(self):
        """生成论文大纲"""
        # 获取用户输入
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("提示", "请输入论文标题")
            return
            
        paper_type = self.paper_type_var.get()
        subject = self.subject_var.get()
        education = self.education_var.get()
        word_count = self.word_count_var.get()
        
        # 更新状态
        self.current_paper_type = paper_type
        self.current_subject = subject
        self.current_title = title
        self.current_word_count = word_count
        self.current_education_level = education
        
        # 显示正在处理
        wait_window = tk.Toplevel(self)
        wait_window.title("正在生成")
        wait_window.geometry("300x100")
        wait_window.transient(self)
        wait_window.grab_set()
        
        ttk.Label(wait_window, text="正在生成大纲，请稍候...").pack(pady=20)
        progress = ttk.Progressbar(wait_window, mode='indeterminate')
        progress.pack(fill='x', padx=20)
        progress.start()
        
        wait_window.update()
        
        try:
            # 生成大纲
            outline = self.outline_generator.generate_outline(
                title=title,
                paper_type=paper_type,
                subject=subject,
                education_level=education,
                word_count=int(word_count)
            )
            
            # 更新大纲
            self.current_outline = outline
            
            # 关闭等待窗口
            wait_window.destroy()
            
            # 显示大纲
            self.update_outline_display()
            
            # 启用大纲编辑标签页
            self.notebook.tab(1, state='normal')
            self.notebook.select(1)  # 切换到大纲页
            
            messagebox.showinfo("成功", "大纲生成完成，请检查并编辑大纲")
            
        except Exception as e:
            wait_window.destroy()
            messagebox.showerror("错误", f"大纲生成失败: {str(e)}")
            logger.error(f"大纲生成失败: {str(e)}")
        
    def update_outline_display(self):
        """更新大纲显示"""
        if not self.current_outline:
            return
            
        # 清空编辑器
        self.outline_editor.delete('1.0', tk.END)
        
        # 根据选择的级别显示大纲
        level = self.outline_level_var.get()
        max_level = 3
        if level == "一级大纲":
            max_level = 1
        elif level == "二级大纲":
            max_level = 2
        
        # 格式化大纲
        formatted_outline = self.format_outline_for_display(self.current_outline, max_level)
        
        # 显示大纲
        self.outline_editor.insert('1.0', formatted_outline)
        
    def format_outline_for_display(self, outline, max_level=3, current_level=1, prefix=""):
        """将大纲格式化为显示文本"""
        if not outline or not isinstance(outline, list):
            return ""
            
        result = []
        for i, item in enumerate(outline):
            if isinstance(item, dict):
                # 处理标题
                title = item.get('title', f"标题 {i+1}")
                section_prefix = f"{prefix}{i+1}."
                result.append(f"{'  ' * (current_level-1)}{section_prefix} {title}")
                
                # 处理子标题（如果在允许的级别内）
                if current_level < max_level and 'subtitles' in item:
                    child_text = self.format_outline_for_display(
                        item['subtitles'], 
                        max_level, 
                        current_level + 1, 
                        section_prefix
                    )
                    result.append(child_text)
            else:
                # 直接处理文本项
                result.append(f"{'  ' * (current_level-1)}{prefix}{i+1}. {item}")
                
        return "\n".join(result)
        
    def parse_outline_from_editor(self):
        """从编辑器解析大纲结构"""
        text = self.outline_editor.get('1.0', tk.END).strip()
        lines = text.split('\n')
        
        # 解析大纲结构
        outline = []
        current_items = {0: outline}  # 存储每个级别的当前项列表
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 判断大纲级别和标题
            indent_level = 0
            while line.startswith('  '):
                indent_level += 1
                line = line[2:]
                
            # 提取标题内容
            parts = line.split('. ', 1)
            if len(parts) != 2:
                # 跳过格式不正确的行
                continue
                
            section_num, title = parts
            
            # 创建节点
            node = {"title": title}
            
            # 添加到适当的父级
            parent_level = indent_level - 1
            if parent_level < 0:
                # 顶级节点
                outline.append(node)
            else:
                if parent_level not in current_items:
                    # 出错的大纲结构，忽略
                    continue
                    
                parent_list = current_items[parent_level]
                if not parent_list:
                    continue
                    
                parent = parent_list[-1]
                if 'subtitles' not in parent:
                    parent['subtitles'] = []
                    
                parent['subtitles'].append(node)
                
            # 更新当前级别的项列表
            current_items[indent_level] = current_items.get(indent_level, [])
            current_items[indent_level].append(node)
            
            # 清除此级别以下的所有项
            for level in list(current_items.keys()):
                if level > indent_level:
                    current_items.pop(level)
        
        return outline
        
    def regenerate_outline(self):
        """重新生成大纲"""
        if messagebox.askyesno("确认", "确定要重新生成大纲吗？当前编辑将丢失。"):
            self.generate_outline()
        
    def save_outline(self):
        """保存当前大纲"""
        # 从编辑器解析大纲
        try:
            outline = self.parse_outline_from_editor()
            self.current_outline = outline
            messagebox.showinfo("成功", "大纲已保存")
        except Exception as e:
            messagebox.showerror("错误", f"大纲解析失败: {str(e)}")
            logger.error(f"大纲解析失败: {str(e)}")
        
    def start_paper_generation(self):
        """开始论文生成"""
        # 保存大纲和需求设置
        self.save_outline()
        
        # 获取特殊需求设置
        self.current_images_required = self.images_var.get()
        self.current_tables_required = self.tables_var.get()
        self.current_charts_required = self.charts_var.get()
        self.current_formulas_required = self.formulas_var.get()
        
        # 检查是否有大纲
        if not self.current_outline:
            messagebox.showwarning("提示", "请先生成大纲")
            return
            
        # 确认生成
        if not messagebox.askyesno("确认", "确定要开始生成论文吗？"):
            return
            
        # 启用生成页面
        self.notebook.tab(2, state='normal')
        self.notebook.select(2)  # 切换到生成页
        
        # 开始生成
        self.status_var.set("正在准备生成...")
        self.current_section_var.set("准备中...")
        self.paper_preview.delete('1.0', tk.END)
        self.progress_bar.start()
        
        # 在后台线程中处理
        self.after(100, self.generate_paper_in_background)
        
    def generate_paper_in_background(self):
        """在后台生成论文"""
        try:
            # 配置生成参数
            config = {
                "title": self.current_title,
                "paper_type": self.current_paper_type,
                "subject": self.current_subject,
                "education_level": self.current_education_level,
                "word_count": int(self.current_word_count),
                "outline": self.current_outline,
                "requirements": {
                    "images": self.current_images_required,
                    "tables": self.current_tables_required,
                    "charts": self.current_charts_required,
                    "formulas": self.current_formulas_required
                },
                "template": self.template_var.get()
            }
            
            # 注册进度回调
            def update_progress(section_title, progress, content):
                self.current_section_var.set(f"正在生成: {section_title}")
                self.progress_bar.set_value(progress * 100)
                
                # 更新预览
                self.paper_preview.delete('1.0', tk.END)
                self.paper_preview.insert('1.0', content)
                
                # 确保UI更新
                self.update_idletasks()
            
            # 使用新的生成顺序生成论文
            result = self.paper_generator.generate_full_paper_with_new_order(
                config, progress_callback=update_progress
            )
            
            # 完成生成
            self.status_var.set("论文生成完成")
            self.current_section_var.set("已完成")
            self.progress_bar.stop()
            
            # 显示结果
            self.paper_preview.delete('1.0', tk.END)
            self.paper_preview.insert('1.0', result["content"])
            
            messagebox.showinfo("成功", "论文生成完成，可以下载保存")
            
        except Exception as e:
            self.status_var.set("生成失败")
            self.progress_bar.stop()
            messagebox.showerror("错误", f"论文生成失败: {str(e)}")
            logger.error(f"论文生成失败: {str(e)}")
        
    def stop_generation(self):
        """停止论文生成"""
        if messagebox.askyesno("确认", "确定要停止生成吗？"):
            self.paper_generator.stop_generation()
            self.status_var.set("已停止生成")
            self.progress_bar.stop()
        
    def download_paper(self):
        """下载生成的论文"""
        content = self.paper_preview.get('1.0', tk.END).strip()
        if not content:
            messagebox.showinfo("提示", "没有可下载的内容")
            return
            
        # 选择保存位置
        filepath = filedialog.asksaveasfilename(
            title="保存论文",
            defaultextension=".docx",
            initialfile=f"{self.current_title}.docx",
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
            self.status_var.set("正在保存文件...")
            self.update_idletasks()
            
            success = self.file_handler.save_file(filepath, content)
            
            if success:
                self.status_var.set(f"文件已保存: {os.path.basename(filepath)}")
                messagebox.showinfo("成功", f"论文已保存至:\n{filepath}")
                logger.info(f"论文已保存: {filepath}")
            else:
                raise Exception("文件保存失败")
                
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存文件: {str(e)}")
            logger.error(f"保存文件错误: {str(e)}")
            self.status_var.set("保存失败")

    def get_school_templates(self):
        """获取已上传的学校模板列表"""
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        templates = ["通用模板"]  # 默认模板
        
        # 遍历模板目录
        for file in os.listdir(templates_dir):
            if file.endswith(".docx") and file != "default.docx":
                # 提取学校名称 (格式: 学校名_模板.docx)
                school_name = file.split('_')[0] if '_' in file else file.replace('.docx', '')
                if school_name not in templates:
                    templates.append(school_name)
                    
        return templates
        
    def upload_template(self):
        """上传新的学校模板"""
        # 打开文件选择对话框
        filepath = filedialog.askopenfilename(
            title="选择Word模板文件",
            filetypes=[("Word文档", "*.docx"), ("所有文件", "*.*")]
        )
        
        if not filepath:
            return
            
        # 获取学校名称
        school_name = simpledialog.askstring("学校名称", "请输入学校名称:")
        if not school_name:
            return
            
        # 复制模板到模板目录
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        target_path = os.path.join(templates_dir, f"{school_name}_模板.docx")
        
        try:
            import shutil
            shutil.copy2(filepath, target_path)
            
            # 更新模板列表
            self.school_templates = self.get_school_templates()
            
            # 将新模板设为当前选择
            self.template_var.set(school_name)
            
            messagebox.showinfo("成功", f"已添加{school_name}的论文模板")
            logger.info(f"上传模板成功: {school_name}")
            
        except Exception as e:
            messagebox.showerror("错误", f"上传模板失败: {str(e)}")
            logger.error(f"上传模板失败: {str(e)}")

    def generate_references(self):
        """生成参考文献"""
        # 获取参数
        count = int(self.ref_count_var.get())
        format_type = self.ref_format_var.get()
        title = self.current_title
        subject = self.current_subject
        
        # 显示正在处理
        self.status_var.set("正在生成参考文献...")
        self.current_section_var.set("参考文献")
        self.update_idletasks()
        
        try:
            # 创建参考文献生成器
            ref_generator = ReferenceGenerator()
            
            # 生成参考文献
            references = ref_generator.generate_references(
                topic=title,
                subject=subject,
                count=count,
                format_type=format_type
            )
            
            # 将参考文献添加到预览中
            current_content = self.paper_preview.get('1.0', tk.END)
            
            # 检查是否已有参考文献部分
            if "参考文献" in current_content:
                # 替换现有参考文献
                parts = current_content.split("参考文献")
                new_content = parts[0] + "参考文献\n\n" + references
                self.paper_preview.delete('1.0', tk.END)
                self.paper_preview.insert('1.0', new_content)
            else:
                # 添加新的参考文献部分
                self.paper_preview.insert(tk.END, "\n\n参考文献\n\n" + references)
            
            self.status_var.set("参考文献生成完成")
            
        except Exception as e:
            self.status_var.set("参考文献生成失败")
            messagebox.showerror("错误", f"参考文献生成失败: {str(e)}")
            logger.error(f"参考文献生成失败: {str(e)}")