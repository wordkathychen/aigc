import tkinter as tk
from tkinter import ttk, scrolledtext
from models.text_detector import TextDetector
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DetectorPage(ttk.Frame):
    def __init__(self, master, text_detector: TextDetector):
        super().__init__(master)
        self.detector = text_detector
        self.create_widgets()
        
    def create_widgets(self):
        # 创建左右分栏
        left_frame = ttk.Frame(self)
        left_frame.pack(side='left', fill='both', expand=True)
        
        right_frame = ttk.Frame(self)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # 左侧：文本输入区
        input_label = ttk.Label(left_frame, text="待检测文本：")
        input_label.pack(pady=5)
        
        self.text_input = scrolledtext.ScrolledText(left_frame, height=20)
        self.text_input.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 右侧：参考文本区
        ref_label = ttk.Label(right_frame, text="参考文本：")
        ref_label.pack(pady=5)
        
        self.ref_text = scrolledtext.ScrolledText(right_frame, height=20)
        self.ref_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 底部：按钮和结果区
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="检测相似度", 
                  command=self._check_similarity).pack(side='left', padx=5)
        ttk.Button(button_frame, text="AI检测", 
                  command=self._detect_ai).pack(side='left', padx=5)
        
        # 结果显示区
        result_frame = ttk.LabelFrame(self, text="检测结果")
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=10)
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def _check_similarity(self):
        """执行相似度检测"""
        try:
            text = self.text_input.get('1.0', 'end-1c')
            ref_text = self.ref_text.get('1.0', 'end-1c').split('\n\n')  # 按空行分割参考文本
            
            if not text or not ref_text:
                raise ValueError("请输入待检测文本和参考文本")
                
            result = self.detector.check_similarity(text, ref_text)
            self._show_result("相似度检测结果", result)
            
        except Exception as e:
            logger.error(f"相似度检测失败: {str(e)}")
            self._show_error(str(e))
            
    def _detect_ai(self):
        """执行AI检测"""
        try:
            text = self.text_input.get('1.0', 'end-1c')
            
            if not text:
                raise ValueError("请输入待检测文本")
                
            result = self.detector.detect_ai_generated(text)
            self._show_result("AI检测结果", result)
            
        except Exception as e:
            logger.error(f"AI检测失败: {str(e)}")
            self._show_error(str(e))
            
    def _show_result(self, title: str, result: Dict):
        """显示检测结果"""
        self.result_text.delete('1.0', 'end')
        self.result_text.insert('1.0', f"{title}\n{'='*50}\n\n")
        
        if isinstance(result, dict):
            for key, value in result.items():
                self.result_text.insert('end', f"{key}:\n{value}\n\n")
        else:
            self.result_text.insert('end', str(result))
            
    def _show_error(self, error_msg: str):
        """显示错误信息"""
        self.result_text.delete('1.0', 'end')
        self.result_text.insert('1.0', f"错误：{error_msg}")