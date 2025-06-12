import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json

# 添加项目根目录到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.logger import setup_logger
from src.config.settings import APP_NAME, ADMIN_APP_NAME

# 导入管理后台页面
from src.admin.pages.dashboard import Dashboard
from src.admin.pages.prompt_manager import PromptManager
from src.admin.pages.user_manager import UserManager
from src.admin.pages.template_manager import TemplateManager
from src.admin.pages.api_settings import APISettings

logger = setup_logger(__name__)

class AdminApplication:
    """AI文本生成器管理后台主应用程序"""
    
    def __init__(self, root=None):
        """初始化管理后台应用程序
        
        Args:
            root: tkinter根窗口实例，如果为None则创建新窗口
        """
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
            
        self.root.title(f"{ADMIN_APP_NAME}")
        self.root.geometry("1280x800")
        
        # 在Windows上设置应用程序图标
        if sys.platform.startswith('win'):
            try:
                icon_path = self._get_resource_path("admin_icon.ico")
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
        self.show_page("dashboard")
        
        logger.info("管理后台初始化完成")
        
    def _get_resource_path(self, relative_path):
        """获取资源文件的绝对路径"""
        if getattr(sys, 'frozen', False):
            # 在PyInstaller打包环境中
            base_path = sys._MEIPASS
        else:
            # 在开发环境中
            base_path = os.path.abspath(".")
            
        return os.path.join(base_path, "resources", relative_path)
        
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
                 text=ADMIN_APP_NAME,
                 style='Title.TLabel').pack(side='left')
                 
        # 当前登录用户信息
        self.user_info_label = ttk.Label(
            header_frame,
            text="管理员",
            style='Subtitle.TLabel'
        )
        self.user_info_label.pack(side='right', padx=10)
        
        # 退出按钮
        ttk.Button(
            header_frame,
            text="退出登录",
            command=self.logout
        ).pack(side='right')
    
    def create_left_panel(self):
        """创建左侧面板"""
        self.left_frame = ttk.Frame(self.root, style='Dark.TFrame', width=200)
        self.left_frame.pack(side='left', fill='y', padx=10, pady=10)
        self.left_frame.pack_propagate(False)  # 防止frame缩小
        
        # 添加导航菜单
        self.menu_items = [
            ("数据概览", "dashboard"),
            ("提示词管理", "prompt"),
            ("会员管理", "user"),
            ("模板管理", "template"),
            ("API设置", "api")
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
        
        # 添加系统信息
        ttk.Separator(self.left_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # 显示系统信息
        system_frame = ttk.Frame(self.left_frame, style='Dark.TFrame')
        system_frame.pack(fill='x', pady=5)
        
        # 显示当前时间
        self.time_label = ttk.Label(
            system_frame, 
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            foreground="white",
            background="#2c3e50"
        )
        self.time_label.pack(pady=5)
        self.update_time()
        
        # 服务器状态
        self.server_status = ttk.Label(
            system_frame, 
            text="服务器状态: 在线",
            foreground="green",
            background="#2c3e50"
        )
        self.server_status.pack(pady=5)
    
    def update_time(self):
        """更新当前时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)  # 每秒更新一次
    
    def create_center_panel(self):
        """创建中央面板"""
        self.center_frame = ttk.Frame(self.root, style='TFrame')
        self.center_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
    
    def initialize_pages(self):
        """初始化所有页面"""
        # 数据概览页面
        self.pages["dashboard"] = Dashboard(self.center_frame, self)
        
        # 提示词管理页面
        self.pages["prompt"] = PromptManager(self.center_frame, self)
        
        # 会员管理页面
        self.pages["user"] = UserManager(self.center_frame, self)
        
        # 模板管理页面
        self.pages["template"] = TemplateManager(self.center_frame, self)
        
        # API设置页面
        self.pages["api"] = APISettings(self.center_frame, self)
        
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
    
    def logout(self):
        """退出登录"""
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            self.root.destroy()
            # 在这里可以添加返回登录界面的代码
    
    def run(self):
        """运行管理后台应用程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = AdminApplication()
    app.run() 