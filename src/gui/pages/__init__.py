import tkinter as tk
from tkinter import ttk

class BasePage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style='Dark.TFrame')
        self.create_widgets()
    
    def create_widgets(self):
        """子类需要实现此方法来创建页面内容"""
        raise NotImplementedError

# 导出所有页面类
from .paper import PaperGenerator
from .reduce_ai import ReduceAI
from .reduce_dup import ReduceDuplication
from .ppt import PPTMaker
from .survey import SurveyGenerator
from .format import FormatFixer
from .comment import CommentEditor

__all__ = [
    'PaperGenerator',
    'ReduceAI',
    'ReduceDuplication',
    'PPTMaker',
    'SurveyGenerator',
    'FormatFixer',
    'CommentEditor'
]