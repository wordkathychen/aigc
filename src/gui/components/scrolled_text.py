import tkinter as tk
from tkinter import ttk

class ScrolledText(tk.Text):
    """带滚动条的文本框"""
    
    def __init__(self, master=None, **kw):
        self.frame = ttk.Frame(master)
        self.vbar = ttk.Scrollbar(self.frame)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 水平滚动条（默认不显示）
        self.hbar = ttk.Scrollbar(self.frame, orient='horizontal')
        if kw.get('wrap') == 'none':
            self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 确保这些关键字参数存在
        kw.update({
            'wrap': kw.get('wrap', 'word'),
            'yscrollcommand': self.vbar.set,
            'xscrollcommand': self.hbar.set
        })
        
        tk.Text.__init__(self, self.frame, **kw)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vbar['command'] = self.yview
        self.hbar['command'] = self.xview
        
        # 复制Text的方法到自己
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))
    
    def __str__(self):
        return str(self.frame) 