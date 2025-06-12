from . import BasePage
from tkinter import ttk, scrolledtext
from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox
from models.text_optimizer import TextOptimizer
from utils.logger import setup_logger
import os
from PIL import Image, ImageTk
import time
from typing import Dict, List, Optional, Tuple

from src.models.text_detector import AIDetector
from src.utils.file_handler import FileHandler
from src.gui.components.scrolled_text import ScrolledText
from src.gui.components.progress_bar import ProgressBar
from src.gui.components.tooltip import ToolTip

logger = setup_logger(__name__)

class ReduceAI(BasePage):
    def create_widgets(self):
        # 标题
        ttk.Label(
            self,
            text="AI检测优化",
            style='Title.TLabel'
        ).pack(pady=20)
        
        # 操作区域
        control_frame = ttk.Frame(self, style='Dark.TFrame')
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # 上传按钮
        ttk.Button(
            control_frame,
            text="上传文档",
            command=self.upload_document
        ).pack(side='left', padx=5)
        
        # AI检测平台选择
        ttk.Label(control_frame, text="目标平台：").pack(side='left', padx=5)
        self.platform = ttk.Combobox(
            control_frame,
            values=["Copy Detection", "GPTZero", "Turnitin", "其他"]
        )
        self.platform.pack(side='left', padx=5)
        
        ttk.Button(
            control_frame,
            text="开始优化",
            command=self.start_optimization
        ).pack(side='right', padx=5)
        
        # 文本编辑区
        edit_frame = ttk.LabelFrame(self, text="文本编辑", style='Card.TFrame')
        edit_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.text_area = scrolledtext.ScrolledText(edit_frame)
        self.text_area.pack(fill='both', expand=True, padx=5, pady=5)
        
    def upload_document(self):
        file = filedialog.askopenfilename(
            title="选择文档",
            filetypes=[
                ("Word文件", "*.docx;*.doc"),
                ("文本文件", "*.txt")
            ]
        )
        if file:
            self.text_area.insert('end', f"已上传文件：{file}\n")
            
    def start_optimization(self):
        platform = self.platform.get()
        if not platform:
            self.text_area.insert('end', "请选择目标平台\n")
            return
        self.text_area.insert('end', f"正在针对 {platform} 进行优化...\n")
        
    def __init__(self, master, text_optimizer: TextOptimizer):
        super().__init__(master)
        self.optimizer = text_optimizer
        self.setup_ui()
        
    def setup_ui(self):
        # 创建左右分栏
        left_frame = ttk.Frame(self)
        left_frame.pack(side='left', fill='both', expand=True)
        
        right_frame = ttk.Frame(self)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # 左侧：原文输入
        input_label = ttk.Label(left_frame, text="原文:")
        input_label.pack(pady=5)
        
        self.input_text = scrolledtext.ScrolledText(left_frame, height=20)
        self.input_text.pack(fill='both', expand=True, padx=5)
        
        # 右侧：参考文本
        ref_label = ttk.Label(right_frame, text="参考文本:")
        ref_label.pack(pady=5)
        
        self.ref_text = scrolledtext.ScrolledText(right_frame, height=20)
        self.ref_text.pack(fill='both', expand=True, padx=5)
        
        # 控制按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="分析相似度", 
                  command=self._analyze_similarity).pack(side='left', padx=5)
        ttk.Button(button_frame, text="优化文本", 
                  command=self._optimize_text).pack(side='left', padx=5)
        
        # 结果显示
        result_frame = ttk.LabelFrame(self, text="分析结果")
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=10)
        self.result_text.pack(fill='both', expand=True, padx=5)
        
    def _analyze_similarity(self):
        """分析文本相似度"""
        try:
            original = self.input_text.get('1.0', 'end-1c')
            references = self.ref_text.get('1.0', 'end-1c').split('\n\n')
            
            if not original or not references:
                raise ValueError("请输入原文和参考文本")
                
            # 分析相似度
            result = self.optimizer.analyze_similarity(original, references)
            
            # 显示结果
            self.result_text.delete('1.0', 'end')
            self.result_text.insert('end', 
                f"总体相似度: {result['overall_similarity']:.2%}\n"
                f"最高相似度: {result['max_similarity']:.2%}\n\n"
                "相似片段分析：\n"
            )
            
            for idx, seg in enumerate(result['similar_segments'], 1):
                self.result_text.insert('end',
                    f"\n{idx}. 原文：{seg['original']}\n"
                    f"   相似：{seg['reference']}\n"
                    f"   相似度：{seg['similarity']:.2%}\n"
                )
                
            # 分析风格
            style = self.optimizer.analyze_style(original)
            self.result_text.insert('end', 
                f"\n文本风格分析：\n"
                f"平均句长：{style['avg_sentence_length']:.2f}\n"
                f"词汇丰富度：{style['unique_words_ratio']:.2%}\n"
                f"标点密度：{style['punctuation_ratio']:.2%}\n"
            )
            
        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            messagebox.showerror("错误", str(e))
            
    def _optimize_text(self):
        """优化文本"""
        try:
            original = self.input_text.get('1.0', 'end-1c')
            references = self.ref_text.get('1.0', 'end-1c').split('\n\n')
            
            # 先进行相似度分析
            result = self.optimizer.analyze_similarity(original, references)
            
            # 优化文本
            optimized = self.optimizer.optimize_text(
                original, 
                result['similar_segments']
            )
            
            # 创建结果预览窗口
            preview = tk.Toplevel(self)
            preview.title("优化结果")
            preview.geometry("600x400")
            
            result_text = scrolledtext.ScrolledText(preview)
            result_text.pack(fill='both', expand=True, padx=5, pady=5)
            result_text.insert('1.0', optimized)
            
        except Exception as e:
            logger.error(f"优化失败: {str(e)}")
            messagebox.showerror("错误", str(e))