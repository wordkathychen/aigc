import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import time
from typing import Dict, List, Optional, Tuple

from src.models.text_detector import TextDetector
from src.utils.file_handler import FileHandler
from src.utils.logger import setup_logger
from src.gui.components.scrolled_text import ScrolledText
from src.gui.components.progress_bar import ProgressBar
from src.gui.components.tooltip import ToolTip

logger = setup_logger(__name__)

class ReduceDuplication(ttk.Frame):
    """文本查重降重页面"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.file_handler = FileHandler()
        self.detector = TextDetector()
        self.current_file = None
        
        # 创建界面
        self.create_widgets()
        logger.info("初始化文本查重降重页面")
        
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
        
        # 中间文本区
        self.create_text_area()
        
        # 底部按钮区
        self.create_bottom_controls()
        
    def create_top_controls(self):
        """创建顶部控制区"""
        # 第一行 - 标题
        row1 = ttk.Frame(self.top_frame)
        row1.pack(fill='x', pady=5)
        
        ttk.Label(row1, text="查重降重", style="Title.TLabel").pack(side='left')
        
        # 第二行 - 文件操作和设置
        row2 = ttk.Frame(self.top_frame)
        row2.pack(fill='x', pady=5)
        
        # 文件操作按钮
        file_frame = ttk.Frame(row2)
        file_frame.pack(side='left')
        
        ttk.Button(file_frame, text="上传文件", command=self.upload_file).pack(side='left', padx=2)
        ttk.Button(file_frame, text="粘贴文本", command=self.paste_text).pack(side='left', padx=2)
        ttk.Button(file_frame, text="清空", command=self.clear_text).pack(side='left', padx=2)
        
        # 优化设置
        settings_frame = ttk.Frame(row2)
        settings_frame.pack(side='right')
        
        ttk.Label(settings_frame, text="优化强度:").pack(side='left')
        self.intensity_var = tk.StringVar(value="moderate")
        intensity_options = {
            "轻度": "light",
            "中度": "moderate", 
            "深度": "heavy"
        }
        intensity_cb = ttk.Combobox(settings_frame, 
                                    textvariable=self.intensity_var,
                                    values=list(intensity_options.keys()),
                                    width=10,
                                    state="readonly")
        intensity_cb.pack(side='left', padx=5)
        
        # 绑定显示值到实际值的映射
        def on_intensity_select(event):
            selected = intensity_cb.get()
            self.intensity_var.set(intensity_options[selected])
        
        intensity_cb.bind("<<ComboboxSelected>>", on_intensity_select)
        intensity_cb.set("中度")  # 设置默认显示值
        
    def create_text_area(self):
        """创建文本区域"""
        # 创建水平分割的两个文本区
        paned = ttk.PanedWindow(self.middle_frame, orient='horizontal')
        paned.pack(fill='both', expand=True)
        
        # 左侧原文区
        left_frame = ttk.LabelFrame(paned, text="原始文本")
        paned.add(left_frame, weight=1)
        
        self.original_text = ScrolledText(left_frame)
        self.original_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 右侧优化区
        right_frame = ttk.LabelFrame(paned, text="优化文本 (绿色标记为修改部分)")
        paned.add(right_frame, weight=1)
        
        self.optimized_text = ScrolledText(right_frame)
        self.optimized_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 相似度显示区
        self.similarity_label = ttk.Label(right_frame, text="相似度: 暂无数据")
        self.similarity_label.pack(anchor='e', padx=5, pady=2)
        
        # 初始状态设置
        self.optimized_text.config(state='disabled')
        
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
        
        self.optimize_btn = ttk.Button(buttons_frame, text="开始优化", 
                                       command=self.start_optimization)
        self.optimize_btn.pack(side='left', padx=5)
        
        self.download_btn = ttk.Button(buttons_frame, text="下载结果", 
                                      command=self.download_result, state='disabled')
        self.download_btn.pack(side='left', padx=5)
        
        self.copy_btn = ttk.Button(buttons_frame, text="复制结果", 
                                  command=self.copy_result, state='disabled')
        self.copy_btn.pack(side='left', padx=5)
        
    def upload_file(self):
        """上传文件"""
        filetypes = [
            ("Word文档", "*.docx"),
            ("Word文档旧版", "*.doc"),
            ("PDF文档", "*.pdf"),
            ("文本文件", "*.txt"),
            ("所有文件", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="选择文件",
            filetypes=filetypes
        )
        
        if not filepath:
            return
            
        try:
            self.status_var.set(f"正在读取文件: {os.path.basename(filepath)}")
            self.update_idletasks()
            
            # 读取文件内容
            text = self.file_handler.read_file(filepath)
            
            # 更新UI
            self.clear_text()
            self.original_text.insert('1.0', text)
            self.current_file = filepath
            
            self.status_var.set(f"已加载文件: {os.path.basename(filepath)}")
            logger.info(f"已加载文件: {filepath}")
            
        except Exception as e:
            messagebox.showerror("文件读取错误", f"无法读取文件: {str(e)}")
            logger.error(f"文件读取错误: {str(e)}")
            self.status_var.set("文件读取失败")
            
    def paste_text(self):
        """粘贴文本"""
        text = self.clipboard_get()
        if text:
            self.original_text.delete('1.0', tk.END)
            self.original_text.insert('1.0', text)
            self.status_var.set("已粘贴文本")
            self.current_file = None
        else:
            messagebox.showinfo("提示", "剪贴板为空")
            
    def clear_text(self):
        """清空文本"""
        self.original_text.delete('1.0', tk.END)
        self.optimized_text.config(state='normal')
        self.optimized_text.delete('1.0', tk.END)
        self.optimized_text.config(state='disabled')
        self.similarity_label.config(text="相似度: 暂无数据")
        self.status_var.set("就绪")
        self.download_btn.config(state='disabled')
        self.copy_btn.config(state='disabled')
        self.current_file = None
            
    def start_optimization(self):
        """开始优化处理"""
        text = self.original_text.get('1.0', tk.END).strip()
        if not text:
            messagebox.showinfo("提示", "请先输入或上传文本")
            return
            
        # 获取参数
        intensity = self.intensity_var.get()
            
        # 更新UI状态
        self.status_var.set("正在优化文本...")
        self.optimize_btn.config(state='disabled')
        self.progress.start()
        self.update_idletasks()
            
        # 在后台线程中处理，避免UI冻结
        self.after(100, lambda: self.process_in_background(text, intensity))
            
    def process_in_background(self, text, intensity):
        """在后台处理文本"""
        try:
            # 处理文本
            result = self.detector.process(text, intensity)
            
            # 更新UI
            self.update_result(result)
            
            # 完成处理
            self.status_var.set("优化完成")
            self.download_btn.config(state='normal')
            self.copy_btn.config(state='normal')
            
        except Exception as e:
            messagebox.showerror("处理错误", f"文本优化失败: {str(e)}")
            logger.error(f"文本优化失败: {str(e)}")
            self.status_var.set("处理失败")
            
        finally:
            # 恢复UI状态
            self.optimize_btn.config(state='normal')
            self.progress.stop()
            
    def update_result(self, result: Dict):
        """更新结果显示"""
        # 更新相似度标签
        similarity = result.get('similarity_score', 0) * 100
        
        if similarity <= 10:
            similarity_status = "优秀"
        elif similarity <= 30:
            similarity_status = "良好"
        else:
            similarity_status = "一般"
        
        self.similarity_label.config(
            text=f"相似度: {similarity:.1f}% ({similarity_status})"
        )
        
        # 更新优化后文本，带颜色标记
        self.optimized_text.config(state='normal')
        self.optimized_text.delete('1.0', tk.END)
        self.optimized_text.insert('1.0', result['optimized_text'])
        
        # 标记修改部分为绿色
        for start_pos, end_pos, similarity in result.get('similarity_regions', []):
            if similarity < 0.8:  # 相似度低于80%的区域标记为绿色
                # 转换字符位置到Tkinter文本位置
                try:
                    start_idx = self.optimized_text.index(f"1.0 + {start_pos} chars")
                    end_idx = self.optimized_text.index(f"1.0 + {end_pos} chars")
                    self.optimized_text.tag_add("modified", start_idx, end_idx)
                except Exception as e:
                    logger.error(f"标记文本失败: {str(e)}")
        
        self.optimized_text.tag_configure("modified", foreground="green")
        self.optimized_text.config(state='disabled')
        
    def download_result(self):
        """下载优化结果"""
        if not hasattr(self.detector, 'optimized_text') or not self.detector.optimized_text:
            messagebox.showinfo("提示", "没有可下载的优化文本")
            return
            
        # 确定默认文件名
        default_name = "优化后的文本.docx"
        if self.current_file:
            basename = os.path.basename(self.current_file)
            name, ext = os.path.splitext(basename)
            default_name = f"{name}_优化后{ext}"
            
        # 选择保存位置
        filepath = filedialog.asksaveasfilename(
            title="保存优化后的文本",
            defaultextension=".docx",
            initialfile=default_name,
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
            
            success = self.file_handler.save_file(
                filepath, 
                self.detector.optimized_text,
                self.detector.original_text,
                highlight_changes=True
            )
            
            if success:
                self.status_var.set(f"文件已保存: {os.path.basename(filepath)}")
                messagebox.showinfo("成功", f"文件已保存至:\n{filepath}")
                logger.info(f"优化后的文件已保存: {filepath}")
            else:
                raise Exception("文件保存失败")
                
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存文件: {str(e)}")
            logger.error(f"保存文件错误: {str(e)}")
            self.status_var.set("保存失败")
            
    def copy_result(self):
        """复制优化结果到剪贴板"""
        if not hasattr(self.detector, 'optimized_text') or not self.detector.optimized_text:
            messagebox.showinfo("提示", "没有可复制的优化文本")
            return
            
        self.clipboard_clear()
        self.clipboard_append(self.detector.optimized_text)
        self.status_var.set("优化文本已复制到剪贴板")
        messagebox.showinfo("成功", "优化后的文本已复制到剪贴板")