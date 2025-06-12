import tkinter as tk
from tkinter import ttk, messagebox
import threading
from src.utils.database import Database
from src.utils.exceptions import DatabaseError, ValidationError
from src.utils.validators import InputValidator
from src.gui.app import MainApplication
from src.config.settings import THEME_COLORS, WINDOW_SIZE
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("论文助手 - 登录")
        self.root.geometry("400x500")
        self.root.configure(bg=THEME_COLORS['background'])
        
        # 初始化数据库
        self.db = Database()
        
        # 创建样式
        self.create_styles()
        self.create_widgets()
    
    def create_styles(self):
        style = ttk.Style()
        style.configure('Login.TFrame', background=THEME_COLORS['card'])
        style.configure('Login.TLabel',
                       font=('微软雅黑', 12),
                       foreground=THEME_COLORS['text'],
                       background=THEME_COLORS['card'])
        style.configure('Login.TButton',
                       font=('微软雅黑', 10),
                       background=THEME_COLORS['button'])
    
    def create_widgets(self):
        # 主框架
        self.main_frame = ttk.Frame(self.root, style='Login.TFrame')
        self.main_frame.pack(padx=40, pady=40, fill='both', expand=True)
        
        # Logo或标题
        ttk.Label(
            self.main_frame,
            text="论文助手",
            font=('微软雅黑', 24, 'bold'),
            foreground=THEME_COLORS['primary'],
            background=THEME_COLORS['card']
        ).pack(pady=30)
        
        # 用户名输入
        ttk.Label(
            self.main_frame,
            text="用户名",
            style='Login.TLabel'
        ).pack(pady=(20, 5))
        
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(
            self.main_frame,
            textvariable=self.username_var,
            width=30
        )
        self.username_entry.pack(pady=(0, 20))
        
        # 密码输入
        ttk.Label(
            self.main_frame,
            text="密码",
            style='Login.TLabel'
        ).pack(pady=(20, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            self.main_frame,
            textvariable=self.password_var,
            show="*",
            width=30
        )
        self.password_entry.pack(pady=(0, 30))
        
        # 登录按钮
        self.login_button = ttk.Button(
            self.main_frame,
            text="登录",
            command=self.login,
            style='Login.TButton'
        )
        self.login_button.pack(pady=20)
        
        # 注册链接
        register_frame = ttk.Frame(self.main_frame, style='Login.TFrame')
        register_frame.pack(pady=20)
        
        ttk.Label(
            register_frame,
            text="没有账号？",
            style='Login.TLabel'
        ).pack(side='left')
        
        register_label = ttk.Label(
            register_frame,
            text="立即注册",
            foreground=THEME_COLORS['primary'],
            background=THEME_COLORS['card'],
            cursor='hand2'
        )
        register_label.pack(side='left', padx=5)
        register_label.bind('<Button-1>', lambda e: self.show_register())
    
    def login(self):
        """处理登录逻辑"""
        try:
            username = self.username_var.get().strip()
            password = self.password_var.get()
            
            # 验证输入
            if not username or not password:
                raise ValidationError("用户名和密码不能为空")
            
            # 验证用户身份
            if self.verify_credentials(username, password):
                self.root.withdraw()  # 隐藏登录窗口
                self.open_main_window()
            else:
                messagebox.showerror("错误", "用户名或密码错误")
                
        except ValidationError as e:
            messagebox.showerror("输入错误", str(e))
        except DatabaseError as e:
            messagebox.showerror("数据库错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")
    
    def verify_credentials(self, username, password):
        try:
            success, user_data = self.db.verify_user(username, password)
            if success:
                return True
            return False
        except DatabaseError as e:
            logger.error(f"验证失败: {e}")
            return False
    
    def show_register(self):
        # 创建注册窗口
        register_window = tk.Toplevel(self.root)
        register_window.title("注册新用户")
        register_window.geometry("300x400")
        register_window.configure(bg='#0a192f')
        # ... 实现注册界面
    
    def open_main_window(self):
        main_window = tk.Toplevel(self.root)
        app = MainApplication(main_window)