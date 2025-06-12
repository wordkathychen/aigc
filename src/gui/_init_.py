"""
GUI 模块初始化文件
提供图形用户界面相关的组件
"""

# src/gui/_init_.py 中导出的类
from .app import MainApplication as ModernPaperGenerator
from .pages import BasePage

__all__ = ['ModernPaperGenerator', 'BasePage']

# src/gui/pages/__init__.py
class BasePage(ttk.Frame):
    def create_widgets(self):
        raise NotImplementedError