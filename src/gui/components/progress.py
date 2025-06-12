import tkinter as tk
from tkinter import ttk
import threading
import queue
from typing import Optional
from config.settings import THEME_COLORS, FONTS

class ProgressManager:
    def __init__(self, master: tk.Widget):
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="就绪")
        self.queue = queue.Queue()
        
        # 创建进度条框架
        self.frame = ttk.Frame(master, style='Card.TFrame')
        self.frame.pack(fill='x', padx=20, pady=5)
        
        # 状态标签
        self.status_label = ttk.Label(
            self.frame,
            textvariable=self.status_var,
            style="Normal.TLabel"
        )
        self.status_label.pack(anchor='w', padx=5, pady=(5, 0))
        
        # 进度条
        self.progress_bar = ttk.Progressbar(
            self.frame,
            variable=self.progress_var,
            maximum=100,
            style="Custom.Horizontal.TProgressbar",
            length=300
        )
        self.progress_bar.pack(fill='x', padx=5, pady=5)
        
        # 百分比标签
        self.percent_label = ttk.Label(
            self.frame,
            text="0%",
            style="Normal.TLabel"
        )
        self.percent_label.pack(anchor='e', padx=5)
        
        self._update_thread: Optional[threading.Thread] = None
        self._running = False
    
    def start(self):
        """启动进度更新线程"""
        if self._update_thread and self._update_thread.is_alive():
            return
            
        self._running = True
        self._update_thread = threading.Thread(target=self._update_progress)
        self._update_thread.daemon = True
        self._update_thread.start()
    
    def stop(self):
        """停止进度更新线程"""
        self._running = False
        if self._update_thread:
            self._update_thread.join(timeout=1.0)
    
    def update(self, progress: float, status: str):
        """更新进度和状态"""
        self.queue.put((progress, status))
    
    def _update_progress(self):
        """进度更新线程"""
        while self._running:
            try:
                progress, status = self.queue.get(timeout=0.1)
                self.progress_var.set(progress)
                self.status_var.set(status)
                self.percent_label.config(text=f"{int(progress)}%")
                
                # 根据进度更新颜色
                if progress >= 100:
                    self.progress_bar.configure(style="Success.Horizontal.TProgressbar")
                elif progress >= 50:
                    self.progress_bar.configure(style="Running.Horizontal.TProgressbar")
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"进度更新错误: {e}")
                break
    
    def reset(self):
        """重置进度显示"""
        self.progress_var.set(0)
        self.status_var.set("就绪")
        self.percent_label.config(text="0%")
        self.progress_bar.configure(style="Custom.Horizontal.TProgressbar")
class ProgressManager:
    def update(self, progress: float, status: str):
        self.queue.put((progress, status))