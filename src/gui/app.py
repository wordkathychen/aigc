import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Dict, List, Optional, Any, Callable

# 导入所有页面
from src.gui.pages.paper import PaperGenerator
from src.gui.pages.reduce_ai import ReduceAI
from src.gui.pages.reduce_dup import ReduceDuplication
from src.gui.pages.ppt import PPTMaker
from src.gui.pages.survey import SurveyGenerator
from src.gui.pages.format import FormatFixer
from src.utils.logger import setup_logger
from src.config.settings import APP_NAME, APP_VERSION

logger = setup_logger(__name__)

class MainApplication:
    """AI文本生成器主应用程序"""
    
    def __init__(self, root=None):
        """初始化主应用程序
        
        Args:
            root: tkinter根窗口实例，如果为None则创建新窗口
        """
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
            
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1200x800")
        
        # 在Windows上设置应用程序图标
        if sys.platform.startswith('win'):
            try:
                icon_path = self._get_resource_path("icon.ico")
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            except Exception as e:
                logger.error(f"加载图标失败: {str(e)}")
        
        # 配置样式
        self.configure_styles()
        
        # 创建主界面
        self.create_header()
        self.create_left_panel()
        self.create_center_panel()
        
        # 初始化页面
        self.pages = {}
        self.current_page = None
        self.initialize_pages()
        
        # 显示默认页面
        self.show_page("paper")
        
        logger.info("主应用程序初始化完成")
        
    def _get_resource_path(self, relative_path):
        """获取资源文件的绝对路径"""
        if getattr(sys, 'frozen', False):
            # 在PyInstaller打包环境中
            base_path = sys._MEIPASS
        else:
            # 在开发环境中
            base_path = os.path.abspath(".")
            
        return os.path.join(base_path, relative_path)
        
    def configure_styles(self):
        """配置应用程序样式"""
        # 获取ttk样式对象
        style = ttk.Style()
        
        # 配置基本样式
        style.configure("TFrame", background="#f5f5f5")
        style.configure("Dark.TFrame", background="#2c3e50")
        style.configure("TLabel", background="#f5f5f5", font=('SimHei', 10))
        style.configure("TButton", font=('SimHei', 10))
        style.configure("TEntry", font=('SimHei', 10))
        style.configure("TCombobox", font=('SimHei', 10))
        
        # 配置标题样式
        style.configure("Title.TLabel", 
                       font=('SimHei', 16, 'bold'), 
                       foreground="#2c3e50",
                       background="#f5f5f5")
        
        # 配置子标题样式
        style.configure("Subtitle.TLabel", 
                       font=('SimHei', 10), 
                       foreground="#7f8c8d",
                       background="#f5f5f5")
        
        # 配置导航按钮样式
        style.configure("Nav.TButton", 
                       font=('SimHei', 12),
                       padding=10)
        
        # 配置激活的导航按钮样式
        style.configure("Active.Nav.TButton", 
                       font=('SimHei', 12, 'bold'),
                       foreground="#3498db",
                       padding=10)
                       
    def create_header(self):
        """创建顶部标题区域"""
        header_frame = ttk.Frame(self.root, style='TFrame')
        header_frame.pack(fill='x', padx=20, pady=15)
        
        ttk.Label(header_frame, 
                 text=APP_NAME,
                 style='Title.TLabel').pack(side='left')
                 
        # 版本信息
        ttk.Label(header_frame,
                 text=f"v{APP_VERSION}",
                 style='Subtitle.TLabel').pack(side='right')
    
    def create_left_panel(self):
        """创建左侧面板"""
        self.left_frame = ttk.Frame(self.root, style='Dark.TFrame', width=200)
        self.left_frame.pack(side='left', fill='y', padx=10, pady=10)
        self.left_frame.pack_propagate(False)  # 防止frame缩小
        
        # 添加导航菜单
        self.menu_items = [
            ("论文生成", "paper"),
            ("AI检测降重", "reduce_ai"),
            ("查重降重", "reduce_dup"),
            ("PPT生成", "ppt"),
            ("问卷生成", "survey"),
            ("格式修改", "format")
        ]
        
        self.nav_buttons = {}
        for text, page_id in self.menu_items:
            btn = ttk.Button(
                self.left_frame,
                text=text,
                style="Nav.TButton",
                command=lambda p=page_id: self.show_page(p)
            )
            btn.pack(fill='x', pady=5)
            self.nav_buttons[page_id] = btn
        
        # 添加其他功能按钮
        ttk.Separator(self.left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Button(
            self.left_frame, 
            text="偏好设置",
            command=self.show_preferences
        ).pack(fill='x', pady=5)
        
        ttk.Button(
            self.left_frame, 
            text="使用帮助",
            command=self.show_help
        ).pack(fill='x', pady=5)
        
        ttk.Button(
            self.left_frame, 
            text="关于我们",
            command=self.show_about
        ).pack(fill='x', pady=5)
    
    def create_center_panel(self):
        """创建中央面板"""
        self.center_frame = ttk.Frame(self.root, style='TFrame')
        self.center_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
    
    def initialize_pages(self):
        """初始化所有页面"""
        # 论文生成页面
        self.pages["paper"] = PaperGenerator(self.center_frame, self)
        
        # AI检测降重页面
        self.pages["reduce_ai"] = ReduceAI(self.center_frame, self)
        
        # 查重降重页面
        self.pages["reduce_dup"] = ReduceDuplication(self.center_frame, self)
        
        # PPT生成页面
        self.pages["ppt"] = PPTMaker(self.center_frame, self)
        
        # 问卷生成页面
        self.pages["survey"] = SurveyGenerator(self.center_frame, self)
        
        # 格式修改页面
        self.pages["format"] = FormatFixer(self.center_frame, self)
        
        # 初始状态下隐藏所有页面
        for page in self.pages.values():
            page.pack_forget()
    
    def show_page(self, page_id: str):
        """显示指定页面
        
        Args:
            page_id: 页面ID
        """
        # 隐藏当前页面
        if self.current_page is not None:
            self.pages[self.current_page].pack_forget()
            
            # 恢复导航按钮样式
            if self.current_page in self.nav_buttons:
                self.nav_buttons[self.current_page].configure(style="Nav.TButton")
        
        # 显示新页面
        if page_id in self.pages:
            self.pages[page_id].pack(fill='both', expand=True)
            self.current_page = page_id
            
            # 设置导航按钮样式
            if page_id in self.nav_buttons:
                self.nav_buttons[page_id].configure(style="Active.Nav.TButton")
            
            logger.info(f"切换到页面: {page_id}")
        else:
            logger.error(f"未找到页面: {page_id}")
    
    def show_preferences(self):
        """显示偏好设置"""
        messagebox.showinfo("提示", "偏好设置功能尚未实现")
    
    def show_help(self):
        """显示使用帮助"""
        messagebox.showinfo("使用帮助", f"{APP_NAME} 使用指南\n\n"
                                    "1. 论文生成：选择论文类型、学科、字数等参数，生成论文大纲和正文\n"
                                    "2. AI检测降重：上传文本，优化文本以通过AI检测\n"
                                    "3. 查重降重：上传文本，降低重复率\n"
                                    "4. PPT生成：输入主题，生成完整PPT\n"
                                    "5. 问卷生成：制作问卷或生成问卷数据\n"
                                    "6. 格式修改：将文档格式调整为模板格式")
    
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo("关于我们", f"{APP_NAME} v{APP_VERSION}\n\n"
                                    "AI驱动的文本生成与处理工具\n\n"
                                    "© 2023-2024 All Rights Reserved")
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()