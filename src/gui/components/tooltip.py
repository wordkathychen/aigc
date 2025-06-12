import tkinter as tk

class ToolTip:
    """为组件创建工具提示"""
    
    def __init__(self, widget, text=None, delay=500, wrap_length=200):
        """初始化工具提示
        
        参数:
            widget: 要添加工具提示的组件
            text: 工具提示文本
            delay: 显示延迟（毫秒）
            wrap_length: 文本自动换行长度
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wrap_length = wrap_length
        self.tooltip_window = None
        self.id = None
        
        # 绑定事件
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        
    def enter(self, event=None):
        """鼠标进入组件时的处理"""
        self.schedule()
        
    def leave(self, event=None):
        """鼠标离开组件时的处理"""
        self.unschedule()
        self.hide()
        
    def schedule(self):
        """调度工具提示显示"""
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)
        
    def unschedule(self):
        """取消工具提示显示调度"""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
            
    def show(self):
        """显示工具提示"""
        if not self.text:
            return
            
        # 获取组件的位置
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # 创建工具提示窗口
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # 无边框窗口
        
        # 设置窗口在所有其他窗口之上
        tw.wm_attributes("-topmost", True)
        
        # 在一些平台上可能需要这个
        # tw.wm_attributes("-type", "tooltip")
        
        # 创建标签
        label = tk.Label(
            tw, 
            text=self.text, 
            justify='left',
            background="#ffffe0", 
            relief='solid', 
            borderwidth=1,
            wraplength=self.wrap_length
        )
        label.pack(padx=2, pady=2)
        
        # 定位窗口
        tw.wm_geometry(f"+{x}+{y}")
        
    def hide(self):
        """隐藏工具提示"""
        tw = self.tooltip_window
        if tw:
            tw.destroy()
            self.tooltip_window = None
            
    def update_text(self, text):
        """更新工具提示文本"""
        self.text = text
        if self.tooltip_window:
            self.hide()
            self.show() 