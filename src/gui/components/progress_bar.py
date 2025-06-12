import tkinter as tk
from tkinter import ttk
import time
import threading

class ProgressBar(ttk.Frame):
    """可控制的进度条组件"""
    
    def __init__(self, master=None, **kw):
        """初始化进度条
        
        参数:
            width: 进度条宽度（像素）
            mode: 'determinate' 或 'indeterminate'
        """
        width = kw.pop('width', 100)
        height = kw.pop('height', 20)
        mode = kw.pop('mode', 'indeterminate')
        
        ttk.Frame.__init__(self, master, **kw)
        
        self.progress = ttk.Progressbar(
            self, 
            orient="horizontal", 
            length=width,
            mode=mode
        )
        self.progress.pack(fill='both', expand=True)
        
        self._running = False
        self._timer = None
        self._value = 0
        self._max = 100
        
    def start(self, interval=50):
        """启动进度条"""
        if self._running:
            return
            
        self._running = True
        self.progress.start(interval)
        
    def stop(self):
        """停止进度条"""
        if not self._running:
            return
            
        self._running = False
        self.progress.stop()
        
    def step(self, amount=1.0):
        """增加进度"""
        self.progress.step(amount)
        
    def set_value(self, value):
        """设置具体进度值（适用于determinate模式）"""
        if not 0 <= value <= 100:
            raise ValueError("进度值必须在0-100之间")
            
        self._value = value
        self.progress['value'] = value
        
    def get_value(self):
        """获取当前进度值"""
        return self.progress['value']
        
    def reset(self):
        """重置进度条"""
        self.stop()
        self._value = 0
        self.progress['value'] = 0
    
    def set_determinate(self, is_determinate=True):
        """设置进度条模式"""
        if is_determinate:
            self.progress['mode'] = 'determinate'
        else:
            self.progress['mode'] = 'indeterminate' 